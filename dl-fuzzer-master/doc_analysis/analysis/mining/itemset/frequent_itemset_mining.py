import sys
sys.path.insert(0,'..')
from mining_utils import *
from mlxtend.frequent_patterns import apriori, fpmax


def get_fim_result(frequent_itemsets,  use_len = True, min_len = -1, max_len=-1, sort_by = None, ascending = False):
    
    
    
    if use_len:
        frequent_itemsets['length'] = frequent_itemsets['itemsets'].apply(lambda x: len(x))

        #print(frequent_itemsets[ (frequent_itemsets['length'] >1) ])
        if min_len != -1:
            frequent_itemsets = frequent_itemsets[ (frequent_itemsets['length'] >=min_len) ]
        if max_len != -1:
            frequent_itemsets = frequent_itemsets[ (frequent_itemsets['length'] <=max_len) ]
        if sort_by!=None:
            frequent_itemsets = frequent_itemsets.sort_values(by=sort_by, ascending=ascending)

            
    return frequent_itemsets

def get_sent_set(word_set, df):
    # get a sentence set, each of the sentence contains all the words from word_idx_set
    ret_sent_idx_set = []
    
    for sent_idx, r in df.iterrows():
        yes = True
        for word in word_set:
            if df[word][sent_idx]:
                continue
            else:
                yes = False
                break
                
        if yes:
            ret_sent_idx_set.append(sent_idx)
    return ret_sent_idx_set
        


def get_word_from_idx(word_idx_set, df_word):
    
    # get the exact word in string from the column index to df
    # e.g. get_word_from_idx([26,54], df_word) -> ['dimension', 'none']
    ret = []
    for idx in word_idx_set:
        ret.append(df_word.columns[idx])
    return ret

def main(framework, algorithm='apriori', _min_support = 0.001, _min_len=2):
    folder = get_dir_path(framework)

    # read files
    yaml_files = get_file_list(folder)
        
        
    stop_word = read_file('../stopwords')
    stop_word = [s.replace('\n', '') for s in stop_word]


    dtype_list = read_yaml('../dtype_ls.yaml')[framework]


    replace_dict = {
        r'[,:;&-\[\]\(\)`\'\"\{\}]': ' ',
        r'\.$': ' ',
        r'sparse': 'ssparse',
        r'\b\d+\b': 'SOME_VALUE',
        'tensors': 'tensor'
    }

    # dataset[0] = ['zero', 'tensors', 'group']
    # original_sent[0] = 'zero or more tensors to group'
    # api = corresponding API name for each sentence
    dataset, original_sent, api = load_data4mining(folder, yaml_files, dtype_list, replace_dict, stop_word)
    print('Data Loaded, {} sentences from {} files'. format(len(original_sent), len(yaml_files)))
    
    df = get_encoded_df(dataset)


    # df: true/false table
    # each row: coresponding to each sentence, row1 is to dataset[1]
    # each col: each word
    # to visit some item [1,1] first word in first sentence: df.iloc[[1], [1]]
    if algorithm == 'fmax':
        frequent_itemsets = fpmax(df, min_support=_min_support, use_colnames=True)
    else:
        frequent_itemsets = apriori(df, min_support=_min_support, use_colnames=True)

    print("size of frequent_itemsets: "+ str(frequent_itemsets.size))
    
    fim_result = get_fim_result(frequent_itemsets, use_len = True, min_len = _min_len, max_len=-1, sort_by = 'support', ascending = False)



    # save result with sentences
    ret = []
    for idx,r in fim_result.iterrows():
        sent_set = get_sent_set(list(fim_result.loc[idx]['itemsets']), df)
        for sent_idx in sent_set:
            ret.append([idx, fim_result.loc[idx]['support'], len(sent_set), fim_result.loc[idx]['itemsets'], original_sent[sent_idx], api[sent_idx], fim_result.loc[idx]['length'] ])
                                        
                                        
                                        
    df_ret = pd.DataFrame(ret, columns = ['idx', 'support', 'cnt', 'itemsets', 'sentence', 'api', 'len' ]) 

    
    fim_result.to_csv('./{}_{}_{}_len{}.csv'.format(framework, algorithm, _min_support, _min_len), index=True)     
    df_ret.to_csv('./{}_{}_{}_len{}_with_sent.csv'.format(framework, algorithm, _min_support, _min_len), index=True)                                         
         

if __name__ == "__main__":
    # python frequent_itemset_mining.py (tf/pytorch) (fmax/apriori) 0.01 2
    main(sys.argv[1], sys.argv[2], float(sys.argv[3]), int(sys.argv[4]))

    

### TODO also replace digital number -> SOMENUMBER