
import os
import pandas as pd
import argparse
from nltk.parse.corenlp import CoreNLPDependencyParser
from build_mapping import get_all_comb
import sys
sys.path.insert(0,'../')
from util import *
from mining_util import *
import train
from multiprocessing import Process, Queue



# all_category = read_yaml('../config/all_category.yaml')

# train.constr_cat = {
#     'dtype': 'dtype', 
#     'structure': 'structure', 
#     'tensor_t': 'structure',    # merge into structure 
#     'shape': 'shape', 
#     'ndim': 'ndim', 
#     'range' : 'range',
#     'enum': 'enum'
#     }
cat_group = {
    'dtype': ['dtype'],
    'structure': ['structure'], # no tensor_t since tensor_t and structure are merged when counting IR
    'shape': ['shape', 'ndim'],
    'validvalue': ['range', 'enum']
}

MAX_SENT_LEN = 70
MAX_PROC = 400


def init_sent_ir():
    # sentence-level IR
    ret = {}
    for cat in train.constr_cat.values():
        ret[cat] = set()
    return ret

def is_ir_empty(sent_ir):
    for cat in sent_ir:
        if sent_ir[cat]:
            return False
    return True
class test_sent():
    def __init__(self, row):
        self.normalized_sent = row['Normalized_descp']
        if pd.isna(self.normalized_sent):
            self.normalized_sent = 'one_word none'
        self.horizontal_tree = None
        self.label_ir = self.get_ir_label(row)
    

    def get_ir_label(self, row):
        label_ir = init_sent_ir()
        nulless = row.isnull()
        for cat in train.constr_cat:
            if not nulless[cat]: 
                for c in row[cat].split(';'):
                    label_ir[train.constr_cat[cat]].add(c)
        
        return label_ir
    
    def set_horizontal_tree(self, parser):
        _, horizontal_format = generate_parsing_tree(parser, self.normalized_sent)
        self.horizontal_tree = horizontal_format

    # def reset_extracted_ir(self,):
    #     self.extracted_ir = None
    
    # def set_extracted_ir(self, new_ir):
    #     self.extracted_ir = new_ir

class Eval_Counter():
    def __init__(self):
        self.reset()
        
    def init_cnt(self):
        cat_success_cnt = {}
        for big_cat in cat_group:
            cat_success_cnt[big_cat] = 0
        return cat_success_cnt

    def cnt_sum(self, cat_cnt):
        ret_sum = 0
        for big_cat in cat_cnt:
            ret_sum += cat_cnt[big_cat]
        return ret_sum

    def reset(self,):
        self.correct_sent_cnt = 0
        self.num_sent_with_ir = 0               # either extracted or in the label
        self.num_sent = 0                       # with or without ir
        self.cat_success_cnt = self.init_cnt()  # count of IR for certain big_cat is correct
        self.cat_extracted = self.init_cnt()    # count of IR extracted for each big_cat
        self.cat_labeled = self.init_cnt()      # count of IR labeled for each big_cat
        self.precision = {}                     # precision for each big_cat and total
        self.recall = {}                        # recall for each big_cat and total
        self.f1 = {}
        self.accuracy = 0                       # num_correct_sent/num_sent_with_ir 

    def update(self, label_ir, extracted_ir):
        # for a single sentence
        '''
        update the following:  
        [x]self.correct_sent_cnt = 0
        [x]self.num_sent_with_ir = 0    # either extracted or in the label
        [x]self.num_sent = 0               # with or without ir
        [x]self.cat_success_cnt = self.init_cnt()     # count of IR for certain big_cat is correct
        [x]self.cat_extracted = self.init_cnt()       # count of IR extracted for each big_cat
        [x]self.cat_labeled = self.init_cnt()         # count of IR labeled for each big_cat
        '''

        def _compare_big_cat(big_cat):
            for cat in cat_group[big_cat]:
                if label_ir[cat] != extracted_ir[cat]:
                    return False
            return True
            
        def _is_bigcat_empty(big_cat, sent_ir):
            for cat in cat_group[big_cat]:
                if sent_ir[cat]:
                    return False
            return True


        self.num_sent += 1
        if is_ir_empty(label_ir) and is_ir_empty(extracted_ir):
            return 
        self.num_sent_with_ir += 1

        all_correct = True
        for big_cat in cat_group:
            label_ir_empty = _is_bigcat_empty(big_cat, label_ir)
            extracted_ir_empty = _is_bigcat_empty(big_cat, extracted_ir)
            if not label_ir_empty:
                self.cat_labeled[big_cat] += 1
            if not extracted_ir_empty:
                self.cat_extracted[big_cat] += 1

            if not label_ir_empty and not extracted_ir_empty:
                # otherwise no need to compare, either both empty or incorrect
                if _compare_big_cat(big_cat):
                    self.cat_success_cnt[big_cat]+=1
                else:
                    all_correct = False
            elif not label_ir_empty or not extracted_ir_empty:
    
                all_correct = False

        # print(extracted_ir)
        # print(label_ir)
        # print(all_correct)
        # print()
        # print(self.correct_sent_cnt)
        if all_correct:
            self.correct_sent_cnt += 1

            
    def eval(self):
        def _calulate_f1(p, r):
            return 2*safe_divide(p*r, p+r)

        for big_cat in cat_group:
            self.precision[big_cat] = safe_divide(self.cat_success_cnt[big_cat], self.cat_extracted[big_cat])
            self.recall[big_cat] = safe_divide(self.cat_success_cnt[big_cat], self.cat_labeled[big_cat])
            self.f1[big_cat] = _calulate_f1(self.precision[big_cat], self.recall[big_cat])

        self.precision['all'] = safe_divide(self.cnt_sum(self.cat_success_cnt), self.cnt_sum(self.cat_extracted))
        self.recall['all'] = safe_divide(self.cnt_sum(self.cat_success_cnt), self.cnt_sum(self.cat_labeled))
        self.f1['all'] = _calulate_f1(self.precision['all'], self.recall['all'])

        self.accuracy = safe_divide(self.correct_sent_cnt, self.num_sent_with_ir)

    # for aa in all_attr:
    #     if len(in_doc[aa])!=len(extracted[aa]):
    #         print('error')
    #         return
    #     precision[aa] = divide(success_cnt[aa], extracted[aa].count(1))
    #     recall[aa] = divide(success_cnt[aa], in_doc[aa].count(1))

    # precision['total'] = divide(count_sum(success_cnt), count_sum(extracted, count1=True))
    # recall['total'] = divide(count_sum(success_cnt), count_sum(in_doc, count1=True))

    
    # accuracy = all_correct_cnt/num_param_with_contr


    
class Eval_Result():
    def __init__(self):
        self.title = ['min_support', 'min_confidence', 'max_len', 'fold#', 'accuracy', 'precision', 'recall', 'f1']
        self.bigcat_order = []
        self.update_title()
        self.row = []
        self.df = None
    def update_title(self):
        for big_cat in cat_group:
            self.bigcat_order.append(big_cat)
            self.title.append(big_cat+'_pre')
            self.title.append(big_cat+'_recall')
            self.title.append(big_cat+'_f1')

    def update(self, min_supp, min_conf, max_len, i, eval_counter):
        curr_row = [min_supp, min_conf, max_len, i, eval_counter.accuracy, eval_counter.precision['all'], eval_counter.recall['all'], eval_counter.f1['all']]
        for big_cat in self.bigcat_order: 
            curr_row.append(eval_counter.precision[big_cat])
            curr_row.append(eval_counter.recall[big_cat])
            curr_row.append(eval_counter.f1[big_cat])
        self.row.append(curr_row)
    
    def to_csv(self, path):
        # write_csv(path, self.row)
        self.df = pd.DataFrame(self.row, columns = self.title)
        self.df.to_csv(path, index=False)
    
    def save_avg(self, path):
        agg_col = {}
        for col in self.df.columns:
            if col != 'fold#':
                agg_col[col] = 'mean'
        new_df = self.df.groupby(self.df.index // 5).agg(agg_col)
        new_df.to_csv(path.replace('.csv', '_avg.csv'), index=False)

def init_testset(label_df, parser):
    testset = []

    for index, row in label_df.iterrows():
        # index to row  = index to testset
        tmp_obj = test_sent(row)
        tmp_obj.set_horizontal_tree(parser)
        testset.append(tmp_obj)

    return testset
    
def match_apply_rule(all_rule, test_sent_obj, max_len):
    #   test_sent_obj.reset_extracted_ir()  # IMPORTANT
    matched_rule = detect_match_rule(all_rule, test_sent_obj.normalized_sent.lower(), test_sent_obj.horizontal_tree, max_len, threadsafe=True) # in util.py
    extracted_ir = init_sent_ir()
    for subtree in matched_rule:
        for constr_cat in all_rule[subtree]:   # for each constraint category
                for constr_ir in all_rule[subtree][constr_cat]:
                    extracted_ir[constr_cat].add(constr_ir)
    return extracted_ir

    
def single_proc(q, rule, test_sent_obj, max_len):
    extracted_ir = match_apply_rule(rule, test_sent_obj, max_len)   # match and apply rules to the test sentence
    # extracted IR should be updated to the test_sent_obj.extracted_ir
    q.put([test_sent_obj.label_ir, extracted_ir])
        
def main(framework, label_path, chuck_record_path, rule_folder, save_path, config_path ): 
    del_file(save_path, etd='*')
    config = read_yaml(config_path)
    chuck_record = read_yaml(chuck_record_path)
    label_df = pd.read_csv(label_path)
    parser = CoreNLPDependencyParser(url='http://localhost:9000')
    testset = init_testset(label_df, parser)
    assert len(testset) == len(label_df)
    num_fold = config['num_fold']
    all_comb = get_all_comb(num_fold, config['min_support'], config['min_conf'], config['max_len'])

    eval_counter = Eval_Counter()
    result = Eval_Result()

    print('Start')
    for min_supp, min_conf, max_len, i in all_comb:
        # 1. read rules with these combination
        rule_path = os.path.join(rule_folder, '%s-fold_minsupp_%s_minconf_%s_maxlen_%s_rule_%s.yaml'%(num_fold, min_supp, min_conf, max_len, i))
        rule = read_yaml(rule_path)
        # 2. get test set 
        test_chuck_id = i 
        test_row_idices = chuck_record[test_chuck_id]
        # test data is in `testset` with index in `test_row_idices`
        # 3. detect & apply match rules to each sent in the testset
        eval_counter.reset()  # IMPORTANT
        process_pool = []
        pcnt = 0
        q = Queue()
        for test_idx in test_row_idices:
            test_sent_obj = testset[test_idx]
            if len(test_sent_obj.horizontal_tree) >MAX_SENT_LEN:
                continue
            p = Process(target=single_proc, args=(q, rule, test_sent_obj, max_len))
            p.start()
            process_pool.append(p)
            pcnt += 1

            if pcnt >= MAX_PROC:

                print('[%s] Start %s processes' % (os.getppid(), MAX_PROC))
                for p in process_pool:
                    label_ir, extracted_ir = q.get()
                    eval_counter.update(label_ir, extracted_ir)
                for p in process_pool:
                    p.join()
                pcnt=0
                process_pool = []
                print('[%s] Finish %s processes' % (os.getppid(), MAX_PROC))
                

        for p in process_pool:
            label_ir, extracted_ir = q.get()
            eval_counter.update(label_ir, extracted_ir)

        for p in process_pool:
            p.join()
            

        # 4. calculate acc, pre, recall, f1 score
        #   acc: sent-level, pre/recall/f1 on sent-cat level
        #   since the label is on sent-level, all metric is on sent-level, not param-level
        # print(eval_counter.precision)
        eval_counter.eval()
        result.update(min_supp, min_conf, max_len, i, eval_counter)
        print('Evaluate min_support=%s, min_confidence=%s, max_len=%s, fold#%s, acc=%s'%(min_supp, min_conf, max_len, i, eval_counter.accuracy))
        
        print('Writing result to %s' % save_path)
        result.to_csv(save_path)
        result.save_avg(save_path)

    
if __name__ == "__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument('framework')
    parser.add_argument('label_path')
    parser.add_argument('chuck_record_path')
    parser.add_argument('rule_folder')
    parser.add_argument('save_path')
    parser.add_argument('--config_path', default='./config.yaml')
    

    args = parser.parse_args()
    framework = args.framework
    label_path = args.label_path
    chuck_record_path = args.chuck_record_path
    rule_folder = args.rule_folder
    save_path = args.save_path
    config_path = args.config_path
    main(framework, label_path, chuck_record_path, rule_folder, save_path, config_path)

# framework = 'tf'
# label_path = '../sample/tf_label.csv'
# chuck_record_path = './chuck_5/tf_chuck.yaml'
# rule_folder = './rule/tf/'
# save_path = '/Users/danning/Desktop/deepflaw/exp2/code/dl-fuzzer/doc_analysis/subtree_mine/cross_val/result/tf.csv'

# python eval.py tf ../sample/tf_label.csv ./chuck_5/tf_chuck.yaml ./rule/tf/ ./result/tf.csv
