import yaml
import os 
import re
from mlxtend.preprocessing import TransactionEncoder
import pandas as pd




def get_file_list(dir_addr):

    files = []
    for _,_, filenames in os.walk(dir_addr):
        files.extend(filenames)
        break

    if '.DS_Store' in files:
        files.remove('.DS_Store')

    return files


def read_yaml(path):
    with open(path) as yml_file:
        ret = yaml.load(yml_file, Loader=yaml.FullLoader)
    return ret

def save_yaml(path, data):
    with open(path, 'w') as yaml_file:
        yaml.dump(data, yaml_file)

def read_file(path):
    with open(path) as file:
        ret = file.readlines()
    return ret


def parse_sentences(paragraph):
    pat = r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?)\s'
    #print(re.split(pat, paragraph))
    return re.split(pat, paragraph)

def list_idx(l, element):
    # return index of element in list l, -1 if doesn't exist
    try:
        return l.index(element)
    except:
        return -1


def replace_symbol(descp, replace_dict):
    
    for s in replace_dict:
        descp = re.sub(s, replace_dict[s], descp)
    return descp

def replace_with_list(descp, word_list, to):
    # replace each word in the word list to "to" within descp
    big_regex = re.compile(r'\b%s\b' % r'\b|\b'.join(map(re.escape, word_list)))
    descp = big_regex.sub(to, descp)

    return descp

def get_encoded_df(dataset):
    te = TransactionEncoder()
    te_ary = te.fit(dataset).transform(dataset)
    df = pd.DataFrame(te_ary, columns=te.columns_)
    return df

def get_word_map(df):
    word_map = {} # word->idx
    word_map_inverse = {} # idx-> word
    columns = list(df) 
    
    for i, word in enumerate(columns): 
        word_map[word] =i
        word_map_inverse[i]=word

    return word_map, word_map_inverse

def get_dir_path(framework):
    path = {
        'tf': '/Users/danning/Desktop/deepflaw/dl-fuzzer/doc_analysis/collect_doc/tf/doc2.1_parsed_rmv1/',
        'pytorch': '/Users/danning/Desktop/deepflaw/dl-fuzzer/doc_analysis/collect_doc/pytorch/doc1.5_parsed/',
        'mxnet': '/Users/danning/Desktop/deepflaw/dl-fuzzer/doc_analysis/collect_doc/mxnet/doc1.6_parsed/'
    }
    return path[framework]

def load_data4mining(folder, file_list, dtype_list, replace_dict, stop_word, sect='descp', parse_sent = True):
    # load data for mining
    dataset = []
    original_sent = []  # original
    api = []
    num_dd = 0  # number of doc_dtype

    for i, f in enumerate(file_list[:]):  
        info = read_yaml(folder+f)
        for arg in info['constraints']:

            if 'doc_dtype' in info['constraints'][arg]:
                num_dd+=1
            
            if sect == 'name' :
                descp_str = arg
                replace_dict['_'] = ' '

            elif not info['constraints'][arg].get(sect, None):
                continue
            else: 
                descp_str = info['constraints'][arg][sect]
            if isinstance(descp_str, str):
                if parse_sent:
                    data = parse_sentences(descp_str)
                else:
                    data = [descp_str]
            else:
                # is list
                data = descp_str

            for sent in  data:
                #descp_str = re.sub(r'\s+',' ', info['constraints'][arg]['descp'])

                original_sent.append(sent)

                sent = replace_symbol(sent.lower(), replace_dict)

                # try to replace all datatype word to SOME_DTYPE
                sent = replace_with_list(sent, dtype_list['dtype'], "SOME_DTYPE")
                sent = replace_with_list(sent, dtype_list['structure'], "SOME_STRUCTURE")
                
                descp_ls = list(filter(lambda s: (len(s)>0 and not s.isspace()) and not s.isnumeric() and s not in stop_word, sent.split(' '))) 
                dataset.append(descp_ls)

                api.append(f)
            #dataset.append(list(set(descp_ls)))

    if sect=='doc_dtype':
        num_sent = num_dd
    else:
        num_sent = len(original_sent)
    return dataset, original_sent, api, num_sent
