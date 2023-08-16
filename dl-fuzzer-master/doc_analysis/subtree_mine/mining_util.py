import hashlib
from datetime import datetime
import os

from pandas.core.algorithms import isin
from util import *
from mlxtend.preprocessing import TransactionEncoder
import pandas as pd
import subprocess
import random

# def save_file(path, content):
#     with open(path, 'w') as f:
#         f.write(content)

# def save_list(l, path):
#     save_file(path, '\n'.join(l))

def load_data4mining(sent_set):
    # load data for mining
    word_set = []  # 2-D list of all words in each sentences
    for sent in sent_set:
        descp_ls = list(filter(lambda s: (len(s)>0 and not s.isspace()), sent.split())) 
        word_set.append(descp_ls)
    return word_set


def get_encoded_df(dataset):
    # takes 2D list as input
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


def encode_horizontal_tree(idx, horizontal_format, word_map):
    ret = [str(idx), str(idx), str(len(horizontal_format))]
    for node in horizontal_format:
        if node=='-1':
            ret.append('-1')
        else:
            if node not in word_map:
                print(node)
                print(word_map)
                return None 
                # print(horizontal_format)
            ret.append(str(word_map[node]))
    return ' '.join(ret)

def parse_subtree(line):
    parse = re.search(r'(.*?)\s\((.*?)\)', line)
    try:
        subtree = parse.group(1)
    except:
        return None, 1
    freq = parse.group(2)
    return ' '.join(subtree.split()), int(freq)

def decode_subtree(subtree, inverse_word_map):
    # subtree: string
    # return: str
    ret = []
    for node in subtree.split():
        if node=='-1':
            ret.append(node)
        else:
            ret.append(inverse_word_map[int(node)])

    return ' '.join(ret)

    
def call_treeminer(timeout=0.5):
    p = subprocess.Popen(['bash', 'run_treeminer.sh'])
    try:
        p.wait(timeout)
    except subprocess.TimeoutExpired:
        p.kill()
        print('killed')
    
def get_all_subtree(sent, horizontal_format, max_iter = 5, threadsafe=False):
    decoded_subtree_list = []   # list of strs

    if not threadsafe:
        mining_input_path = './TreeMiner/data/tmp_data'
        mining_output_path  = './TreeMiner/data/tmp_out'
    else:
        now = datetime.now().time()
        hash = hashlib.sha1((str(now)+str(random.random())+str(horizontal_format)).encode('utf-8')).hexdigest()
        mining_input_path = './TreeMiner/data/'+hash+'_data'
        mining_output_path = './TreeMiner/data/'+hash+'_out'

    wordset = load_data4mining([sent])
    encoding_df = get_encoded_df(wordset)
    # word_map: word->idx
    # word_map_inverse: idx->word
    word_map, word_map_inverse = get_word_map(encoding_df)
    # print(sent)
    # print(horizontal_format)
    # print(word_map)
    # print()
    encoded_tree = encode_horizontal_tree(0, horizontal_format, word_map)
    if encoded_tree is None: # keyerror:
        print("*************1**********"+str(sent))
        print("*************1**********"+str(horizontal_format))
        return 
    save_list([encoded_tree, ''], mining_input_path)
    command = './TreeMiner/treeminer -i %s -S 1 -m %s -o -l > %s' % (mining_input_path, max_iter, mining_output_path)
    # print(command)
    subprocess.call(command, shell=True)
    # print('finish')
    # exe_var = os.system()
    # assert exe_var == 0
    # call_treeminer()


    mine_result = read_file(mining_output_path)[3:]
    mine_result = mine_result[:-1]
    for l in mine_result:
        if l.startswith('ITER') or l.startswith('Tree:'):
            continue
        else:   # frequent subtree with its frequency
            subtree, freq = parse_subtree(l)
            assert freq==1
            if subtree is None: 
                print("************2***********"+str(sent))
                print("************2***********"+str(horizontal_format))
                return 
            decoded_subtree_list.append(decode_subtree(subtree, word_map_inverse))

    # remove the input and output file after exiting
    assert os.path.exists(mining_input_path)
    assert os.path.exists(mining_output_path)
    os.remove(mining_input_path)
    os.remove(mining_output_path)
        
    return decoded_subtree_list, word_map, word_map_inverse

    

def detect_match_rule(rule, sent, src_tree, maxiter, threadsafe):
    # rule: read from yaml file, in dict format
    # normalized tree in honrizontal format
    # src_tree: horizontal_format, 1D list of words and "-1"
    # sent: a string
    all_subtree, word_map, word_map_inverse = get_all_subtree(sent, src_tree, maxiter, threadsafe)
    matched_rule = []
    count = 0
    if len(all_subtree) < len(rule.keys()):
        for subtree in all_subtree:
            count += 1
            # print(count)
            if subtree in rule:
                matched_rule.append(subtree)
    else:
        for subtree in rule:
            count += 1
            # print(count)
            if subtree in all_subtree:
            # if is_subseq(subtree.split(), src_tree):
                matched_rule.append(subtree)
    return matched_rule



class Tree():
    def __init__(self, val, children=[]):
        self.value = val
        self.children = children    

def tree2horizontal(root):
    # input: nltk.tree.tree
    if isinstance(root, str):
        ret = [root]
    else:
        ret = [root.label()]
        for child in root:
            ret += tree2horizontal(child)
    
    ret.append('-1')
    return ret





def generate_parsing_tree(parser, sent):
    # type(parser) = nltk.parse.corenlp.CoreNLPDependencyParser
    '''
    create parser:

    >> cd /Users/danning/stanford-corenlp-full-2018-02-27

    >> java -mx4g -cp "*" edu.stanford.nlp.pipeline.StanfordCoreNLPServer \
    -preload tokenize,ssplit,pos,lemma,ner,parse,depparse \
    -status_port 9000 -port 9000 -timeout 15000 &

    from nltk.parse.corenlp import CoreNLPDependencyParser
    parser = CoreNLPDependencyParser(url='http://localhost:9000')
    '''
    if not isinstance(sent, str):
        print(sent)
    if pd.isna(sent):
        sent = 'one_word none'
    parse, = parser.raw_parse(sent.lower())
    parsing_tree = parse.tree()
    horizontal_format = tree2horizontal(parsing_tree)
    # horizontal_format = [x.lower() for x in horizontal_format]
    # here horizontal_format is a list of str.
    return parsing_tree, horizontal_format