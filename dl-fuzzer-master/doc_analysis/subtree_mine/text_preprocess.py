from util import *
import argparse
import nltk
# nltk.download()
# from pywsd.utils import lemmatize_sentence
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import sys
sys.path.insert(0,'./preprocess')
from normalize_sent import *
# import generate_parsing_tree 
# from nltk.parse.corenlp import CoreNLPDependencyParser
    




# all_txt = []
# dependency_parser = CoreNLPDependencyParser(url='http://localhost:9000')

class Record():
    def __init__(self,):
        self.data = []
    def add(self, s):
        if isinstance(s, str):
            self.data.append(s)
        else:
            # list
            self.data += s
    def save(self, path):
        with open(path, 'w+') as wf:
            for c in self.data:
                wf.write(c)
                wf.write('\n--------------------------------\n')
        # save_file(path, self.data)

def remove_stopwords(src_text):
    stop_words = set(stopwords.words('english'))
    word_tokens = word_tokenize(src_text)
    filtered_sentence = [w for w in word_tokens if not w.lower() in stop_words]
    return ' '.join(filtered_sentence)

def process_yaml(yaml_data, all_anno):
    framework = yaml_data['package']
    arg_list = list(yaml_data['constraints'].keys())
    for arg in yaml_data['constraints']:
        arg_data = yaml_data['constraints'][arg]
        normalized_descp = []
        for sent in nltk.sent_tokenize(arg_data['descp']):
            
            normalized_sent, _ = normalize_sent(sent, framework, arg_list, arg)
            normalized_descp.append(normalized_sent)
        if 'doc_dtype' in arg_data:
            normalized_docdtype, _ = normalize_docdtype(arg_data['doc_dtype'], framework, arg_list, arg)
            yaml_data['constraints'][arg]['normalized_docdtype'] = normalized_docdtype
        if 'default' in arg_data and arg_data['default'] is not None:
            normalized_default, _ = normalize_default(arg_data['default'], all_anno, framework, arg_list, arg)
            yaml_data['constraints'][arg]['normalized_default'] = normalized_default
        yaml_data['constraints'][arg]['normalized_descp'] = normalized_descp
        record.add(normalized_descp)
    return yaml_data




def get_data_from_api(yaml_data):
    arg_list = []
    framework = yaml_data['package']
    for arg in yaml_data['constriants']:
        arg_data = yaml_data['constriants'][arg]
        arg_list.append(Argument(arg, arg_data.get('default', None), arg_data.get('doc_dtype', None), arg_data['descp'], framework))
        
    return arg_list


def main(constr_folder, save_to, sent_path):
    # data = []  
    global record  
    record = Record()  
    yaml_files = get_file_list(constr_folder)
    dtype_ls = read_yaml('./dtype_ls.yaml')
    all_anno = read_yaml('./preprocess/all_anno.yaml')
    del_file(save_to)
    for fpath in yaml_files:
        # if fpath !='torch.bartlett_window.yaml':
        #     continue
        info = read_yaml(os.path.join(constr_folder, fpath))
        print('Processing %s' % fpath)
        normalized_info = process_yaml(info, all_anno)
        save_yaml(os.path.join(save_to, fpath), normalized_info)
    if sent_path:
        record.save(sent_path)
    


if __name__ == "__main__":
    parser=argparse.ArgumentParser()
    # parser.add_argument('framework')
    parser.add_argument('constr_folder')
    parser.add_argument('save_to')
    parser.add_argument('--sent_path', default=None)


    args = parser.parse_args()
    # framework = args.framework
    constr_folder = args.constr_folder
    save_to = args.save_to
    sent_path = args.sent_path
    main(constr_folder, save_to, sent_path)



'''
To preprocess all:

python text_preprocess.py ../collect_doc/tf/tf21_all_src  ./normalized_doc/tf --sent_path=./normalized_doc/sent/tf_sent
python text_preprocess.py ../collect_doc/pytorch/pt1.5_new_all/  ./normalized_doc/pt --sent_path=./normalized_doc/sent/pt_sent
python text_preprocess.py ../collect_doc/mxnet/mx1.6_new_all  ./normalized_doc/mx --sent_path=./normalized_doc/sent/mx_sent
'''
