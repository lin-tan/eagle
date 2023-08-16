import pandas as pd
from util import * 
import argparse

constr_cat = {
    'dtype': 'dtype', 
    'structure': 'structure', 
    'tensor_t': 'structure',    # merge into structure 
    'shape': 'shape', 
    'ndim': 'ndim', 
    'range' : 'range',
    'enum': 'enum'
    }
# anno_path = '/local1/xdanning/docter/code/dl-fuzzer/doc_analysis/subtree_mine/preprocess/all_anno.yaml'
anno_path = './preprocess/all_anno.yaml'
anno_list = read_yaml(anno_path)
#['D_TYPE', 'D_STRUCTURE', 'PARAM', 'THIS_PARAM', 'BSTR', 'QSTR', 'CONSTANT_NUM', 'CONSTANT_BOOL', 'REXPR']

def init_constr_count():
    ret = {}
    for cat in constr_cat.values():
        ret[cat] = {}
    return ret


def init_constr_record():
    ret = {}
    for cat in constr_cat.values():
        ret[cat] = set()
    return ret

def filter_constr_by_anno(subtree, constr_val):
    # return False if constr_val contains anno that subtree doesn't have
    def str_constains_anno(s):
        contain_anno = []
        for anno in anno_list:
            if anno in s:
                contain_anno.append(anno)
        return contain_anno

    def subtree_contain_anno(subtree, anno_list):
        # if the subtree contains all the anno in the anno_list
        for anno in anno_list:
            if anno.lower() not in subtree: # subtree doesn't contain one of the anno
                # TODO: this need to change: CONSTANT_NUM-D
                return False
        return True

    contain_anno = str_constains_anno(constr_val)       # the annotaions this constraints contains.
    if not subtree_contain_anno(subtree, contain_anno):
        return False
    return True
                

def parse_constr(row, decoded_subtree, filter_by_anno=True):

    def _constr_empty(constr_row):
        for cat in constr_row:
            if constr_row[cat]:
                return False
        return True
    
    constr_row = init_constr_record()
    nulless = row.isnull()
    for cat in constr_cat:
        if not nulless[cat]: 
            for c in row[cat].split(';'):
                if filter_by_anno and not filter_constr_by_anno(decoded_subtree, c):
                    # print(decoded_subtree + ' : ' + c)
                    continue
                constr_row[constr_cat[cat]].add(c)
    assert (filter_by_anno or not _constr_empty(constr_row))    # if filter_by_anno=False, the constr_row shoundn't be empty
    return constr_row


def update_constr(all_constr, constr_row):
    for cat in constr_row:
        for constr_val in constr_row[cat]:
            if constr_val in all_constr[cat]:
                all_constr[cat][constr_val]+=1
            else:
                all_constr[cat][constr_val]=1

    return all_constr




def select_constr(constr_cnt, subtree_supp, min_conf, top_k):
    # constr_cnt:  {'dtype': {'constr1': freq1}, 'structure': ...}
    # subtree_supp: number of trees this subtree appears in 
    # min_conf ([0,1] float): the minimum freq that the constr appears together with the subtree
    #   e.g., if min_conf=0.8, the freq of constr has to be at least 0.8*subtree_supp to be selected
    #   min_conf=0: select all.

    # top_k: select top k most frequent cosntratints. if -1, select all that meet min_conf

    def _get_freq_threshold():
        init_freq_threshold = min_conf * subtree_supp
        if top_k > 0:
            # get all freq
            all_freq = []
            for cat in constr_cnt:
                for c in constr_cnt[cat]:
                    freq = constr_cnt[cat][c]
                    if freq >= init_freq_threshold:
                        all_freq.append(freq)
            all_freq.sort(reverse=True)

            if top_k <= len(all_freq):
                return all_freq[top_k-1]
            elif len(all_freq)>0:   # otherwise return init_freq_threshold
                return all_freq[-1]
        
        return init_freq_threshold


    selected_constr = init_constr_record()
    freq_threshold = _get_freq_threshold()
    # no top_k, select all that meet the min_conf
    for cat in constr_cnt:
        for c in constr_cnt[cat]:
            freq = constr_cnt[cat][c]
            if freq >= freq_threshold:
                selected_constr[cat].add(c)
    return selected_constr



def update_rule(decoded_subtree, selected_constr):
    new_rule = {}
    # new_rule['encoded_subtree']=row['Subtree']
    # new_rule['constraints'] = {}
    for cat in selected_constr:
        if selected_constr[cat]:
            new_rule[cat] = list(selected_constr[cat])

    if not new_rule:
        return None

    # new_rule['subtree']=decoded_subtree
    return new_rule

def build(mine_result_path, label_path, save_path, min_conf=0, top_k=-1):
    # min_conf ([0,1] float): the minimum freq that the constr appears together with the subtree, for example: 80%
    # top_k: select top k most frequent cosntratints. if -1, select all that meet min_conf
    # mine_result_path: parsed mine result
    # save_path: not dir, actual file path
    print('Begin building the mapping...')
    min_conf = float(min_conf)
    top_k = int(top_k)
    mine_result_df = pd.read_csv(mine_result_path)
    label = pd.read_csv(label_path)
    rule = {}
    empty_rule = []
    for index, row in mine_result_df.iterrows():  # for each frequent subtree
        # print(index)
        # all constr(and freq) appears together with this subtree 
        # of format: {'dtype': {'constr1': freq1}, 'structure': ...}
        all_constr = init_constr_count()    
        unique_sent_idx = [int(x) for x in row['Unique_Sent_IDX'].split()]    # list of ints
        decoded_subtree = row['Decoded_Subtree']
        subtree_supp = int(row['Frequency'])
        assert int(subtree_supp) == len(unique_sent_idx)
        for sidx in unique_sent_idx:
            # for each tree the subtree comes from
            label_row = label.iloc[sidx]
            constr_row = parse_constr(label_row, decoded_subtree, filter_by_anno=True)
            all_constr = update_constr(all_constr, constr_row)
            
        
        selected_constr = select_constr(all_constr, subtree_supp, min_conf, top_k)
        
        new_rule = update_rule(decoded_subtree, selected_constr)
        if new_rule:
            rule[decoded_subtree] = new_rule
            # rule.append(new_rule)
        else:       # the subtree is not corelated with a constr
            empty_rule.append(decoded_subtree)  

    # save_yaml(os.path.join(save_path, 'subtree_rule.yaml'), rule)
    save_yaml(save_path, rule)
    # save_yaml(os.path.join(save_path, 'subtree_without_constr.yaml'), empty_rule)
    print('%s subtree mined in total, %s subtree rule, %s subtree without constr' %(len(mine_result_df), len(rule), len(empty_rule)))


if __name__ == "__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument('mine_result_path')
    parser.add_argument('label_path')
    parser.add_argument('save_path')
    parser.add_argument('--min_conf', default=0.8)
    parser.add_argument('--top_k', default=-1)
    
    

    args = parser.parse_args()
    mine_result_path = args.mine_result_path
    label_path = args.label_path
    save_path = args.save_path
    min_conf = args.min_conf
    top_k = args.top_k
    build(mine_result_path, label_path, save_path, min_conf, top_k)

# python train.py ./mining_data/tf/parsed_result.csv ./sample/tf_label.csv ./mining_data/tf/subtree_rule.yaml --min_conf=  --top_k=

# main('./tree_data/parsed_result.csv', './sample/tf_label.csv', './tree_data/subtree_rule.yaml',min_freq=0.8, top_k=-1)
# 302 subtree mined in total, 224 subtree rule, 78 subtree without constr
