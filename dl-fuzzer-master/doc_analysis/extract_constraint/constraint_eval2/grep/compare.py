import sys
sys.path.insert(0,'../..')
import yaml
import os
from extract_utils import *
import argparse


def cnt_total(cnt_dict):
    ret = 0
    for k in cnt_dict:
        ret+=cnt_dict[k]
    return ret

def run_cnt(dir, files):
    target = ['dtype','structure','shape','ndim','enum','range']

    constraint_cnt = {}
    grouped_constraint_cnt = {}
    group = {
        'prim_dtype': ['dtype'],
        # 'nonprim_dtype': ['tensor_t', 'structure'],
        'nonprim_dtype': ['structure'],
        'shape': ['shape', 'ndim'],
        'validvalue': ['enum', 'range']
    }

    # init
    for t in target:
        constraint_cnt[t] = 0
    for g in group:
        grouped_constraint_cnt[g] = 0
    constraint_cnt['total'] = 0
    grouped_constraint_cnt['total'] = 0


    for f in files:
        info = read_yaml(dir+f)

        for arg in info['constraints']:
            for constr_cat in info['constraints'][arg]:
                if constr_cat in target:
                    constraint_cnt[constr_cat]+=1
                    #constr_cnt+=1
            for g in group:
                for subcat in group[g]:
                    if subcat in info['constraints'][arg]:
                        grouped_constraint_cnt[g] +=1
                        break

    constraint_cnt['total'] = cnt_total(constraint_cnt)
    grouped_constraint_cnt['total'] =cnt_total(grouped_constraint_cnt)

    return constraint_cnt, grouped_constraint_cnt


def cnt_constraint(constraint_folder):
    config_foler = constraint_folder
    files = get_file_list(config_foler)

    constraint_cnt, grouped_constraint_cnt = run_cnt(config_foler, files)

    print('Number of files: '+str(len(files)))
    # print("counting:")
    # print(constraint_cnt)
    print('Grouped result:')
    print(grouped_constraint_cnt)


def compare_constraint(constr1, constr2, cat):
    def _prepare_constr(constr):
        ret = set()
        for c in constr:
            tmp = re.sub(r'(.*)\(.*\)', r'\1', c)
            if tmp == 'dict':
                continue
            ret.add(tmp)
        return list(ret)


    if cat!='nonprim_dtype':
        if constr1==constr2:
            return True
        else:
            return False
    
    # for nonprim_dtype, list(int) = list
    constr1 = _prepare_constr(constr1)
    constr2 = _prepare_constr(constr2)

    if constr1==constr2:
        return True
    else:
        return False 
    

def compare(old, new, save=True):
    old_files = get_file_list(old)
    new_files = get_file_list(new)

    target = ['dtype','structure', 'shape','ndim','enum','range']
    group = {
        'prim_dtype': ['dtype'],
        # 'nonprim_dtype': ['tensor_t', 'structure'],
        'nonprim_dtype': [ 'structure'],
        'shape': ['shape', 'ndim'],
        'validvalue': ['enum', 'range']
    }

    csv_miss = [['File', 'Arg', 'Type', 'Constr', 'Descp']]
    csv_additional = [['File', 'Arg', 'Type', 'Constr', 'Descp']]
    csv_diff = [['File', 'Arg', 'Type', 'Constr_src', 'Constr_cmp', 'Descp']]
    # init diff
    diff_old = {}
    common = {}
    for cat in group:
        diff_old[cat] = 0
        common[cat] = 0

    def _get_constr(yamlfile, arg):
        constr = {}
        for cat in group:
            constr[cat] = []
            for subcat in group[cat]:
                constr[cat] += yamlfile['constraints'][arg].get(subcat, [])

            constr[cat] = sorted(constr[cat])
        return constr


    unique_old = []         # APIs with constraint extracted only in DocTer
    unique_new = []         # # APIs with constraint extracted only in grep
    eval_list = []
    for oldf in old_files:
        if oldf not in new_files:
            unique_old.append(oldf)
            continue
        oldyaml = read_yaml(old+oldf)
        newyaml = read_yaml(new+oldf)

        for arg in oldyaml['constraints']:
            oldconstr = _get_constr(oldyaml, arg)
            newconstr = _get_constr(newyaml, arg)
            for cat in group:
                if oldconstr[cat]:
                    if not compare_constraint(oldconstr[cat], newconstr[cat], cat):
                        diff_old[cat]+=1
                        eval_list.append([oldf, arg, cat])
                    else:    # if not empty and the same
                        common[cat]+=1

                if save and not compare_constraint(oldconstr[cat], newconstr[cat], cat) and cat in ['prim_dtype', 'nonprim_dtype']:
                    # print incorrectly extracted constraints
                    if newconstr[cat] and not oldconstr[cat]:
                        csv_additional.append([newyaml['title'], arg, cat, str(newconstr[cat]), oldyaml['constraints'][arg]['descp']])
                        #print(newyaml['title']+ '   '+oldyaml['constraints'][arg]['descp'])
                    
                    # print missing constraint
                    elif oldconstr[cat] and not newconstr[cat]:
                        csv_miss.append([newyaml['title'], arg, cat, str(oldconstr[cat]), oldyaml['constraints'][arg]['descp']])
                        #print(newyaml['title']+ '   '+oldyaml['constraints'][arg]['descp'])
                    
                    else:
                        csv_diff.append([newyaml['title'], arg, cat, str(oldconstr[cat]), str(newconstr[cat]), oldyaml['constraints'][arg]['descp']])

    


    for newf in new_files:
        if newf not in old_files:
            unique_new.append(newf)


    _, unique_old_cnt = run_cnt(old, unique_old)
    _, unique_new_cnt = run_cnt(new, unique_new)

    for cat in group:
        #diff[cat]+=unique_old_cnt[cat]
        diff_old[cat]+=unique_old_cnt[cat]

    for f in unique_old:
        info = read_yaml(old+f)
        for arg in info['constraints']:
            constr = _get_constr(info, arg)
            for cat in group: 
                if constr[cat] and cat in ['prim_dtype', 'nonprim_dtype']:
                    csv_miss.append([info['title'], arg, cat, str(constr[cat]), info['constraints'][arg]['descp']])
    # prepare eval_list
    for f in unique_new:
        info = read_yaml(new+f)
        for arg in info['constraints']:
            constr = _get_constr(info, arg)
            for cat in group:
                if constr[cat] and cat in ['prim_dtype', 'nonprim_dtype']:
                    csv_additional.append([info['title'], arg, cat, str(constr[cat]), info['constraints'][arg]['descp']])
                for subcat in group[cat]:
                    if subcat in info['constraints'][arg]:
                        eval_list.append([f, arg, cat])
                        break

 

    if save:
        write_csv('./comp/miss.csv',csv_miss)
        write_csv('./comp/additional.csv',csv_additional)
        write_csv('./comp/diff.csv',csv_diff)

    diff_old['total'] = cnt_total(diff_old)
    print("compare results (diff):")
    print(diff_old)

    common['total'] = cnt_total(common)
    print('Common:')
    print(common)

    return eval_list




# if __name__ == "__main__":
    # compare the constraints between grepping and docter
    # constraint_src = {
    #     'tf': './tf/changed/',
    #     'pytorch': './pytorch/changed/',
    #     'mxnet': './mxnet/changed/'
    # }

    # old_constraint_src = {
    #     'tf': '../../tf/tf21_all/changed/',
    #     'pytorch': '../../pytorch/pt15_all/',
    #     'mxnet': '../../mxnet/mx16_all/'
    # }
    
    # framework = sys.argv[1]

    # print('Counting results of DocTer')
    # cnt_constraint(old_constraint_src[framework])

    # print()
    # print('Counting results of grep')
    # cnt_constraint(constraint_src[framework])

    # print()

    # eval_list = compare(old_constraint_src[framework], constraint_src[framework])
    #save_yaml('./{}_evallist'.format(framework), eval_list)


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument('src_path')
    parser.add_argument('compare_path')
    args = parser.parse_args()


    print('Counting results of DocTer')
    cnt_constraint(args.src_path)

    print()
    print('Counting results of grep')
    cnt_constraint(args.compare_path)

    print()

    eval_list = compare(args.src_path, args.compare_path, save=True)
        