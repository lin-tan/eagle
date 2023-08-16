import hashlib
from datetime import datetime
import os
import subprocess

import sys
sys.path.insert(0,'..')
from util import * 
from mining_util import *


def main(tree, sent):
    node_seq = tree.split()
    word_map = {}           # word -> int
    inverse_word_map = {}   # int-> word
    curr_encode = 1
    encoded_tree = []
    decoded_subtree_list = []
    all_leaf_node = sent.split()
    # print(node_seq)
    for node in node_seq:
        if node!='-1':
            if node not in word_map:
                word_map[node] = curr_encode
                inverse_word_map[curr_encode] = node
                curr_encode += 1

            encoded_tree.append(str(word_map[node]))
        else:
            encoded_tree.append('-1')

    # print(encoded_tree)
    encoded_tree = ['1', '1', str(len(encoded_tree))] + encoded_tree
    encoded_tree = ' '.join(encoded_tree)
        
    now = datetime.now().time()
    hash = hashlib.sha1((str(now)+str(random.random())+str(tree)).encode('utf-8')).hexdigest()
    mining_input_path = '../TreeMiner/data/'+hash+'_data'
    mining_output_path = '../TreeMiner/data/'+hash+'_out'


    save_list([encoded_tree, ''], mining_input_path)
    command = '../TreeMiner/treeminer -i %s -S 1 -m %s -o -l > %s' % (mining_input_path, -1, mining_output_path)
    # print(command)
    subprocess.call(command, shell=True)


    mine_result = read_file(mining_output_path)[3:]
    mine_result = mine_result[:-1]
    # print(mine_result)
    for l in mine_result:
        if l.startswith('ITER') or l.startswith('Tree:'):
            continue
        else:   # frequent subtree with its frequency
            subtree, freq = parse_subtree(l)
            assert freq==1
            assert subtree!=None
            # if subtree is None: 
            #     print("************2***********"+str(tree))
            #     # print("************2***********"+str(horizontal_format))
            #     return 
            decoded_subtree_list.append(decode_subtree(subtree, inverse_word_map))



    assert os.path.exists(mining_input_path)
    assert os.path.exists(mining_output_path)
    os.remove(mining_input_path)
    os.remove(mining_output_path)

    # filter out subtrees that doesn't contain at least two leaf node
    ret = []
    for decoded_tree in decoded_subtree_list:
        cnt = 0
        for node in decoded_tree.split():
            if node in all_leaf_node:
                cnt += 1
            if cnt >=2:
                break
        if cnt >= 2:
            ret.append(decoded_tree)
        # elif cnt == 0:
        #     print(decoded_tree)
    save_list(ret, './tmp')

tree = 'NP1 NP2 DT3 a -1 -1 JJ4 constant_num_d -1 -1 NN5 d_structure -1 -1 -1 PP6 IN7 of -1 -1 NP8 NN9 type -1 -1 NN10 d_type -1 -1 -1 -1'
sent = 'a constant_num_d d_structure of type d_type'
main(tree, sent)