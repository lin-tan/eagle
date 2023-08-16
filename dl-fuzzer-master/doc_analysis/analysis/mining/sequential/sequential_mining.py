import sys
sys.path.insert(0,'..')
from mining_utils import *
from prefixspan import PrefixSpan

def encode_dataset(dataset, word_map):
    ret = []
    for sent in dataset:
        encode_sent = []
        for word in sent:
            encode_sent.append(word_map[word])
        
        ret.append(encode_sent)
    
    return ret



def main(framework, min_support, min_len, sect='descp'):

    folder = get_dir_path(framework)
    # read filess
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
    # dataset4seq[0] = [304, 266, 117]
    # original_sent[0] = 'zero or more tensors to group'
    # api = corresponding API name for each sentence
    dataset, original_sent, api = load_data4mining(folder, yaml_files, dtype_list, replace_dict, stop_word, sect)
    print('Data Loaded, {} sentences from {} files'. format(len(original_sent), len(yaml_files)))
 

    df = get_encoded_df(dataset)
    # word_map: word->idx
    # word_map_inverse: idx->word
    word_map, word_map_inverse = get_word_map(df)

    dataset4seq = encode_dataset(dataset, word_map)
    


    # begin customize for sequential pattern mining
    ps = PrefixSpan(dataset4seq)
    result = ps.frequent(min_support,closed=True)
    result.sort(key=lambda x:-x[0])   # sort by frequency
    '''
    [(7, [266]),
    (13, [172]),
    (7, [172, 193]),...
    '''

    csv_file = []
    csv_with_sentence = []
    idx = 1
    for res in result:
        freq = res[0]  # frequency of the pattern (integer)
        word_seq_idx = res[1]  # e.g. [172, 193]
        word_seq = []  # e.g. ['name', 'operation']
        
        # check length 
        if len(word_seq_idx)<min_len:
            continue
        
        idx += 1

        for word_idx in word_seq_idx:
            word_seq.append(word_map_inverse[word_idx])
            
        csv_file.append([freq, str(word_seq), len(word_seq)])
        
        
        # get related sentence
        sent_idx_set = [] # list of all sentences contains word_seq as subsentence

        for i, sent in enumerate(dataset4seq):
            valid_sent = True
            sent_offset = 0
            for word_idx in word_seq_idx:
                tmp_offset = list_idx(sent[sent_offset:], word_idx)
                if tmp_offset != -1:
                    sent_offset+= (tmp_offset+1)
                else:
                    valid_sent=False
                    break
            if valid_sent:
                sent_idx_set.append(i)
                csv_with_sentence.append([idx, freq, str(word_seq), original_sent[i], api[i], len(word_seq)])




    csv_file_df = pd.DataFrame(csv_file, columns = ['freq', 'sequence',  'len' ]) 
    csv_with_sent_df = pd.DataFrame(csv_with_sentence, columns = ['idx', 'freq', 'sequence', 'sentence', 'api', 'len' ]) 

    csv_file_df.to_csv('./new/{}_{}_freq{}_len{}.csv'.format(framework, sect, str(min_support), min_len), index=True)
    csv_with_sent_df.to_csv('./new/{}_{}_freq{}_len{}_with_sent.csv'.format(framework, sect, str(min_support), min_len), index=True)

if __name__ == "__main__":
    # python sequential_mining.py tf 5 2 descp
    # python sequential_mining.py pytorch 5 2 descp
    main(sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), sys.argv[4])
