import yaml
import os
from extract_utils import *
import sys


def cnt_total(cnt_dict):
    ret = 0
    for k in cnt_dict:
        ret+=cnt_dict[k]
    return ret

def main(pat_folder, constraint_folder):

    target_file = pat_folder+'targets.yml'
    # config_foler = constraint_folder+ 'changed/'
    config_foler = constraint_folder
    print(config_foler)
    min= 10000
    max=0
    max_file = None
    avg = 0

    target = read_yaml(target_file)

    # init result
    # constraint_cnt = {}
    constraint_cnt = {}
    pat_cnt = {}
    grouped_constraint_cnt = {}
    grouped_pat_cnt = {}
    group = {
        'prim_dtype': ['dtype'],
        'nonprim_dtype': ['tensor_t', 'structure'],
        'shape': ['shape', 'ndim'],
        'validvalue': ['enum', 'range']
    }
    for t in target:
        # constraint_cnt[t] = 0
        constraint_cnt[t] = 0
        pat_cnt[t] = 0

    for g in group:
        grouped_constraint_cnt[g] = 0
        grouped_pat_cnt[g] = 0

    pat_cnt['total'] = 0
    constraint_cnt['total'] = 0
    grouped_constraint_cnt['total'] = 0
    grouped_pat_cnt['total'] = 0

    # read files
    files = get_file_list(config_foler)
    pat_files = get_file_list(pat_folder)

    # count patterns
    for pf_name in pat_files:
        pf = read_yaml(pat_folder+pf_name)
        if pf and 'target' in pf and pf['target'] in target:
            pat_cnt[pf['target']] += len(pf['pat'])

    pat_cnt['total'] = cnt_total(pat_cnt)

    for f in files:
        con_cnt = 0
        info = read_yaml(config_foler+f)

        for arg in info['constraints']:
            # if 'shape' in info['constraints'][arg] and 'ndim' not in info['constraints'][arg]:
            #     print(f+'  '+arg)
            for k in info['constraints'][arg]:
                if k in target:
                    constraint_cnt[k]+=1
                    #con_cnt+=1
            for g in group:
                for subcat in group[g]:
                    if subcat in info['constraints'][arg]:
                        grouped_constraint_cnt[g] +=1
                        con_cnt+=1
                        break

                
        if con_cnt<min:
            min=con_cnt
        if con_cnt>max:
            max = con_cnt
            max_file = f

    constraint_cnt['total'] = cnt_total(constraint_cnt)
    grouped_constraint_cnt['total'] =cnt_total(grouped_constraint_cnt)


    # merge count fot patterns
    for g in group:
        tmp_pat = 0
        for cat in group[g]:
            if cat in target:
                tmp_pat += pat_cnt[cat]

        grouped_pat_cnt[g] = tmp_pat

            


        
                        
    print('Number of files: '+str(len(files)))
    print('Pattern Count:')
    print(pat_cnt)
    print("Constraint Count:")
    print(constraint_cnt)
    print('Grouped result:')
    print(grouped_pat_cnt)
    print(grouped_constraint_cnt)
    print('Constraints min: {} max: {} ({}) avg: {}'.format(min, max, max_file, grouped_constraint_cnt['total']/len(files)))



if __name__ == "__main__":
    pat_src = {
        # 'tf': './tf/patterns/',
        # 'pytorch': './pytorch/patterns/',
        # 'mxnet': './mxnet/patterns/'
        'sklearn_tf': './sklearn/patterns_tf/',
        'sklearn_pt': './sklearn/patterns_pt/',
        'sklearn_mx': './sklearn/patterns_mx/',
        'sklearn_all': './sklearn/patterns_all/',
    }

    constraint_src = {
        # 'tf': './tf/tf21_all/changed/',
        # 'pytorch': './pytorch/pt15_all/',
        # 'mxnet': './mxnet/mx16_all/'
        'sklearn_tf': './sklearn/constr_tf/changed/',
        'sklearn_pt': './sklearn/constr_pt/changed/',
        'sklearn_mx': './sklearn/constr_mx/changed/',
        'sklearn_all': './sklearn/constr_all/changed/',
    }
    # for tf: python count_constraints.py ./tf/patterns/ ./tf/constraint_2/
    # for pytorch:  python count_constraints.py ./pytorch/patterns/ ./pytorch/constraint_1/
    # for mxnet: python count_constraints.py ./mxnet/patterns/ ./mxnet/constraint_1/

    framework = sys.argv[1]
    main(pat_src[framework], constraint_src[framework])