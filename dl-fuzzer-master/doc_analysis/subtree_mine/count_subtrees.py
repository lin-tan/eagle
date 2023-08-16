# copied from parse_mine_result.py
# remove the denormalization, and mapping to original sentences part
# only count the number of the subtrees mined. 


from util import *
import pandas as pd
import argparse
from mining_util import *

def parse_tree_idx(line, tree_idx_map):
    tree_idx = re.search(r'Tree: (.*)', line).group(1)
    sent_idx = [tree_idx_map[int(x)] for x in tree_idx.split()]
    unique_sent_idx = sorted(list(set(sent_idx)))
    return tree_idx, ' '.join([str(x) for x in sent_idx]), ' '.join([str(x) for x in unique_sent_idx])






# from nltk.corpus import stopwords
# def filter_out_stopwords(decoded_subtree) :
#     # decoded_subtree: list of string
#     stop_words = set(stopwords.words('english'))
#     for w in decoded_subtree:
#         if w!='-1' and w not in stop_words:
#             return True

#     return False

def run(mine_result_path):
    print('Parsing the Mining Results from %s.'%mine_result_path)
    mine_result = read_file(mine_result_path)[3:]     # the first three lines are DBASE_NUM_TRANS, DBASE_MAXITEM, MINSUPPORT
    mine_result = mine_result[:-1]      # the last line is TIME

    subtree_list = []               # 2-D list, subtree with encoded integers
    # freq_list = []
    # subtree_decoded_list = []       # 2-D list, subtree decoded with actual words
    # tree_idx_list = []              # 2-D list, the idx of tree the subtree comes from
    # sent_idx_list = []              # 2-D list, the idx of actual sent in xx_sample/xx_label.csv
    # unique_sent_idx_list = []       

    # inverse_word_map = read_yaml(inverse_word_map_path)
    # tree_idx_map = read_yaml(tree_idx_map)
    for l in mine_result:
        if l.startswith('ITER'):
            continue
        elif l.startswith('Tree:'):
            pass
            # tree_idx, sent_idx, unique_sent_idx = parse_tree_idx(l, tree_idx_map)
            # tree_idx_list.append(tree_idx)
            # sent_idx_list.append(sent_idx)
            # unique_sent_idx_list.append(unique_sent_idx)
        else:   # frequent subtree with its frequency
            subtree, freq = parse_subtree(l)
            subtree_list.append(subtree)
            # freq_list.append(freq)
            # subtree_decoded_list.append(decode_subtree(subtree, inverse_word_map))
    
    # assert len(subtree_list) == len(subtree_decoded_list) == len(tree_idx_list) == len(sent_idx_list) == len(freq_list)
    
    # for i in range(len(unique_sent_idx_list)):
    #     if len(unique_sent_idx_list[i].split()) != freq_list[i]:
    #         print('Find error on subtree %s (%s)' % (subtree_list[i], subtree_decoded_list[i]))
    #         print('Tree idx: %s ; Sent idx: %s, Unique sent idx %s' % (tree_idx_list[i], sent_idx_list[i], unique_sent_idx_list[i]))
    #         print('%s != %s' %(len(unique_sent_idx_list[i].split()), freq_list[i]))
    #         return

    print(len(subtree_list))

    # data = {'Subtree': subtree_list,
    #     'Decoded_Subtree': subtree_decoded_list,
    #     'Tree_IDX': tree_idx_list ,
    #     'Sent_IDX': sent_idx_list,
    #     'Unique_Sent_IDX': unique_sent_idx_list,
    #     'Frequency': freq_list}

    # df = pd.DataFrame(data)
    # df = df.sort_values(by='Frequency', ascending=False)
    # df.to_csv(save_path, index=False)
    # print('Parsing Succeed')
    # return df

if __name__ == "__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument('mine_result_path')
    # parser.add_argument('inverse_word_map_path')
    # parser.add_argument('tree_idx_map')
    # parser.add_argument('save_path')
    
    

    args = parser.parse_args()
    mine_result_path = args.mine_result_path
    # inverse_word_map_path = args.inverse_word_map_path
    # tree_idx_map = args.tree_idx_map
    # save_path = args.save_path
    run(mine_result_path)

# python parse_mine_result.py ./mining_data/tf/mine_result  ./mining_data/tf/inverse_word_map ./mining_data/tf/train_idx_map  ./mining_data/tf/parsed_result.csv
# python parse_mine_result.py ./mining_data/pt/mine_result  ./mining_data/pt/inverse_word_map ./mining_data/pt/train_idx_map  ./mining_data/pt/parsed_result.csv
# python parse_mine_result.py ./mining_data/mx/mine_result  ./mining_data/mx/inverse_word_map ./mining_data/mx/train_idx_map  ./mining_data/mx/parsed_result.csv



