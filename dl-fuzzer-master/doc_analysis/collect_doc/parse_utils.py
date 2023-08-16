

import re
import glob
import os
import bs4
from bs4 import BeautifulSoup
import requests
import pprint
import yaml
import csv

class GoToTheNextOne(Exception):
    def __init__(self, link, title, msg, save=True):
        self.link = link
        self.title = title
        self.msg = msg
        self.save = save

def is_camel_case(s):
    return s != s.lower() and s != s.upper() and "_" not in s

def parse_html(url, class_=None, text=None):
    req = requests.get(url)
    soup = BeautifulSoup(req.text, 'lxml')
    if class_!=None:
        return soup.find_all(class_=class_)
    elif text != None:
        return soup.find_all(text)


def get_file_list(dir_addr):

    files = []
    for _,_, filenames in os.walk(dir_addr):
        files.extend(filenames)
        break

    if '.DS_Store' in files:
        files.remove('.DS_Store')

    return files



def del_file(dir_addr, etd = '*.yaml'):
    # delete recursively all files existing in the folder
    del_files = glob.glob(dir_addr+etd, recursive=False)
    for df in del_files:
        try:
            os.remove(df)
        except:
            print('Failed to delete all files in '+dir_addr)


def replace_symbol(descp, replace_dict):
    
    for s in replace_dict:
        descp = re.sub(s, replace_dict[s], descp)
    return descp


def split_str(s, sep, boundary=True, not_empty=True, escape=True):
    # split str with a list of seprators
    # when not_empty: return a list of string that is not space nor empty string
    
    if boundary:
        s1 = r'\b%s\b'
        s2 = r'\b|\b'
    else:
        s1 = r'%s'
        s2 = r'|'


    if escape:
        split_re = re.compile(s1 % s2.join(map(re.escape, sep)))
    else:
        split_re = re.compile(s1 % s2.join(sep))
    ret = split_re.split(s)

    if not_empty:
        nonempty_ret = []
        for r in ret:
            if not r or r.isspace():
                continue
            else:
                nonempty_ret.append(r)

        return nonempty_ret

    return ret

def save_file(path, content):
    with open(path, 'wb') as f:
        f.write(content)
    
def read_file(path):
    with open(path) as file:
        ret = file.readlines()
    return ret
        
def save_yaml(path, data):
    with open(path, 'w') as yaml_file:
        yaml.dump(data, yaml_file)

def read_yaml(path):
    with open(path) as yml_file:
        ret = yaml.load(yml_file, Loader=yaml.FullLoader)
    return ret

def read_soup(path):
    with open(path) as f:
        soup = BeautifulSoup(f.read(), features="lxml")
        
    return soup

def write_csv(path, lines):
    with open(path, 'w', newline='') as file:
        writer = csv.writer(file)
        for l in lines:
            writer.writerow(l)

def pre_descp(descp):
    # remove space before descp
    ret = descp [(len(descp) - len(descp.lstrip())):]
    return ret

def filename_wo_duplicate(filepath, offset, msg = False):
    # generate filename without duplicate/overwrite
    while os.path.exists(filepath + offset) :
        if msg:
            print(filepath + ' exist. Try adding 2.')
        filepath += '2'
    return filepath+offset

def cnt_num_word(s):
    return len(s.split())

    
def extract_nested_bracket(s, bracket = '[]'):
    # extract all string from the nested bracket 
    # bracket can be '[]' or '()', etc

    # e.g. in s = "device: Union[torch.device, str, int, None] = None, device: Union[int, str, torch.device] = 'cuda'"
    # return ['[torch.device, str, int, None]', '[int, str, torch.device]']


    stack = []
    matched_str = []
    curr_str = ''
    for c in s:
        
            
        if c == bracket[0]: # c=='['
            stack.append([])   # stack.psuh()
            
        if stack:
            # if stack is not empty
            curr_str += c
            
        if c == bracket[1]:
            stack.pop()
            
        if not stack and curr_str:
            # if stack is empty
            matched_str.append(curr_str)
            curr_str = ''

    return matched_str

def sig_pre_process(sig, replace_dict=None, extract_bracket=False):
    # extract_bracket for pytorch 1.6+
    # e.g. device: Union[torch.device, str, int, None] = None, device2: Union[int, str, torch.device] = 'cuda'
    # convert to:  device = None, device2 = 'cuda'
    # reutrn sig_dtype_map: {'device': 'Union[torch.device, str, int, None]',
    #                           'device2': 'Union[int, str, torch.device]'}

    

    stripWS = lambda txt:'\''.join( it if i%2 else ''.join(it.split())  # remove space that is not qouted
        for i,it in enumerate(txt.split('\''))  )
    
    if replace_dict:
        sig = replace_symbol(sig, replace_dict)

    sig = stripWS(sig)
    # print('orig sig: '+str(sig))

    if replace_dict:
        sig = replace_symbol(sig, replace_dict)

    sig_dtype_map = {}

    if extract_bracket:
        extracted_str = extract_nested_bracket(sig)

        for es in extracted_str:
            match_str = re.search(r'([a-zA-Z_0-9]+)\s*:\s*([\w\.]+{})'.format(re.escape(es)), sig)
            arg = match_str.group(1)
            sig_dtype = match_str.group(2)
            sig_dtype_map[arg] = sig_dtype
            sig = re.sub(r':\s*'+re.escape(sig_dtype), '', sig, count=1)

        for match in re.findall(r'([a-zA-Z_0-9]+):([a-zA-Z_0-9\.]+)($|[=,])',sig):
            # e.g. device:Union[torch.device,str,None,int]=None,abbreviated:bool=False
            #  without [ ]
            # match = [('abbreviated', 'bool', '=')]
            arg = match[0]
            sig_dtype = match[1]
            sig_dtype_map[arg] = sig_dtype
            sig = re.sub(r':\s*'+re.escape(sig_dtype), '', sig, count=1)


    # print('sig '+str(sig))
    # print(sig_dtype_map)

    return sig, sig_dtype_map


def parse_input(sig, detect_keywordonly=False):
    # parse signature
    # input_str: obj, allow_tensor=True, allow_operation=True  
    # need to take care of default value with comma, e.g. shape = [2,2]
    
    keywordonly = False
    keywordonly_args = []
    
    # stripWS = lambda txt:'\''.join( it if i%2 else ''.join(it.split())  # remove space that is not qouted
    #     for i,it in enumerate(txt.split('\''))  )
    
    # if replace_dict:
    #     sig = replace_symbol(sig, replace_dict)
    
    
    # # print(sig)
    # # sig = stripWS(sig)
    # if extract_bracket:
    #     # for pytorch 1.6+ 
    #     # delete brackets 
    #     sig, sig_dtype_map = sig_pre_process(sig)

    #parsed_str = re.split(',(?![0-9\(\)\[\]\{\}\'])', sig)  #str(input_str).split(',')
    parsed_str = re.split(r',\s*(?=[a-zA-Z_\*])(?=[^)]*(?:\(|$))', sig) # parse by comma (,) that is not in brackets
    ret = {}

    for ps in parsed_str:
        ps = re.sub('[\']', '', ps)
        
        if ps =='*':
            keywordonly = True
            continue
            
        if '=' in ps:
            curr_arg, default = ps.split('=',1)
            ret[curr_arg] = default
            ps = curr_arg

        else:
            # no default value
            ret[ps] = None
        if detect_keywordonly and keywordonly:
            keywordonly_args.append(ps)

    if detect_keywordonly:
        return ret, keywordonly_args
    else:
        return ret

        


def prettyprint(info):
	pp = pprint.PrettyPrinter(indent=2)
	pp.pprint(info)


def get_module_name(title):
    # given tf.keras.layers.Conv2d -> tf.keras.layers
    # note: return lower case
    return '.'.join(title.lower().split('.')[:-1])



def get_bigrex(sep, boundary=True, escape=True):
    if boundary:
        s1 = r'\b%s\b'
        s2 = r'\b|\b'
    else:
        s1 = r'%s'
        s2 = r'|'


    if escape:
        return s1 % s2.join(map(re.escape, sep))
    else:
        return s1 % s2.join(sep)

