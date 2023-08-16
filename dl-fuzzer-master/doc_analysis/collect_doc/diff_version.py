# investigate difference of document between two versions
from parse_utils import *
import sys
from difflib import SequenceMatcher


def intersect(l1, l2):
    return list(set(l1) & set(l2))

def union(l1, l2):
    return list(set(l1+l2))

def minus(l1, l2):
    # return l1-l2
    return [x for x in l1 if x not in l2]

def compare(dir1, dir2):
    dirname1 = dir1.split('/')[-1]
    dirname2 = dir2.split('/')[-1]
    running_stat = {
        'uniqu_'+dirname1: [],
        'uniqu_'+dirname2: [],
        'param_diff': [],
        'descp_diff': []
    }
    file_list1 = get_file_list(dir1)
    file_list2 = get_file_list(dir2)

    common_files = intersect(file_list1, file_list2) 
    running_stat['uniqu_'+dirname1] = [x for x in file_list1 if x not in common_files]
    running_stat['uniqu_'+dirname2] = [x for x in file_list2 if x not in common_files]

    similar_descp = [['API', 'Param', 'ratio', dirname1, dirname2]]
    diff_descp = [['API', 'Param', 'ratio', dirname1, dirname2]]

    num_api_diff_param = 0
    num_diff_param = 0
    num_same_doc = 0
    total_num_param = 0
    for cf in common_files:
        doc_same = True
        data1 = read_yaml(dir1+'/'+cf)
        data2 = read_yaml(dir2+'/'+cf)

        param_list1 = data1['inputs']['optional'] + data1['inputs']['required']
        param_list2 = data2['inputs']['optional'] + data2['inputs']['required']

        all_param = union(param_list1, param_list2)
        total_num_param += len(all_param)

        if sorted(param_list1) != sorted(param_list2):
            same_param_list = intersect(param_list1, param_list2)
            diff_param_list = minus(all_param, same_param_list)
            
            running_stat['param_diff'].append({'filename': cf, 'param': diff_param_list})

            num_api_diff_param += 1
            num_diff_param += len(diff_param_list)
        else:
            same_param_list = param_list1

        for param in same_param_list:
            ori_descp1 = data1['constraints'][param]['descp']
            ori_descp2 = data2['constraints'][param]['descp']

            descp1 = ori_descp1.lower().replace('`', '')
            descp2 = ori_descp2.lower().replace('`', '')

            #if descp1.lower()!= descp2.lower(): 
            ratio = SequenceMatcher(None, descp1, descp2).ratio()
            if ratio<0.9:
                running_stat['descp_diff'].append({'filename': cf, 'param': param})
                diff_descp.append([cf, param, ratio, ori_descp1, ori_descp2])
                doc_same=False

            elif ratio!=1:
                similar_descp.append([cf, param, ratio, ori_descp1, ori_descp2])

        if doc_same:
            num_same_doc+=1

    write_csv('./diff_version_results/{}_{}_similar_descp.csv'.format(dirname1, dirname2), similar_descp)
    write_csv('./diff_version_results/{}_{}_diff_descp.csv'.format(dirname1, dirname2), diff_descp)
    save_yaml('./diff_version_results/{}_{}_stat.yaml'.format(dirname1, dirname2), running_stat)


    print("Results for {} vs {}".format(dirname1, dirname2))
    print('unique in {}: {}; unique in {}: {}'.format(dirname1, len(running_stat['uniqu_'+dirname1]), dirname2, len(running_stat['uniqu_'+dirname2])))
    print('Out of {} commen APIs, {} APIs have param difference on {}/{} parameters'.format(len(common_files), num_api_diff_param, num_diff_param, total_num_param))
    print('Out of {} commen APIs, {} doc changed'.format(len(common_files), len(common_files)-num_same_doc))


'''

sequence match threshold = 0.9

Results for doc2.1_parsed_rmv1 vs tfdoc2.2
unique in doc2.1_parsed_rmv1: 48; unique in tfdoc2.2: 1381
Out of 901 commen APIs, 9 APIs have param difference on 9/3122 parameters
Out of 901 commen APIs, 66 doc changed


Results for tfdoc2.2 vs tfdoc2.3
unique in tfdoc2.2: 17; unique in tfdoc2.3: 104
Out of 2265 commen APIs, 33 APIs have param difference on 37/10223 parameters
Out of 2265 commen APIs, 89 doc changed

Results for mx1.6_parsed vs mx1.7_parsed
unique in mx1.6_parsed: 2; unique in mx1.7_parsed: 15
Out of 957 commen APIs, 11 APIs have param difference on 13/5929 parameters
Out of 957 commen APIs, 5 doc changed


Results for pt1.5_parsed vs pt1.6_parsed
unique in pt1.5_parsed: 10; unique in pt1.6_parsed: 45
Out of 405 commen APIs, 16 APIs have param difference on 20/1444 parameters
Out of 405 commen APIs, 9 doc changed

Results for pt1.6_parsed vs pt1.7_parsed
unique in pt1.6_parsed: 25; unique in pt1.7_parsed: 51
Out of 425 commen APIs, 9 APIs have param difference on 11/1476 parameters
Out of 425 commen APIs, 28 doc changed

'''






if __name__ == "__main__":
    # usage: python diff_version.py ./pytorch/pt1.5_parsed  ./pytorch/pt1.6_parsed
    dir1 = sys.argv[1]
    dir2 = sys.argv[2]
    compare(dir1, dir2)