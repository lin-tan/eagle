from util import *
from extractor import *
import os
import argparse
import time





def run_doc_extractor(doc_data, dtype_map, rule, all_category, all_anno):
    doc_extractor = Doc_Extractor(doc_data, dtype_map, rule, all_category, all_anno)
    new_doc_data = doc_extractor.extract_constr()
    return new_doc_data, doc_extractor.success

def gen(doc_folder, save_folder, rule_path, dtype_map_path, all_cat_path='./config/all_category.yaml', all_anno_path='./preprocess/all_anno.yaml'):
    doc_files = get_file_list(doc_folder)
    # del_file(save_folder)
    rule = read_yaml(rule_path)
    dtype_map = read_yaml(dtype_map_path)
    all_category = read_yaml(all_cat_path)      # all constraint categories
    all_anno = read_yaml(all_anno_path)         # all annotaions
    success_cnt = 0
    end=start=0
    for docf in doc_files:
        if docf.lower()!='tf.clip_by_global_norm.yaml':
            continue
        print('Extracting %s, time(last) %s' %(str(docf), end - start))
        start = time.time()
        doc_data = read_yaml(os.path.join(doc_folder, docf))
        new_doc_data, success = run_doc_extractor(doc_data, dtype_map, rule, all_category, all_anno)
        # if success:
        #     save_path = os.path.join(save_folder, 'success')
        #     success_cnt += 1
        # else:
        #     save_path = os.path.join(save_folder, 'fail')
        # create_dir(save_path)
        # save_yaml(os.path.join(save_path, docf), new_doc_data)
        end = time.time()
    print('Extract constraints from %s / %s APIs.' %(success_cnt, len(doc_files)))
    

if __name__ == "__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument('doc_folder')
    parser.add_argument('save_folder')
    parser.add_argument('rule_path')
    parser.add_argument('dtype_map_path')
    parser.add_argument('--all_cat_path', default='./config/all_category.yaml')
    parser.add_argument('--all_anno_path', default='./preprocess/all_anno.yaml')
    
    

    args = parser.parse_args()
    doc_folder = args.doc_folder
    save_folder = args.save_folder
    rule_path = args.rule_path
    dtype_map_path = args.dtype_map_path
    all_cat_path = args.all_cat_path
    all_anno_path = args.all_anno_path
    gen(doc_folder, save_folder, rule_path, dtype_map_path, all_cat_path, all_anno_path)


# python gen_constr.py ../collect_doc/tf/tf21_all_src ./constr/tf/ ./mining_data/tf/subtree_rule.yaml ./config/tf_dtype_map.yaml

# doc_folder = '../collect_doc/tf/tf21_all_src'
# save_folder = './constr/tf/'
# rule_path = './tree_data/subtree_rule.yaml'
# dtype_map_path = './config/tf_dtype_map.yaml'
# main(doc_folder, save_folder, rule_path, dtype_map_path)
