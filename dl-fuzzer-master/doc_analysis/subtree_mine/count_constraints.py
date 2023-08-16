import yaml
import os
from util import *
import sys


def cnt_total(cnt_dict):
    ret = 0
    for k in cnt_dict:
        ret+=cnt_dict[k]
    return ret

def main(constraint_folder):

    config_foler = constraint_folder
    # print(config_foler)
    min= 10000
    max=0
    max_file = None
    avg = 0

    constraint_cnt = {}
    grouped_constraint_cnt = {}
    group = {
        'dtype': ['dtype'],
        'structure': ['tensor_t', 'structure'],
        'shape': ['shape', 'ndim'],
        'validvalue': ['enum', 'range']
    }
    target = []
    for g in group:
        grouped_constraint_cnt[g] = 0
        for cat in group[g]:
            constraint_cnt[cat] = 0
            target.append(cat)
    constraint_cnt['total'] = 0
    grouped_constraint_cnt['total'] = 0


    # read files
    files = get_file_list(config_foler)
    # pat_files = get_file_list(pat_folder)


    for f in files:
        con_cnt = 0
        info = read_yaml(os.path.join(config_foler, f))

        for arg in info['constraints']:
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
    
            
                        
    print('Number of files: '+str(len(files)))
    # print('Pattern Count:')
    # print(pat_cnt)
    print("Constraint Count:")
    print(constraint_cnt)
    print('Grouped result:')
    print(grouped_constraint_cnt)
    print('Constraints min: {} max: {} ({}) avg: {}'.format(min, max, max_file, grouped_constraint_cnt['total']/len(files)))



if __name__ == "__main__":
    # pat_src = {
    #     # 'tf': './tf/patterns/',
    #     # 'pytorch': './pytorch/patterns/',
    #     # 'mxnet': './mxnet/patterns/'
    #     'sklearn_tf': './sklearn/patterns_tf/',
    #     'sklearn_pt': './sklearn/patterns_pt/',
    #     'sklearn_mx': './sklearn/patterns_mx/',
    #     'sklearn_all': './sklearn/patterns_all/',
    # }

    constraint_src = {
        # 'tf': './tf/tf21_all/changed/',
        # 'pytorch': './pytorch/pt15_all/',
        # 'mxnet': './mxnet/mx16_all/'
        # 'sklearn_tf': './sklearn/constr_tf/changed/',
        # 'sklearn_pt': './sklearn/constr_pt/changed/',
        # 'sklearn_mx': './sklearn/constr_mx/changed/',
        # 'sklearn_all': './sklearn/constr_all/changed/',
        'tf': './constr/tf/success',
        'pt': './constr/pt/success',
        'mx': './constr/mx/success',
        'tf_general': './constr/pt_mx_on_tf/success',
        'pt_general': './constr/tf_mx_on_pt/success',
        'mx_general': './constr/tf_pt_on_mx/success',
        'sklearn_general': './generality_analysis/constr/all_on_sklearn/success',
        'tf_ablation': './rebuttal_ablation/constr/tf/success',
        'pt_ablation': './rebuttal_ablation/constr/pt/success',
        'mx_ablation': './rebuttal_ablation/constr/mx/success',
    }
    # for tf: python count_constraints.py ./tf/patterns/ ./tf/constraint_2/
    # for pytorch:  python count_constraints.py ./pytorch/patterns/ ./pytorch/constraint_1/
    # for mxnet: python count_constraints.py ./mxnet/patterns/ ./mxnet/constraint_1/

    framework = sys.argv[1]
    main(constraint_src[framework])




# (docter_fuzz) ➜  subtree_mine git:(master) ✗ python count_constraints.py tf
# Number of files: 917
# Constraint Count:
# {'dtype': 2456, 'tensor_t': 1028, 'structure': 349, 'shape': 228, 'ndim': 1911, 'enum': 256, 'range': 311, 'total': 6539}
# Grouped result:
# {'dtype': 2456, 'structure': 1251, 'shape': 1911, 'validvalue': 552, 'total': 6170}
# Constraints min: 1 max: 50 (tf.keras.layers.lstm.yaml) avg: 6.7284623773173395
# (docter_fuzz) ➜  subtree_mine git:(master) ✗ python count_constraints.py pt
# Number of files: 498
# Constraint Count:
# {'dtype': 1163, 'tensor_t': 719, 'structure': 248, 'shape': 25, 'ndim': 860, 'enum': 78, 'range': 240, 'total': 3333}
# Grouped result:
# {'dtype': 1163, 'structure': 885, 'shape': 860, 'validvalue': 296, 'total': 3204}
# Constraints min: 1 max: 33 (torch.onnx.export.yaml) avg: 6.433734939759036
# (docter_fuzz) ➜  subtree_mine git:(master) ✗ python count_constraints.py mx
# Number of files: 1006
# Constraint Count:
# {'dtype': 2272, 'tensor_t': 55, 'structure': 2397, 'shape': 0, 'ndim': 1699, 'enum': 155, 'range': 337, 'total': 6915}
# Grouped result:
# {'dtype': 2272, 'structure': 2413, 'shape': 1699, 'validvalue': 489, 'total': 6873}
# Constraints min: 1 max: 111 (mxnet.io.imagerecorditer.yaml) avg: 6.832007952286283



# python count_constraints.py sklearn_general
# Number of files: 223
# Constraint Count:
# {'dtype': 761, 'tensor_t': 0, 'structure': 406, 'shape': 183, 'ndim': 862, 'enum': 103, 'range': 180, 'total': 2495}
# Grouped result:
# {'dtype': 761, 'structure': 406, 'shape': 862, 'validvalue': 280, 'total': 2309}
# Constraints min: 1 max: 47 (sklearn.decomposition.dict_learning_online.yaml) avg: 10.354260089686099
