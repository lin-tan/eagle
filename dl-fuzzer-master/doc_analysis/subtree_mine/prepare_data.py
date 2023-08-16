from util import *
from nltk.parse.corenlp import CoreNLPDependencyParser
from mining_util import *
import pandas as pd
import random
import argparse


constr_cols = ['dtype', 'structure', 'tensor_t', 'shape', 'ndim', 'enum', 'range']

def divide_train_test(df, test_ratio):
    if test_ratio==0:
         return list(range(len(df))), []
    else:
        all_index = list(range(len(df)))
        num_test = int(test_ratio*len(df))
        test_idx = random.sample(all_index, num_test)
        train_idx = [x for x in all_index if x not in test_idx]
        return train_idx, test_idx

# def select_train(df, train_size):
#     # how many parameter to select 
#     if train_size<0:
#         return list(range(len(df))), []
#     else:
#         all_api_param = []
#         for index, row in df.iterrows(): 
#             api = row['API']
#             param = row['Arg']
            

def get_sent_idx(df, candidate_idx, remove_noconstr_sent=True):
    assert len(list(set(candidate_idx))) == len(candidate_idx)
    if not remove_noconstr_sent:
        return candidate_idx
    else:
        keep_line = []
        for index in candidate_idx:
            nullness = df.iloc[index].isnull()
            include = False
            for constr_col in constr_cols:
                if not nullness[constr_col]:    # nulless=False, constr_col isn't null
                    include=True            # include this line
                    break

            if include: 
                keep_line.append(index)
        return keep_line

def prepare_sent(df, sent_idx, col='Normalized_descp', lower=False):
    return_sent = []
    for index in sent_idx:
        if not isinstance(df.iloc[index][col], str):
            print(df.iloc[index][col])
            sent = 'one_word none'
        else:
            sent = df.iloc[index][col]


        if lower:
            return_sent.append(sent.lower())
        else:
            return_sent.append(sent)
    return return_sent


def gen_idx_map(sent_idx):
    assert len(list(set(sent_idx))) == len(sent_idx)
    idx_map = {}
    for i in range(len(sent_idx)):
        idx_map[i] = sent_idx[i]
    return idx_map


def prepare_mining_dataset(sent_set, word_map, parser ):
    dataset = []
    idx = 0
    # dataset stored in format specified in https://github.com/zakimjz/TreeMiner/tree/master/TreeMiner
    for sent in sent_set:
        _, horizontal_format = generate_parsing_tree(parser, sent)
        # parse, = parser.raw_parse(sent)
        # parsing_tree = parse.tree()
        # horizontal_format = tree2horizontal(parsing_tree)
        try:
            dataset.append(encode_horizontal_tree(idx, horizontal_format, word_map))
        except:
            print('Failed when encoding horizontal tree')
            print(sent)
            print(horizontal_format)
            return
        idx += 1 
    return dataset+['']

def run(sample_path, save_path):
    # test_ratio: the ratio for test set, default 0.3 (30%). if =0, no test set 
    df = pd.read_csv(sample_path)       # get csv into df
    # train_idx, test_idx = divide_train_test(df, test_ratio, train_size)
    train_idx = list(range(len(df)))#  select_train(df)
    print('Total: %s, Train: %s' % (len(df), len(train_idx), ))
    # get the index of sentences to keep, remove the sentences without any constraiint by default
    sent_idx = get_sent_idx(df, train_idx, remove_noconstr_sent=True)  
    print('Selected %s sentences for mining from %s training samples.' %(len(sent_idx), len(train_idx)))        
    sent_set = prepare_sent(df, sent_idx, col='Normalized_descp', lower=True)
    word_set = load_data4mining(sent_set)
    encoding_df = get_encoded_df(word_set)
    # word_map: word->idx
    # word_map_inverse: idx->word
    word_map, word_map_inverse = get_word_map(encoding_df)

    # start parser:
    '''
    cd /Users/danning/stanford-corenlp-full-2018-02-27

    java -mx4g -cp "*" edu.stanford.nlp.pipeline.StanfordCoreNLPServer \
    -preload tokenize,ssplit,pos,lemma,ner,parse,depparse \
    -status_port 9000 -port 9000 -timeout 15000 &
    '''
    parser = CoreNLPDependencyParser(url='http://localhost:9000')

    dataset = prepare_mining_dataset(sent_set, word_map, parser)

    save_list(dataset, os.path.join(save_path, 'mining_input'))
    save_yaml(os.path.join(save_path, 'word_map'), word_map)
    save_yaml(os.path.join(save_path, 'inverse_word_map'), word_map_inverse)
    save_yaml(os.path.join(save_path, 'train_idx_map'), gen_idx_map(sent_idx))   # map from tree idx to sent idx
    save_yaml(os.path.join(save_path, 'test_idx_list'), test_idx)

# run('./sample/tf_label.csv', './tree_data/', test_ratio=0)


    # then encode the data into trees and store them in file


if __name__ == "__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument('sample_path')
    parser.add_argument('save_path')
    # parser.add_argument('--test_ratio', default=0)
    # parser.add_argument('--train_size', default=-1)
    

    args = parser.parse_args()
    sample_path = args.sample_path
    save_path = args.save_path
    # test_ratio = args.test_ratio
    # train_size = args.train_size
    run(sample_path, save_path)


# python prepare_data.py ./sample/tf_label.csv ./mining_data/tf/ --test_ratio=0
# python prepare_data.py ./sample/pt_label.csv ./mining_data/pt/ --test_ratio=0
# python prepare_data.py ./sample/mx_label.csv ./mining_data/mx/ --test_ratio=0



# Selected 1597 sentences for mining from 2660 training samples.    (1063)
# Selected 1095 sentences for mining from 1568 training samples.    (473)
# Selected 2549 sentences for mining from 4567 training samples.    (2018)

# selected 5241  from 8795 , delete 3554