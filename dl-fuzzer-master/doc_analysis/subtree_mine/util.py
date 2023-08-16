import re
import yaml
import os
import glob
import csv


# def save_file(path, content):
#     with open(path, 'wb') as f:
#         f.write(content)
    
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


def save_file(path, content):
    with open(path, 'w') as f:
        f.write(content)

def save_list(l, path):
    save_file(path, '\n'.join(l))

def write_csv(path, lines):
    with open(path, 'w', newline='') as file:
        writer = csv.writer(file)
        for l in lines:
            writer.writerow(l)


def get_file_list(dir_addr):

    files = []
    for _,_, filenames in os.walk(dir_addr):
        files.extend(filenames)
        break

    if '.DS_Store' in files:
        files.remove('.DS_Store')

    return files

def del_file(dir_addr, etd = '*.yaml'):
    # delete **recursively** all files existing in the folder
    del_files = glob.glob(dir_addr+'**/'+etd, recursive=True)
    for df in del_files:
        try:
            os.remove(df)
        except:
            pass

def create_dir(addr):
    if not os.path.exists(addr):
        print('Creating path '+ str(addr))
        os.makedirs(addr)

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

def split_str(s, sep, boundary=True, escape=True, not_empty=True):
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
        ret = [r for r in ret if not is_empty_str(r)]
    return ret

def is_empty_str(s):
    return not s or s.isspace()

    
def consecutive_anno_regex(anno):
    return r'{}((\s|,|and|or|a|an|/)+{})+'.format(anno, anno)
    

def remove_extra_space(s):
    s = re.sub(r'\s+', ' ', s)
    return s

def remove_nonalnum(s):
    s = re.sub(r'\W+', ' ', s)        # '\W == [^a-zA-Z0-9_]
    return remove_extra_space(s)

def merge_dict(dict1, dict2):
    if not dict1:
        return dict2
    if not dict2:
        return dict1
    
    merged = dict1
    for k in dict2:
        if k not in merged:
            merged[k] = dict2[k]
        else:
            merged[k] = list(set(merged[k]+dict2[k]))
    return merged


def is_subseq(x, y, ignorecase=True):
    # takes two lists
    it = iter(y)
    if ignorecase:
        return all(any(c.lower() == ch.lower() for c in it) for ch in x)
    else:
        return all(any(c == ch for c in it) for ch in x)


def replace_list_words(s, replace_list, to, boundary=True, escape=True):
    replace_re = get_bigrex(replace_list, boundary, escape)
    ret = re.sub(replace_re, to, s)
    return ret

def parse_str(s, stop_word = ['and', 'or'], sep=[',', '\'', '\"', '`', ' '], min_len = 3):
        '''
        e.g. from `complex64`, or `complex128`. to [`complex64`, `complex128`]
        '''
        # if not stop_word:
        #     stop_word = ['and', 'or']
        # if not sep:
        #     sep = [',', '\'', '\"', '`', ' ']

        s = replace_list_words(s, stop_word, '', boundary=True, escape=True)
        token = split_str(s, sep, boundary=False, escape=False, not_empty=True)


        ret = []
        for t in token:
            tmp = t.replace(' ', '')
            
            if len(tmp)<min_len or tmp.lower() in stop_word:
                continue
            ret.append(tmp)
        return ret

def rm_quo_space(s, quo=['`', '"', "'"], merge_word=True, remove_space=True):
    # remove the quotation marks and the space
    s =  replace_list_words(s, quo, '', boundary=False, escape=True)
    if merge_word:
        # replace .... a b ... to ...a_b...
        s = re.sub(r'([a-zA-Z])\s([a-zA-Z])', r'\1_\2', s)
    if remove_space:
        s = re.sub(r'\s', '', s)
    return s
     
def is_shape_range_valid(s):
    
    def count_bracket(ss):
        return ss.count('(') + ss.count(')') + ss.count('[') + ss.count(']')
    

    if count_bracket(s) >2:
        return False
    
    if s[0] not in ['(', ')', '[', ']'] or s[-1] not in ['(', ')', '[', ']']:
        if count_bracket(s) >0:
            return False
        
    if re.search(r'[^a-zA-Z0-9_\(\)\[\],\s\.]', s):
        return False
    
    return True


def list_rm_duplicate(l1, l2=[], sort=False):
    # append several list together without duplicate
    merge = list(set(l1+l2))
    if sort:
        return sorted(merge)
    else:
        return merge


def call_tree_miner(treeminer_path, input_path, output_path, min_supp, max_iter=-1):
    # treeminer_path: path to executable
    if max_iter==-1:
        command = '%s -i %s -S %s -o -l > %s' %(treeminer_path, input_path, min_supp, output_path)
    else:
        command = '%s -i %s -S %s -m %s -o -l > %s' %(treeminer_path, input_path, min_supp, max_iter, output_path)
    os.system(command)



def safe_divide(a,b):
    # a/b
    if b==0:
        return 0
    else:
        return a/b