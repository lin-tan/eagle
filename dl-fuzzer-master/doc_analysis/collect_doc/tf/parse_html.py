import sys
sys.path.insert(0,'..')

from bs4 import BeautifulSoup
import yaml
import re
from parse_utils import *
from yaml_file_cls import yaml_file
import pprint
import traceback
import time



def prettyprint(info):
	pp = pprint.PrettyPrinter(indent=2)
	pp.pprint(info)




class web_parser():
	def __init__(self, soup, url, aliases, target_module=None):
		self.soup = soup
		self.url = url
		self.yaml_data = None
		self.aliases = aliases
		self.warning = False # warning class api
		self.target_module = target_module

		self.sect_title = {'inputs':
			  {'title': ['Args', 'Arguments'],
			  'item': True,
			  'replace_sym': True},
			 'outputs': 
			  {'title': ['Returns', 'Yields'],
			  'item': False,
			  'replace_sym': True},
			 'exceptions': 
			  {'title': ['Raises'],
			  'item': False,
			  'replace_sym': True}}






	def init(self):

		try:
			self.title = str(self.soup.find_all(class_ = 'devsite-page-title')[0].contents[0])
			self.api_name = self.title.split('.')[-1]
			self.body = self.soup.find_all(class_='devsite-article-body')[0]
			self.word_cnt = self.cnt_word()

		except GoToTheNextOne as gttno:
			raise GoToTheNextOne(self.url , self.title, 'Error when init', save=True)


		if self.title.startswith('Module: '):
			running_stat['module'].append(self.url)
			raise GoToTheNextOne(self.url , self.title, 'Module', save=False)

		if self.target_module!=None:
			flag = False
			for tm in self.target_module:
				if self.title.lower().startswith(tm):
					flag=True
					break
			if not flag:
				raise GoToTheNextOne(self.url , self.title, 'not target module', save=False)

			
	def cnt_word(self):
		return cnt_num_word(self.body.get_text())+cnt_num_word(self.title)
		


	def detect_deprecated(self):

		deprecated_list = []
		for wrn in self.body.find_all(class_='warning'):
			wrn_cnt = re.search(r'<span>(((.*)\n*)+)</span>', str(wrn)).group(1)
			if 'THIS FUNCTION IS DEPRECATED' in wrn_cnt:
				return True, None

			elif 'SOME ARGUMENTS ARE DEPRECATED' in wrn_cnt:
				d_arg = re.search(r'<code.*>\((.*)\)</code>', wrn_cnt).group(1)
				d_arg_parsed = re.split(r',\s', d_arg)
				if d_arg:
					for dap in d_arg_parsed:
						deprecated_list.append(dap)
					
		return False, deprecated_list


	def detect_class_api(self):
		for i,bc in enumerate(self.body.contents):
			if bc.name in ['h1', 'h2', 'h3', 'h4']:
				if bc.contents[0] in ['Methods', 'Child Classes', 'Class Variables']:
					return True
				
		return False


	def get_code_signature(self, cls = 'prettyprint lang-python'):
		
		def _multiple_signature(wo_newline):
			# HARD CODE: take the longest
			all_sig = re.findall(r'{}\(.*?\)'.format(self.title), wo_newline)
			signature = max(all_sig, key=len)
			pat = '(.*?)\((.*?)\)'
			ret = re.match(r'{}'.format(pat), signature)
			return ret.group(1), ret.group(2)
			

		# get the code signature
		code = self.body.find_all(class_= cls)
		if len(code) == 0:
			running_stat['no_signature'].append(self.url)
			raise GoToTheNextOne(self.url , self.title, 'signature not found', save=False)
			
			
		code = code[0].contents[0]
		pat = '<code(.*?)>(.*?)\((.*?)\)</code>'
		
		wo_newline = re.sub(r'\n', '', str(code))   # without new line

		# check multiple signature:
		if len(re.findall(r'{}\(.*?\)'.format(self.title), wo_newline))>1:
			print("Warning: more than one signature found in, take the longest one: {}".format(self.url))
			return _multiple_signature(wo_newline)
			#raise GoToTheNextOne(self.url , self.title, 'More than one signature found', save=True)
		
		parsed = re.match(r'{}'.format(pat), wo_newline)
		
		if not parsed:
			raise GoToTheNextOne(self.url , self.title, 'signature parsing failure', save=True)
			
		parsed_title = parsed.group(2)
		sig = parsed.group(3)
		sig = re.sub(r'^[ \t]+', '', sig)


		return parsed_title, sig

					
	def convert2str(self):
				
		convert_str = ''
		for bc in self.body.contents:
			if bc!='\n':
				convert_str+=str(bc)
				
		convert_str = re.sub('(?<!>)\n(?!<)','<NL>',convert_str)
		convert_str = re.sub('\n','',convert_str)
		return convert_str

	def get_section(self,  convert_str, sect, replace_dict = {}, item=True, replace_sym=True):
		# get arg/returns/exception section, return string
		# sect can be a list of strings
		
		# item=True: only allow item <ul>.*?(<li>.*</li>)+.*</ul>  (for args)
		# item=False (for exceptions and returns): allow both <ul>.*?(<li>.*</li>)+.*</ul> and <p></p>
		
		def _special_parse(cs):
			#pat = '<pre class.*>(.*)</code></pre>'
			parsed_str = re.search(r'<h1.*?>(\b%s\b).*?</h1><pre class.*?>(.*?)</pre>'% r'\b|\b'.join(map(re.escape, sect)),cs)
			ret = parsed_str.group(2)
			if ':' in ret:
				return ret, True, True
			else:
				return ret, False, True


		
		if replace_sym:
			convert_str = replace_symbol(convert_str, replace_dict)

		if self.target_module==None and re.search(r'<p>Inherits From:', convert_str)!=None:
			running_stat['class_api'].append(self.url)
			raise GoToTheNextOne(self.url , self.title, ' class API (inherits from)', save=False)

		if_item = False  # True if the returned string is item (need to be further parsed), False otherwise
		
		findall = re.findall(r'<h4.*?>(\b%s\b):</h4>'% r'\b|\b'.join(map(re.escape, sect)),convert_str)

		if findall!=None and len(findall)>1:
			# HARD CODE
			if sect==self.sect_title['inputs']:
				raise GoToTheNextOne(self.url , self.title, str(sect)+' more than one found', save=True)
			else:
				print("Warning: more than one {} section found, take the first one: {}".format(str(sect), self.url))
				pass

		
		if re.search(r'<h1.*?>(\b%s\b).*?</h1>'% r'\b|\b'.join(map(re.escape, sect)),convert_str)!=None:
			return _special_parse(convert_str)
			# print(convert_str)
			# raise GoToTheNextOne(self.url , self.title, str(sect)+' need special parse ', save=True)

		# try item pattern 
		parsed = re.search(r'<h4.*?>(\b%s\b):</h4><ul>.*?((<li>(<p>)?<b>`*.*?`*</b>.*?</li>)+)</ul>(?!<blockquote>)'% r'\b|\b'.join(map(re.escape, sect)), convert_str)
		if parsed == None:
			if item:
				return None, False, False   # not found 
			if not item:
				# try non-item patter
				parsed = re.search(r'<h4.*?>(\b%s\b):</h4><p>(.*?)</p>'% r'\b|\b'.join(map(re.escape, sect)), convert_str)
				if parsed == None:
					return None, False, False   # not found 
				else:
					ret = parsed.group(2)
					if_item=False
		else:
			ret = parsed.group(2)
			if_item=True
			
		
		return ret, if_item, False

	def parse_sect(self, replace_dict):


		def _special_parse(sect_str, varname = ''):
			# e.g. https://www.tensorflow.org/versions/r2.1/api_docs/python/tf/keras/preprocessing/image/apply_affine_transform
			special_pat = '({}):(((?!<NL>\w+:).)*)'.format(varnmae if varname else '\w+')
			s_arg_idx = 0
			s_descp_idx = 1
			return re.findall(r'{}'.format(special_pat), sect_str), s_arg_idx, s_descp_idx

		def _normal_parse(sect_str, varname=''):
			varname = varname.replace('*', '\*')
			item_pat = r'<li>(<p>)?<b>`*({})`*</b>:\s+(.*?)</li>'.format(varname if varname else '.*?')
			n_arg_idx = 1
			n_descp_idx = 2
			return re.findall(item_pat, sect_str), n_arg_idx, n_descp_idx
		
		def _parse_item(sect_str, sect):
			# so far the item is only in argument section, and only one argument has item
			# print(sect_str)
			# if sect!='inputs':
			# 	raise GoToTheNextOne(self.url , self.title, 'item in {} section'.format(str(self.sect_title[sect]['title'])), save=True)
			
			place_holder = '<ITEM_PART>'
			item_part = re.search(r'<[ou]l>((<li>.*?</li>)+)(</[ou]l>)?', sect_str).group(1)
			ret = re.sub(r'<[ou]l>((<li>.*?</li>)+)(</[ou]l>)?', place_holder, sect_str, count=1)
			item_part = re.sub(r'</*li>', '', item_part)
			ret = re.sub(place_holder, ' '+item_part+' ', ret)
			if not ret.endswith('</li>'):
				ret+='</li>'
			return ret

		def _if_itemize(src):
			pat = '<[ou]l>(<li>.*?</li>)+(</[ou]l>)?'
			if re.search(r'{}'.format(pat), src)!=None:
				return True
			return False

		def _get_parse_result(sect_str, special, varname=''):
			if special:
				return _special_parse(sect_str, varname)
			else: 
				return  _normal_parse(sect_str, varname)

		def _set_input_constraint(parsed_descp, arg_idx, descp_idx, post_replace):
			for li in parsed_descp:
				self.yaml_data.update_constraint(li[arg_idx], li[descp_idx], post_replace)


		
		
		post_replace = {'<NL>': ' ', '</*p>':'', '</*a.*?>': '', '</*pre.*?>': ''}
		convert_str = self.convert2str()
		

		if_attribute, _, _ = self.get_section(convert_str, ['Attributes'], replace_dict=replace_dict, item=True, replace_sym=True)
		if self.target_module==None and if_attribute!=None:
			running_stat['class_api'].append(self.url)
			raise GoToTheNextOne(self.url , self.title, 'class api', save=False)
		if if_attribute!=None:
			print("Warning: Attribute section detected, will ignore : {}".format(self.url))

		
		# if re.search(r'<[ou]l>(<li>.*?</li>)+(</[ou]l>)?', convert_str)!=None:
		# 	convert_str = _parse_item(convert_str,sect = None)

		for sect in self.sect_title:
			sect_str, if_item, special = self.get_section(convert_str, self.sect_title[sect]['title'], replace_dict=replace_dict, item=self.sect_title[sect]['item'], replace_sym = self.sect_title[sect]['replace_sym'])
			# no argument section found
			if sect == 'inputs' and sect_str==None:
				running_stat['no_arg'].append(self.url)
				raise GoToTheNextOne(self.url , self.title, 'no argument section', save=False)


			if sect_str!=None:
				# check item, e.g. https://www.tensorflow.org/versions/r2.1/api_docs/python/tf/batch_to_space
				if _if_itemize(sect_str):
					sect_str = _parse_item(sect_str, sect)

				
				# update config file
				if if_item:
					parsed_descp, arg_idx, descp_idx = _get_parse_result(sect_str, special)

				

				if sect == 'inputs':
				
					_set_input_constraint(parsed_descp, arg_idx, descp_idx, post_replace)
					empty_arg = self.yaml_data.get_empty_arg()
					
					for ea in empty_arg:
						# use convert_str
						parsed_descp, arg_idx, descp_idx = _get_parse_result(replace_symbol(convert_str, replace_dict), special, varname=ea)
						_set_input_constraint(parsed_descp, arg_idx, descp_idx, post_replace)


				else:
					if not if_item:
						self.yaml_data.update_out_excep(sect, None, sect_str, post_replace)
						continue
					
					for li in parsed_descp:
						self.yaml_data.update_out_excep(sect, li[arg_idx], li[descp_idx], post_replace)




	def run(self):

		replace_dict = {'&gt;':'>', '&lt;':'<', r'<(code|/code).*?>': '`', r'</*tf\.variable.*?>': '', r'</*a.*?>': '', r'</*em>': '', '&amp;': '&'}

		# check deprecated  & get deprecated arg list
		func_deprecated, deprecated_arg_list = self.detect_deprecated()

		if func_deprecated:
			running_stat['deprecated'].append(self.url)
			raise GoToTheNextOne(self.url , self.title, 'deprecated', save=False)

		if self.target_module==None and self.detect_class_api():		# detect if the API is a class API
			running_stat['class_api'].append(self.url)
			raise GoToTheNextOne(self.url , self.title, 'class api', save=False)

		


		parsed_title, sig = self.get_code_signature()		# get input information
		

		if not (parsed_title==self.title or (parsed_title[0]=='@' and parsed_title.endswith(self.title)) ):
			raise GoToTheNextOne(self.url , self.title, 'signature title incorrect', save=True)
		
		if is_camel_case(self.title):
			self.warning = True
			#print('WARNING class api: '+ str(self.url))
			#raise GoToTheNextOne(self.url , self.title, 'WARNING class api', save=True)

		if sig and not sig.isspace():
			sig_str, _ = sig_pre_process(signature, replace_dict)
			parsed_input = parse_input(sig_str)
		else:
			parsed_input = []

		self.yaml_data = yaml_file(self.title, self.api_name, self.url, self.aliases)
		self.yaml_data.init_input(parsed_input, deprecated_arg_list)

		# get input description:
		self.parse_sect(replace_dict)

		
		
		


def main(test_url=None):
	def _is_target(url, target_module=None):
		if target_module!=None:
			for tm in target_module:
				if tm.replace('.', '/') in url:
					target_module[tm]+=1
					return True, target_module
		else:
			return True, target_module

		return False, target_module


	web_file_folder = '/Users/danning/Desktop/deepflaw/web_source/doc2.1source/'
	save_folder = './tfdoc2.1_layer/' 

	uniqueurl_filename = read_yaml('./stat/tf2.1_py_uniqueurl_filename.yaml')
	target_module = {'tf.nn.':0, 'tf.keras.layers.':0}

	global running_stat
	running_stat = {
		'class_api': [], 
		'deprecated': [], 
		'module': [],
		'warning':[], 
		'no_arg':[], 
		'collected': [], 
		'no_signature': [],
		'word_cnt':{}
		}

	warning_list = []
	warning_arg_list = []
	collect_cnt = 0
	
	if test_url!=None:
		if test_url in uniqueurl_filename:
			candidate = [test_url]
		else:
			print('invalid test url')
			return

	else:		
		candidate = list(uniqueurl_filename.keys())

	if not test_url: 		#delete all files
		del_file(save_folder)

	for url in candidate:
		tmp, target_module = _is_target(url, target_module)
		if not tmp:
			continue

		filename = uniqueurl_filename[url]['filename']
		
		soup = read_soup(web_file_folder+filename)

		aliases = uniqueurl_filename[url]['aliases']
		parse_obj = web_parser(soup, url, aliases, target_module=target_module)

		try:
			parse_obj.init()
			running_stat['word_cnt'][url] = parse_obj.word_cnt

			parse_obj.run()
			parse_obj.yaml_data.save_file(save_folder, filename.replace('.html', ''))

			running_stat['collected'].append(url)
			if test_url!=None:
				prettyprint(parse_obj.yaml_data.data)

		
		except GoToTheNextOne as gttno:
			if gttno.save:
				print(gttno.msg+': '+gttno.link)
				
			continue
		except:
			print('OTHER BUG '+str(url))
			traceback.print_exc()
			continue
		


		if parse_obj.warning:
			warning_list.append(url)

	running_stat['warning'] = warning_list
	
	if not test_url:
		with open('./stat/running_stat', 'w') as yaml_file:
			yaml.dump(running_stat, yaml_file)
	print(target_module)

	# with open('./stat/camel_case_warning_list.yaml', 'w') as yaml_file:
	# 	yaml.dump(warning_list, yaml_file)



if __name__ == "__main__":
    # works for tf 2.1
	start = time.time()

	try:
		test_url = sys.argv[1]
	except:
		test_url = None

	
	main(test_url)

	end = time.time()
	# print(end - start)
		

   