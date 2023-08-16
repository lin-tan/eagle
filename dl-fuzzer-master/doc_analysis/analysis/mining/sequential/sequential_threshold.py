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
    dataset, original_sent, api, num_sent = load_data4mining(folder, yaml_files, dtype_list, replace_dict, stop_word, sect)
    print('Data Loaded, {} sentences from {} files'. format(num_sent, len(yaml_files)))


    df = get_encoded_df(dataset)
    # word_map: word->idx
    # word_map_inverse: idx->word
    word_map, word_map_inverse = get_word_map(df)

    dataset4seq = encode_dataset(dataset, word_map)
    


    # begin customize for sequential pattern mining
    ps = PrefixSpan(dataset4seq)
    result = ps.frequent(min_support,closed=True)

    subseq_cnt=0
    for res in result:
        word_seq_idx = res[1]  # e.g. [172, 193]
        
        # check length 
        if len(word_seq_idx)<min_len:
            continue
        subseq_cnt+=1

    #print(subseq_cnt)
    return subseq_cnt

if __name__ == "__main__":
    # python sequential_mining.py tf 5 2 descp
    # python sequential_mining.py pytorch 5 2 descp
    min_support = [5]
    for ms in min_support: 
        tf_descp = main('tf', ms, 2, 'descp')
        tf_name = main('tf', ms, 1, 'name')
        pt_descp = main('pytorch', ms, 2, 'descp')
        pt_dd = main('pytorch', ms, 1, 'doc_dtype')
        pt_name = main('pytorch', ms, 1, 'name')
        mx_descp = main('mxnet', ms, 2, 'descp')
        mx_dd = main('mxnet', ms, 1, 'doc_dtype')
        mx_name = main('mxnet', ms, 1, 'name')

        total_descp = tf_descp+pt_descp+pt_dd+mx_descp+mx_dd
        total_name = tf_name+pt_name+mx_name
        print('When min_support = {}, # subseq on description: {}, # subseq on name: {}'.format(ms, total_descp, total_name))


