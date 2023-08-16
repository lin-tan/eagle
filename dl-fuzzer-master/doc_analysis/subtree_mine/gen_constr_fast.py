from util import *
from extractor import *
import os
import argparse
import time
from multiprocessing import Process


MAX_PROC = 100
MAX_ITER = 7


def run_doc_extractor(doc_data, dtype_map, rule, all_category, all_anno, maxiter):
    doc_extractor = Doc_Extractor(doc_data, dtype_map, rule, all_category, all_anno, maxiter)
    try:
    # if True:
        new_doc_data = doc_extractor.extract_constr()
    except Exception as e:
        print("**********************Fail %s **********************************" % doc_data['title'])
        print(e)
        return 
    return new_doc_data, doc_extractor.success

def get_maxiter(rulefile):
    # rulefile = read_yaml(rule_path)
    max_len = 0
    for r in rulefile:
        curr_len =  len([x for x in r.split() if x != '-1'])
        max_len =  max(max_len,curr_len)
    return max_len -1

    
def extract_single_doc(file_path, fname, dtype_map, rule, all_category, all_anno, max_iter):
    print('[%s] Extracting %s'% (os.getppid(), fname))
    start = time.time()
    # if docf!='tf.keras.layers.embedding.yaml':
    #     continue
    doc_data = read_yaml(file_path)
    new_doc_data, success = run_doc_extractor(doc_data, dtype_map, rule, all_category, all_anno, max_iter)
    if success:
        save_path = os.path.join(save_folder, 'success')
        # success_cnt += 1
    else:
        save_path = os.path.join(save_folder, 'fail')
    # create_dir(save_path)
    # print(save_path)
    save_yaml(os.path.join(save_path, fname), new_doc_data)
    # print('Saving '+str(docf))
    end = time.time()
    print('Finish %s, Time: %s'% (fname, end - start))

def gen(doc_folder, save_folder, rule_path, dtype_map_path, all_cat_path='./config/all_category.yaml', all_anno_path='./preprocess/all_anno.yaml'):
    doc_files = get_file_list(doc_folder)
    del_file(save_folder)
    
    create_dir(os.path.join(save_folder, 'fail'))
    create_dir(os.path.join(save_folder, 'success'))

    rule = read_yaml(rule_path)
    max_iter = min(MAX_ITER, get_maxiter(rule))
    dtype_map = read_yaml(dtype_map_path)
    all_category = read_yaml(all_cat_path)      # all constraint categories
    all_anno = read_yaml(all_anno_path)         # all annotaions
    # success_cnt = 0
    # end=start=0
    process_pool= []
    pcnt = 0
    
    for docf in doc_files: 
        pcnt += 1
        
        file_path = os.path.join(doc_folder, docf)

        # tmp:
        # extract_single_doc(file_path, docf, dtype_map, rule, all_category, all_anno, max_iter)

        p = Process(target=extract_single_doc, args=(file_path, docf, dtype_map, rule, all_category, all_anno, max_iter))
        p.start()
        process_pool.append(p)

        if pcnt >= MAX_PROC:
            for p in process_pool:
                p.join()
            pcnt = 0
            process_pool = []

        # extract_single_doc(file_path, fname, dtype_map, rule, all_category, all_anno, max_iter)
    print('All finish')
    #print('Extract constraints from %s / %s APIs.' %(success_cnt, len(doc_files)))
    

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
    start = time.time()
    gen(doc_folder, save_folder, rule_path, dtype_map_path, all_cat_path, all_anno_path)
    print('Duratino: %s seconds' %(time.time()-start))


# python gen_constr.py ../collect_doc/tf/tf21_all_src ./constr/tf/ ./mining_data/tf/subtree_rule.yaml ./config/tf_dtype_map.yaml

# doc_folder = '../collect_doc/tf/tf21_all_src'
# save_folder = './constr/tf/'
# rule_path = './tree_data/subtree_rule.yaml'
# dtype_map_path = './config/tf_dtype_map.yaml'
# main(doc_folder, save_folder, rule_path, dtype_map_path)



# tf: Duratino: 1246.9579780101776 
# pt: Duratino: 321.61626648902893 seconds
# mx: Duratino: 484.6426386833191 seconds
