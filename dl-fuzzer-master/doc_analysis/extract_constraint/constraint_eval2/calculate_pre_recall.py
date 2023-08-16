import sys
sys.path.insert(0,'..')

from extract_utils import *
import random 
import pandas as pd


def check_nan(val):
    if pd.isna(val):
        return 0
    else:
        return int(val)

def count_sum(d, count1=False):
    # input dict
    ret = 0
    for k in d:
        if count1:
            ret +=d[k].count(1)
        else:   
            ret +=d[k]
    return ret

def print_dict(d, title):
    print(title)
    for k in d:
        print('{}: {}'.format(k, d[k]))
    print()

def divide(a,b):
    # a/b
    if b==0:
        return 0
    else:
        return a/b
def main(path):
    files = get_file_list(path)
    # all_attr = ['dtype', 'structure', 'shape', 'validvalue']
    all_attr = ['prim_dtype', 'nonprim_dtype', 'shape', 'validvalue']
    in_doc = {}
    extracted = {}
    success_cnt = {}  # number of success constraint, not parameter

    for aa in all_attr:
        in_doc[aa] = []
        extracted[aa] = []
        success_cnt[aa] = 0
    
    constraint_manually_found = 0
    all_correct_cnt = 0
    num_param_with_contr = 0
    
    for f in files:
        all_correct=True  # if all constraint is correct
        with_constr = False


        try:

            df = pd.read_csv(path+f)
        except:
            print(f)
            return
        for index, row in df.iterrows():
            attr  = row['attribute']
            ind = check_nan(row['in_doc'])
            ex = check_nan(row['extracted'])

            if attr not in all_attr and (ind!=0 or ex!=0):
                print(f)
                return

            if ind==1 or ex==1: 
                in_doc[attr].append(ind)
                extracted[attr].append(ex)
                with_constr=True

            if ind==1 and ex==1: 
                success_cnt[attr]+=1

            if ind==1:
                constraint_manually_found+=1

            if ind!=ex:
                all_correct = False



        if with_constr:
            num_param_with_contr+=1
            if all_correct:
                all_correct_cnt+=1



        




    # precision = success_cnt/extracted.count(1)
    # recall = success_cnt/in_doc.count(1)
    precision = {}
    recall = {}
    for aa in all_attr:
        if len(in_doc[aa])!=len(extracted[aa]):
            print('error')
            return
        precision[aa] = divide(success_cnt[aa], extracted[aa].count(1))
        recall[aa] = divide(success_cnt[aa], in_doc[aa].count(1))

    precision['total'] = divide(count_sum(success_cnt), count_sum(extracted, count1=True))
    recall['total'] = divide(count_sum(success_cnt), count_sum(in_doc, count1=True))

    
    accuracy = all_correct_cnt/num_param_with_contr
    print('# arguments: '+str(len(files)))
    print('# argument with constraints: '+str(num_param_with_contr))
    print('# constraint manually found: '+ str(constraint_manually_found)) 
    print('Accu overall: '+ str(accuracy)) 
    print()
    # print('Precision: '+str(precision))
    # print('Recall: '+str(recall))
    print_dict(precision, 'Precision')
    print_dict(recall, 'Recall')


            


    
                
if __name__ == "__main__":

    path = sys.argv[1]

    main(path)