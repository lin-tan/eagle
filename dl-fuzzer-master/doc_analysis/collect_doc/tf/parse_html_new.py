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
import pandas as pd



def prettyprint(info):
	pp = pprint.PrettyPrinter(indent=2)
	pp.pprint(info)




class web_parser():
	def __init__(self, source_path, soup, url, aliases, target_module=None):
		self.source_path = source_path
		self.soup = soup
		self.url = url
		self.yaml_data = None
		self.aliases = aliases
		self.warning = False # warning class api
		self.target_module = target_module

		self.sect_title = {
			'inputs':['Args', 'Arguments'],
			'outputs': ['Returns', 'Yields'],
			'exceptions': ['Raises']
			 }


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


	def get_code_signature(self ):
		
		def _multiple_signature(wo_newline):
			# HARD CODE: take the longest
			all_sig = re.findall(r'{}\(.*?\)'.format(self.title), wo_newline)
			signature = max(all_sig, key=len)
			pat = r'(.*?)\((.*?)\)'
			ret = re.match(pat, signature)
			return ret.group(1), ret.group(2)
			

		# get the code signature
		cls = ['devsite-click-to-copy prettyprint lang-py tfo-signature-link', 'prettyprint lang-python']
		code = self.body.find_all(class_= cls)
		if len(code) == 0:
			running_stat['no_signature'].append(self.url)
			raise GoToTheNextOne(self.url , self.title, 'signature not found', save=False)
			
			
		code = code[0]
		pat = r'<pre class=.*?><code.*?>(.*?)\((.*?)\)<\/code><\/pre>'
		
		wo_newline = re.sub(r'\n', '', str(code))   # without new line

		# check multiple signature:
		if len(re.findall(r'{}\(.*?\)'.format(self.title), wo_newline))>1:
			print("Warning: more than one signature found in, take the longest one: {}".format(self.url))
			return _multiple_signature(wo_newline)
			#raise GoToTheNextOne(self.url , self.title, 'More than one signature found', save=True)
		
		parsed = re.match(pat, wo_newline)
		
		if not parsed:
			raise GoToTheNextOne(self.url , self.title, 'signature parsing failure', save=True)
			
		parsed_title = parsed.group(1)
		sig = parsed.group(2)
		sig = re.sub(r'^[ \t]+', '', sig)


		return parsed_title, sig

	def get_section(self):
		# get arg/returns/exception section, return string
		# sect can be a list of strings
		
		ret = {}
		try:
			tables = pd.read_html(self.source_path)
		except:
			running_stat['no_tab'].append(self.url)
			running_stat['no_arg'].append(self.url)
			raise GoToTheNextOne(self.url , self.title, 'Failed to get any table', save=False)

		# init ret
		for sect in self.sect_title:
			ret[sect] = []

		class_attr = ['Attributes']
		for tab in tables:
			tab_title = tab.columns[0]
			if self.target_module==None and tab_title in class_attr:
				running_stat['class_api'].append(self.url)
				raise GoToTheNextOne(self.url , self.title, ' class API (Attributes section)', save=False)

			for sect in self.sect_title:
				if tab_title in self.sect_title[sect]:
					ret[sect].append(tab)
					break

		return ret


	def parse_sect(self):
		if self.target_module==None and re.search(r'<p>Inherits From:', str(self.body))!=None:
			running_stat['class_api'].append(self.url)
			raise GoToTheNextOne(self.url , self.title, ' class API (inherits from)', save=False)
		
		all_tab = self.get_section()
		for sect in self.sect_title:
			tables = all_tab[sect]

			
			if not tables:
				if sect == 'inputs':
					# no argument section found
					running_stat['no_arg'].append(self.url)
					raise GoToTheNextOne(self.url , self.title, 'no argument section dectected', save=False)
				else:
					continue

			if len(tables) > 1:
				print("Warning: more than one [%s] found in, take the first one: %s" % (sect, self.url))
			

			target_tab = tables[0]

			for index, row in target_tab.iterrows():
				if sect == 'inputs':
					self.yaml_data.update_constraint(row[0], row[1])
				else:
					if row[0] == row[1]:
						self.yaml_data.update_out_excep(sect, None, row[1])
					else:
						# itemize
						self.yaml_data.update_out_excep(sect, row[0], row[1])

	def run(self):

		replace_dict = {
			'&gt;':'>', 
			'&lt;':'<', 
			r'<(code|/code).*?>': '`', 
			r'</*tf\.variable.*?>': '', 
			r'</*a.*?>': '', 
			r'</*em>': '', 
			'&amp;': '&'
			}

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
			# likely to be a class API
			self.warning = True
			#print('WARNING class api: '+ str(self.url))
			#raise GoToTheNextOne(self.url , self.title, 'WARNING class api', save=True)

		if sig and not sig.isspace():
			sig_str, _ = sig_pre_process(sig, replace_dict)
			parsed_input = parse_input(sig_str)
		else:
			parsed_input = []

		self.yaml_data = yaml_file(self.title, self.api_name, self.url, self.aliases)
		self.yaml_data.init_input(parsed_input, deprecated_arg_list)

		# get input description:
		self.parse_sect()

		
		
		


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


	web_file_folder = '/Users/danning/Desktop/deepflaw/web_source/tf_2.3_source/'
	save_folder = './tf2.3_layer/' 

	uniqueurl_filename = read_yaml('./stat2.3/tf2.3_py_uniqueurl_filename.yaml')
	target_module = {'tf.nn.':0, 'tf.keras.layers.':0}
	version = '2.3'
	running_stat_save = './stat2.3/running_stat_layer'

	global running_stat
	running_stat = {
		'class_api': [], 
		'deprecated': [], 
		'module': [],
		'warning':[], 
		'no_arg':[], 		# no argument or no "Argument" section detected
		'no_tab':[],		# fail to parse table
		'collected': [], 
		'no_signature': [],	# no signatures
		'word_cnt':{},
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
		if '/versions/r2.' not in url:
			url = url.replace('www.tensorflow.org/', 'www.tensorflow.org/versions/r%s/'%version)
		
		#print('curr url: '+ url)
		tmp, target_module = _is_target(url, target_module)
		if not tmp:
			continue

		filename = uniqueurl_filename[url]['filename']
		
		source_path = web_file_folder+filename
		soup = read_soup(source_path)

		aliases = uniqueurl_filename[url]['aliases']
		parse_obj = web_parser(source_path, soup, url, aliases, target_module=target_module)

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
		with open(running_stat_save, 'w') as yaml_file:
			yaml.dump(running_stat, yaml_file)

	# with open('./stat/camel_case_warning_list.yaml', 'w') as yaml_file:
	# 	yaml.dump(warning_list, yaml_file)



if __name__ == "__main__":
	# works for tf 2.2 2.3
	start = time.time()

	try:
		test_url = sys.argv[1]
	except:
		test_url = None

	
	main(test_url)

	end = time.time()
	# print(end - start)
		

   
