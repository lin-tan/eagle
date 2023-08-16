
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

class func_parser():
    def __init__(self, func_src):
        self.func_src = func_src
        self.url = None
        self.title = self.get_title()
        self.api_name = None
        self.yaml_data = None
    

    def get_sig(self):
        sig_pat = r'<span class=\"sig-paren\">\(</span>(.*?)<span class=\"sig-paren\">\)</span>'
        parsed = re.search(sig_pat, str(self.func_src))
        if parsed:
            sig = parsed.group(1)
            sig = re.split('\) -&gt;', sig, 1)[0]
            return sig
        else:
            raise GoToTheNextOne(self.url , self.title, 'signature parsing failed', save=True)
        
    def get_ret_type(self):
        replace_dict = {
            r'</*(em|span).*?>':'',
        }

        sig_sect = self.func_src('dt')[0]

        # try to find -&gt;
        sig_pat = r'(-&gt;|→)(.*?)<(a|code|/dt).*?>'
        parsed = re.search(sig_pat, str(sig_sect))
        ret = ''
        if parsed:
            sig = parsed.group(2)

            ret = replace_symbol(sig, replace_dict)
        

        return pre_descp(ret)


    def detect_deprecated(self):
        warning_sect = self.func_src.find_all(class_='admonition warning')
        if warning_sect:
            if re.search('this function is deprecated', str(warning_sect).lower()):
                return True
        
        # try search "^Deprecated" outside warning section
        # https://pytorch.org/docs/stable/cuda.html#torch.cuda.memory_cached
        if re.search('<dd><p>Deprecated', str(self.func_src)):
            return True

        return False

    def get_title(self):
        sig_sect = self.func_src('dt')[0]

        pat = r'<code class=\"sig-.*?\">(.*?)</code>'
        title = re.findall(pat, str(sig_sect))
        ret = ''
        for t in title:
            ret +=t
        return ret



    def init(self, url):
        # get title, api_name, signature, and init yaml_data
        replace_dict = {
            r'</*(a|em|span).*?>': '', 
            r'</*code.*?>': '`',
            '&lt;': '<', 
            '&gt;': '>'
            }


        self.url = url
        # self.title = self.get_title()
        self.api_name = self.title.split('.')[-1]


        # detect_deprecated
        if self.detect_deprecated():
            running_stat['deprecated'].append(self.url)
            raise GoToTheNextOne(self.url , None, 'deprecated', save=False)

        
        # get signature
        signature = self.get_sig()
        if not signature or signature.isspace() :
            running_stat['no_input'].append({self.title: self.url})
            raise GoToTheNextOne(self.url , self.title, 'no input or no siganture parsed', save=False)
        
        # init yaml data
        self.yaml_data = yaml_file(self.title, self.api_name, self.url, package = 'torch', version = '1.4.0') #'1.5.0a0+4ff3872'

        # parse input variable
        sig_str, sig_dtype_map = sig_pre_process(signature, replace_dict, extract_bracket=True)
        parsed_input, keywordonly_args = parse_input(sig_str, detect_keywordonly=True)
        self.yaml_data.init_input(parsed_input, deprecated_list=[], keyword_only=keywordonly_args, sig_dtype=sig_dtype_map)
        #prettyprint(self.yaml_data.data)

    def get_param_sect(self):
        func_str= re.sub('\n', ' ', str(self.func_src))
        descp_pat = r'<dt class=.*?>(Parameters|Keyword Arguments|Arguments)<\/dt>\s*<dd class=.*?>(.*?)<\/dd>'
        descp_sect = re.findall(descp_pat, func_str)
        if not descp_sect:
            running_stat['no_arg_sect'].append({self.title: self.url})
            raise GoToTheNextOne(self.url , self.title, 'No parameter section detected', save=False)

        #return descp_sect.group(2)
        return [x[1] for x in descp_sect]
    


    
    def parse_param_sect(self, param_str):
        
        def _parse_dtype_descp(dtype_descp):
            if '(' in dtype_descp:
                sep = ['\.\.\.', r',\s*optional', '`']
                ret = split_str(dtype_descp, sep, boundary=False, escape=False)
                running_stat['warning'].append('Warning: [{}] Dtype format issue {}->{} : {} '.format(self.title, dtype_descp, str(ret), self.url))
                return ret


            sep = [',\s*', r'\b\s*or\s*\b', '\.\.\.', 'optional', '`']

            return split_str(dtype_descp, sep, boundary=False, escape=False)
        
        def _unicode2str(s):
            # return unicodedata.normalize('NFKD', s).encode('ascii','ignore')
            byte_str = s.encode('ascii', 'backslashreplace')
            return byte_str.decode(encoding='UTF-8')

        def _inconsistency_handle(arg):
            # hardcode for https://pytorch.org/docs/stable/torch.html#torch.lobpcg
            ret = []
            for x in re.split(r',\s', arg):
                if self.yaml_data.is_input(x,ignore_star =True):
                    ret.append(x)
            return ret

        param_pat= r'<p><strong>(.*?)</strong>(\s*\((.*?)\)\s*)? – (.*?)</p>'
        replace_dict = {
            r'<\/*(a|em|span).*?>': '', 
            r'</*code.*?>': '`',
            '&lt;': '<', 
            '&gt;': '>',
            r'<mrow>.*?</mrow>': '',
            r'<\/*(math|semantics|mi|mo|mtext|cite).*?>': ''
            }
            
        post_replace ={
            r'<\/*strong.*?>': '',
            r'left\[': r'\[',
            r'right\]': r'\]',
            r'\\text{(.*?)}':r'\1', 
            r'\\u201[cd]':'\"',
            r'\\u201[89]':'\'',
            r'\\u03B[\w]': '',
            '\\\\': ' ', 
            r'\\xd7': '*',
            r'\bgeq\b': '>=',
            r'\bleq\b': '<=',
            r'frac{(.*?)}{(.*?)}': r'\1/\2'
            #r'\btimes\b': '*'
        }

        
        param_str = replace_symbol(param_str, replace_dict)
        

        
        parsed_param = re.findall(param_pat, param_str)
        for pp in parsed_param:
            parsed_varname = pp[0]
            parsed_dtype = pp[2]
            parsed_descp = pp[3]

            descp_str = _unicode2str(parsed_descp)
            descp_str = replace_symbol(descp_str, post_replace)

            final_dtype = parsed_dtype.strip('()') # _parse_dtype_descp(parsed_dtype)

            if not self.yaml_data.is_input(parsed_varname,allow_inconsistent_when_kwargs=True, ignore_star =True):
                args = _inconsistency_handle(parsed_varname)
                if args:
                    for ag in args:
                        if self.yaml_data.is_input(ag,ignore_star =True):
                            self.yaml_data.update_constraint(ag, descp_str,  doc_dtype=final_dtype, allow_inconsistent_when_kwargs=True, ignore_star=True)
                        else:
                            raise GoToTheNextOne(self.url , self.title, 'Inconsistency detected, arg {} doesn\'t exist'.format(ag), save=True)

                else:
                    raise GoToTheNextOne(self.url , self.title, 'Inconsistency detected, arg {} doesn\'t exist'.format(parsed_varname), save=True)
            
            else:
                self.yaml_data.update_constraint(parsed_varname, descp_str,  doc_dtype=final_dtype, allow_inconsistent_when_kwargs=True, ignore_star=True)



    def parse_input_descp(self):
        
        param_sect = self.get_param_sect()
        for ps in param_sect:
            self.parse_param_sect(ps)

    def parse_ret_type(self):
        ret_type = self.get_ret_type()
        if ret_type:
            self.yaml_data.set_attr('ret_type', ret_type)

    
    def save_file(self, save_folder):
        save_path = self.yaml_data.save_file(save_folder, self.title)
        running_stat['collected'][save_path] = self.url
    


class web_parser():
    def __init__(self, soup, parent_url, save_folder):
        self.soup = soup
        self.parent_url = parent_url
        self.save_folder = save_folder

        self.api_func = None
        self.api_class = None
        self.word_cnt = 0
        
    def init(self):
        self.api_func = self.soup.find_all('dl',{'class':'function'})
        self.api_class = self.soup.find_all('dl',{'class':'class'})
        self.word_cnt = self.cnt_word()

    def cnt_word(self):
        # count the number of word in the document
        # including title, signature, parameters, etc. of each class and function

        cnt = 0
        for af in self.api_func:
            cnt += cnt_num_word(af.get_text())
        for ac in self.api_class: 
            cnt += cnt_num_word(ac.get_text())
        return cnt




    def get_url_offset(self, func_src):
        url_pat = r'<a class=\"headerlink\" href=\"(.*?)\" title=\"Permalink to this definition\">'
        href = func_src.find_all(class_='headerlink')
        if href:
            ret = href[0]
            ret = re.search(url_pat, str(ret))
            if ret: 
                return ret.group(1)

        return None
    
    
    
    def is_child(self, src, element):
        # determine whether a function is a class method
        if not isinstance(src, list):
            src = [src]

        for ac in src:
            for desc in ac.descendants:
                if desc==element:
                    return True
        return False

    def parse_function(self):

        

        def _get_func_url(func_src):
            # get url
            url_offset = self.get_url_offset(func_src)

            if not url_offset:
                func_url = self.parent_url
                #raise GoToTheNextOne(self.parent_url , None, 'get url offset failed on the {} one'.format(i), save=True)
            else:
                func_url = self.parent_url+url_offset

            return func_url


        def _parse_func(func_src, func_url, check_class=True, check_inside_func=True):

            func_parser_obj = func_parser(func_src)
            
            if func_url==self.parent_url:
                running_stat['warning'].append('Warning: [{}] get url offset failed, use parent url {}'.format(func_parser_obj.title, self.parent_url))

            if check_class and self.is_child(self.api_class, func):
                running_stat['class_method'].append({func_parser_obj.title:func_url})
                raise GoToTheNextOne(func_url , func_parser_obj.title, 'Class method', save=False)
            
            if check_inside_func and self.is_child(self.api_func, func):
                running_stat['inside_func'].append({func_parser_obj.title:func_url})
                raise GoToTheNextOne(func_url , func_parser_obj.title, 'Inside other function', save=False)
            
            
            func_parser_obj.init(func_url)

            func_parser_obj.parse_input_descp()
            func_parser_obj.parse_ret_type()
            func_parser_obj.save_file(self.save_folder)

            return func_parser_obj


        def _detect_multiple_func(func_src):
            pat = r'<dl class="function">'
            num_func = len(re.findall(pat, str(func_src)))
            if num_func>1:
                return True, num_func
            return False, num_func

        def _multi_func_handler(func_src, func_url):

            def _parse_multi_function():

                func_str = str(func_src).replace('\n', '')
                multi_func_pat = r'<dt((?<!</dt>).)*?><code class=\"sig.*?>.*?</code>'

                all_func_str = []
                prev = 0
                first_itr= True

                for match in re.finditer(multi_func_pat, func_str):
                    if first_itr:
                        first_itr=False
                        continue
                    else:
                        all_func_str.append(func_str[prev:match.span()[0]])
                    
                    prev = match.span()[0]

                all_func_str.append(func_str[match.span()[0]:])

                return all_func_str


            all_func_str = _parse_multi_function()

            # print(func_title + '  '+ str(len(all_func_str)))
            for fs in all_func_str:

                try:
                    _parse_func(BeautifulSoup(fs, "html.parser"), func_url, check_class=False, check_inside_func=False)

                except GoToTheNextOne as gttno:
                    if gttno.save:
                        print('[{}] {} {}'.format(gttno.title, gttno.msg, gttno.link))
                        
                    continue
            
                

        
        for i, func in enumerate(self.api_func):
            
            
            try:
                # get url
                func_url = _get_func_url(func)
                #func_title = self.get_title(func)

                for kh in func.find_all(class_='katex-html'):
                    kh.decompose()

                multiple_func, num_func = _detect_multiple_func(func)
                if multiple_func:
                    running_stat['multi_func'][func_url] = num_func
                    _multi_func_handler(func, func_url)
                    #raise GoToTheNextOne(self.url , self.title, '{} function detected'.format(num_func), save=True)
                    
                else:
                    func_parser_obj = _parse_func(func, func_url)

            except GoToTheNextOne as gttno:
                if gttno.save:
                    print('[{}] {} {}'.format(gttno.title, gttno.msg, gttno.link))
                    
                continue
            except KeyboardInterrupt:
                return
            except:
                print('OTHER BUG '+ func_url)
                traceback.print_exc()
                continue



    def run(self):
        self.parse_function()

def main(test_url=None):
    web_file_folder = '/Users/danning/Desktop/deepflaw/web_source/pt_1.5_source/'
    save_folder = './pt1.5_new/' 
    stat_folder = './stat1.5_new/'
    src_path = read_yaml(stat_folder+'save_src.yaml')   # save_src_new_format.yaml for 1.6+

    global running_stat
    running_stat = {
        'class_api': [], 
        'deprecated': [], 
        'collected': {}, 
        'no_input': [], 
        'no_arg_sect': [], 
        'multi_func' : {},
        'warning':[],
        'class_method':[],
        'inside_func':[],
        'word_cnt': {}}

    module_stat = src_path

    if test_url!=None:
        if test_url in src_path:
            candidate = [test_url]
        else:
            print('invalid test url')
            return

    else:		
        candidate = list(src_path.keys())

    if not test_url: 		#delete all files
        del_file(save_folder, etd='*.yaml')

    for url in candidate:
        
        filename = src_path[url]['filename']
        soup = read_soup(web_file_folder+filename)
        

        parse_obj = web_parser(soup, url, save_folder)
        parse_obj.init()

        # count number of word
        running_stat['word_cnt'][url] = parse_obj.word_cnt

        parse_obj.run()
        module_stat[url]['num_func'] = len(parse_obj.api_func)
        module_stat[url]['num_class'] = len(parse_obj.api_class)

    save_yaml(stat_folder+'running_stat.yaml', running_stat)
    save_yaml(stat_folder+'module_stat.yaml', module_stat)
        

		
        



        
if __name__ == "__main__":
	start = time.time()

	try:
		test_url = sys.argv[1]
	except:
		test_url = None

	
	main(test_url)

	end = time.time()
	# print(end - start)