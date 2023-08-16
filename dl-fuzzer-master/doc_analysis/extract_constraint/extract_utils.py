
import re
import glob
import os
import yaml
import pprint
import os
import csv


def prettyprint(info):
    pp = pprint.PrettyPrinter(indent=2)
    pp.pprint(info)


def del_file(dir_addr, etd = '*.yaml'):
    # delete recursively all files existing in the folder
    del_files = glob.glob(dir_addr+'**/'+etd, recursive=True)
    for df in del_files:
        try:
            os.remove(df)
        except:
            pass

def create_dir(dir_addr, clean = True):
    if not os.path.exists(dir_addr):
        os.makedirs(dir_addr)

    if clean:
        del_file(dir_addr, etd='*')

        
def get_file_list(dir_addr):

    files = []
    for _,_, filenames in os.walk(dir_addr):
        files.extend(filenames)
        break

    if '.DS_Store' in files:
        files.remove('.DS_Store')

    return files


def get_bigrex(sep, boundary=True, escape=True):
    if boundary:
        s1 = r'\b%s\b'
        s2 = r'\b|\b'
    else:
        s1 = r'%s'
        s2 = r'|'


    if escape:
        bigrex = re.compile(s1 % s2.join(map(re.escape, sep)))
    else:
        bigrex = re.compile(s1 % s2.join(sep))

    return bigrex


def split_str(s, sep, boundary=True, not_empty=True, escape=True):
    # split str with a list of seprators
    # when not_empty: return a list of string that is not space nor empty string
    
    split_re = get_bigrex(sep, boundary, escape)
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

def replace_symbol_with_list(s, replace_list, to, boundary=True, escape=True):
    replace_re = get_bigrex(replace_list, boundary, escape)
    ret = replace_re.sub(to, s)
    return ret

def replace_symbol_with_dict(descp, replace_dict):
    def helper(s):
        for sub_rule in replace_dict:
            s = re.sub(sub_rule, replace_dict[sub_rule], s)
        return s
    if isinstance(descp, str):
        return helper(descp)
    elif isinstance(descp, list):
        return [helper(s) for s in descp]


def parse_str(dt_str, stop_word = ['and', 'or'], sep=[',', '\'', '\"', '`', ' '], min_len = 3):
        '''
        e.g. from `complex64`, or `complex128`. to [`complex64`, `complex128`]
        '''
        if not stop_word:
            stop_word = ['and', 'or']
        if not sep:
            sep = [',', '\'', '\"', '`', ' ']

        dt_s = replace_symbol_with_list(dt_str, stop_word, '', boundary=True, escape=True)
        dt_s = split_str(dt_str, sep, boundary=False, not_empty=True, escape=False)

        # p = '[,`\'\"]'
        # dt_p = re.sub(p,'!', dt_str)

        # big_regex = re.compile(r'\b%s\b' % r'\b|\b'.join(map(re.escape, stop_word)))
        # dt_p = big_regex.sub("!", dt_p)
        # print(dt_p)

        # dt_s = re.split(r'[!]', dt_p)

        ret = []
        for dt in dt_s:
            tmp = dt.replace(' ', '')
            
            if len(tmp)<min_len or tmp.lower() in stop_word:
                continue
            ret.append(tmp)
        return ret

def is_empty_str(s):
    if not s or s.isspace():
        return True
    else:
        return False

def split_str(s, sep, boundary=True, not_empty=True, escape=True):
    # split str with a list of seprators (sep)
    # when boundary=True: use \b\b
    # when not_empty: return a list of string that is not space nor empty string
    # when escape=True: escape special symbols
    
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
            if is_empty_str(r):
                continue
            else:
                nonempty_ret.append(r)

        return nonempty_ret

    return ret


def match_pat(descp, p, findall=False):
    # match pattern for certain sentence
    if findall:
        rslt = re.findall(r'{}'.format(p), descp)
    else:
        rslt = re.search(r'{}'.format(p), descp)
    
    return rslt

def get_group(rslt, pat, p, group='group', findall=False):
    if not rslt:
        return []

    if isinstance(group, str):
        g = pat.pat_dict['pat'][p].get(group, None)
    else:
        g = int(group)


    if not g:
        return []

    ret = []

    if findall:
        ret = []
        for nv_it in rslt:
            nv = get_group_findall(nv_it, pat, p, group)
            if nv:
                ret.append(nv)
    else:
        if rslt.group(g):
            ret = [rslt.group(g)]

    return ret

def get_group_findall(nv_it, pat, p, group='group'):
    if isinstance(group, str):
        g = pat.pat_dict['pat'][p].get(group, None)
    else:
        g = int(group)

    if isinstance(nv_it, str):
        ret = nv_it
    else:
        ret = nv_it[g-1]

    return ret

    



def pre_descp(descp, pat=None):
    ret = descp [(len(descp) - len(descp.lstrip())):]
    ret = ret.lower()
    # if ret and ret[0]=='[':
    #     ret = ret.split(']',1)[-1]
    #     ret = ret [(len(ret) - len(ret.lstrip())):]

    if pat:
        replace = pat.pat_dict.get('replace', {})
        ret = replace_symbol_with_dict(ret, replace)

    
    return ret

def save_file(path, content):
    with open(path, 'w') as f:
        f.write(content)
    
def read_file(path):
    with open(path) as file:
        ret = file.readlines()
    return ret
        
def write_csv(path, lines):
    with open(path, 'w', newline='') as file:
        writer = csv.writer(file)
        for l in lines:
            writer.writerow(l)

def save_list(l, path):
    save_file(path, '\n'.join(l))

def read_list(path):
    ret = read_file(path)
    return [x.replace('\n', '') for x in ret]

def save_yaml(path, data):
    with open(path, 'w') as yaml_file:
        yaml.dump(data, yaml_file)

def read_yaml(path):
    with open(path) as yml_file:
        ret = yaml.load(yml_file, Loader=yaml.FullLoader)
    return ret



def list_rm_duplicate(l1, l2=None, sort = False):
    # append several list together without duplicate
    if l2:
        tmp = l1+l2
    else:
        tmp = l1
    ret = list(set(tmp))
    if sort:
        return sorted(ret)
    else:
        return ret

def convert_str2numeric(s):
    try:
        return int(s)
    except ValueError:
        return float(s)

def convert_default(val):

    # check bool
    bool_val = ['false', 'true']
    if str(val).lower() in bool_val:
        return {'val':str(val).replace("'",''), 'dtype':'bool', 'ndim': 0}
        
    
    if str(val) in  ['None', '_Null']:
        return {'val':'None', 'dtype':None, 'ndim': None}
    else:
        try:
            return {'val':int(val), 'dtype':'int', 'ndim': 0}
        except:
            pass
        
        try:
            return {'val':float(val), 'dtype':'float', 'ndim': 0}
        except:
            pass

        if len(str(val))>0 and str(val)[0] in ['(', '[']:
            ndim = len(re.findall(r'[\[\(]', str(val).split(',')[0]))
            return {'val':str(val), 'dtype':None, 'ndim': ndim}

        elif re.match(r'.*\..*', str(val))!=None or str(val).startswith('<'):
            return {'val':str(val), 'dtype':None, 'ndim': None}
        else:
            return {'val':str(val), 'dtype':'string', 'ndim': None}
            

        
def match_name(varname, pat):
    for p in pat.pat_dict:
        if re.match(r'{}'.format(p), varname.lower()):
            return pat.pat_dict[p]
        
    return None

def parse_sentences(paragraph):
    pat = r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?)\s'
    #print(re.split(pat, paragraph))
    return re.split(pat, paragraph)


def is_balanced(src):
    """
    Finds out how balanced an src is.
    With a string containing only brackets.

    >>> is_matched('[]()()(((([])))')
    False
    >>> is_matched('[](){{{[]}}}')
    True
    """


    opening = tuple('({[')
    closing = tuple(')}]')
    mapping = dict(zip(opening, closing))
    queue = []

    for letter in src:
        if letter in opening:
            queue.append(mapping[letter])
        elif letter in closing:
            if not queue or letter != queue.pop():
                return False
    return not queue


def get_original_case(sentence, keyword):
    ret = re.search(keyword, sentence, re.IGNORECASE)
    if ret:
        return ret.group(0)
    else:
        return None


def parse_sentences(paragraph):
    pat = r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?)\s'
    #print(re.split(pat, paragraph))
    return re.split(pat, paragraph)


def get_module_name(title):
    # given tf.keras.layers.Conv2d -> tf.keras.layers
    # note: return lower case
    return '.'.join(title.lower().split('.')[:-1])


def check_changed(data):
    target=['dtype', 'ndim', 'shape', 'enum', 'range', 'structure', 'tensor_t']
    for arg in data['constraints']:
        for cat in target:
            constr = data['constraints'][arg].get(cat, [])
            if isinstance(constr, list):
                if len(constr)>0:
                    return True
            else:
                if constr:
                    return True
    return False