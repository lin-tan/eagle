from util import *
from shutil import copyfile
import pandas as pd


# def main(rule_path1, rule_path2, save_to):
#     def merge_rules(r1, r2):
#         ret = r1.copy()
#         for cat in r2:
#             if cat in r1:
#                 ret[cat] = list(set(r1[cat]+r2[cat]))
#             else:
#                 ret[cat] = r2[cat]
#         return ret
    
#     rule1 = read_yaml(rule_path1)
#     rule2 = read_yaml(rule_path2)
#     all_rule = rule1.copy()
#     for subtree in rule2:
#         if subtree in rule1:
#             all_rule[subtree] = merge_rules(rule1[subtree], rule2[subtree])
#         else:
#             all_rule[subtree] = rule2[subtree]

#     print('combine {} and {} to form {} rules'.format(len(list(rule1.keys())), len(list(rule2.keys())), len(list(all_rule.keys()))))
#     save_yaml(save_to, all_rule)

# # main('./mining_data/tf/subtree_rule.yaml', './mining_data/pt/subtree_rule.yaml', './mining_data/general/tf_pt_rule.yaml')
# # main('./mining_data/tf/subtree_rule.yaml', './mining_data/mx/subtree_rule.yaml', './mining_data/general/tf_mx_rule.yaml')
# main('./mining_data/pt/subtree_rule.yaml', './mining_data/mx/subtree_rule.yaml', './mining_data/general/pt_mx_rule.yaml')




# all_cat = ['dtype', 'structure', 'tensor_t','range', 'shape', 'ndim', 'enum']
# def main(src_folder, dest_folder, save_to):
#     del_file(save_to)
#     src_files = get_file_list(src_folder)
#     dest_files = get_file_list(dest_folder)
#     for df in dest_files:
#         if df not in src_files:
#             print('new  '+ df)
#             copyfile(os.path.join(dest_folder, df), os.path.join(save_to, df))
#         else:
#             src_data = read_yaml(os.path.join(src_folder, df))
#             dest_data = read_yaml(os.path.join(dest_folder, df))
#             cp = False
#             for arg in dest_data['constraints']:
#                 for cat in all_cat:
#                     if cat in dest_data['constraints'][arg] and cat in src_data['constraints'][arg]:
#                         if set(dest_data['constraints'][arg][cat]) == set(src_data['constraints'][arg][cat]):
#                             pass
#                         else:
#                             print('{} - {} - {}: from {} to {}'.format(df, arg, cat, str(src_data['constraints'][arg][cat]), str(dest_data['constraints'][arg][cat])))
#                             cp = True
#                     elif cat not in dest_data['constraints'][arg] and  cat not in src_data['constraints'][arg]:
#                         pass
#                     elif cat in dest_data['constraints'][arg] and  cat not in src_data['constraints'][arg]:
#                         print('{} - {} - {}: from None to {}'.format(df, arg, cat,  str(dest_data['constraints'][arg][cat])))
#                         # print('warning '+ df + '  '+ arg)
#                         cp = True
#                     else:
#                         print('{} - {} - {}: from {} to None'.format(df, arg, cat, str(src_data['constraints'][arg][cat])))
#                         cp=True
#             if cp:
#                 copyfile(os.path.join(dest_folder, df), os.path.join(save_to, df))

# main('./constr/tf1/success/', './constr/tf/success/', './constr/tf/fixformat/')

# def main(csv_path, excluding_list, save_to):
#     df = pd.read_csv(csv_path)
#     ex_list = read_file(excluding_list)
#     ex_list = [x.replace('\n', '') for x in ex_list]
#     ex_list = [x.replace('.yaml', '').lower() for x in ex_list]
#     # print(ex_list)
#     print(len(ex_list))
#     ex_list = set(ex_list)
#     df = df.loc[~df['API'].str.lower().isin(ex_list)]
#     # print(df)
#     df.to_csv(save_to, index=False)

# main('./tmp/tf7eo.csv', './tmp/rerun_tf2', './tmp/tf7eo2.csv')
# main('./tmp/tf7ee.csv', './tmp/rerun_tf2', './tmp/tf7ee2.csv')
# main('./tmp/tf7-2eo.csv', './tmp/rerun_tf2', './tmp/tf7-2eo2.csv')
# main('./tmp/tf7-2ee.csv', './tmp/rerun_tf2', './tmp/tf7-2ee2.csv')

# def main(eval_list_path):
#     eval_list = read_yaml(eval_list_path)
#     cnt = 0
#     for api in eval_list:
#         cnt += len(eval_list[api])
#     print(cnt)

# main('./eval/mx/sample_list')


# group = {
#     'dtype': ['dtype'],
#     'structure': ['tensor_t', 'structure'],
#     'shape': ['shape', 'ndim'],
#     'validvalue': ['enum', 'range']
# }
# target = ['dtype', 'structure', 'tensor_t', 'shape', 'ndim', 'enum', 'range']

# def main(eval_folder):
#     eval_file = get_file_list(eval_folder)
#     num_arg = 0
#     num_arg_constr = 0
#     num_constr = 0
#     for ef in eval_file:
#         if ef=='sample_list':
#             continue
#         data = read_yaml(os.path.join(eval_folder, ef))
#         for arg in data['constraints']:
#             num_arg +=1 
#             for k in data['constraints'][arg]:
#                 if k in target:
#                     num_arg_constr += 1
#                     break
#             for g in group:
#                 for subcat in group[g]:
#                     if subcat in data['constraints'][arg]:
#                         num_constr+=1
#                         break
#     print(num_arg)
#     print(num_arg_constr)
#     print(num_constr)
# main('./eval/mx/')



# main('./tmp/pt_bl.csv', './discard/pt_discard_bl', './tmp/pt_bl2.csv')
# main('./tmp/mx_bl.csv', './discard/mx_discard_bl', './tmp/mx_bl2.csv')

# def main(csv_path, excluding_list, save_to):

# def cp_file(log, constr_folder, dest):
#     file_list = read_file(log)
#     file_list = [x.replace('\n', '') for x in file_list]
#     print(len(file_list))
#     for f in get_file_list(constr_folder):
#         if f not in file_list:
#             copyfile(os.path.join(constr_folder, f), os.path.join(dest, f))

# cp_file('./tmplog', './constr/mx/mx7-2eo/', './constr/mx/mx7-3eo/')
# def find_subtree(subtree_path, keywords):
#     rule=read_yaml(subtree_path)
#     for subtree in rule:
#         words = set(subtree.split())
#         # if it containts all keywords
#         ifprint = True
#         for kw in keywords:
#             if kw not in words:
#                 ifprint=False
#                 break
#         if ifprint:
#             print(subtree)
    
# # find_subtree('./mining_data/tf/subtree_rule.yaml', ['same', 'type', 'as'])        
# find_subtree('./mining_data/mx/subtree_rule.yaml', ['number', 'of' ])        
# find_subtree('./mining_data/pt/subtree_rule.yaml', ['positive', 'support' ])    
# find_subtree('./mining_data/tf/subtree_rule.yaml', ['same', 'type', 'as'])           
# def main(csv_path, save_path):
#     df = pd.read_csv(csv_path)
#     for index, row in df.iterrows():
#         param = row['Arg']
#         descp = row['Descp']
#         normalized_descp = row['Normalized_descp']
#         if len(normalized_descp.strip().split())==1:
#             df.at[index, 'Normalized_descp'] = 'ONE_WORD '+normalized_descp
#         # if 'THIS_PARAM' in normalized_descp:
#         #     df.at[index, 'Normalized_descp'] = normalized_descp.replace('THIS_PARAM', param)
#     df.to_csv(save_path)

# # main('./sample/tf_label.csv', './sample/tf_label2.csv')
# main('./sample/pt_label.csv', './sample/pt_label.csv')
# main('./sample/mx_label.csv', './sample/mx_label.csv')

# def main(subtree_rule_path):
#     rules = read_yaml(subtree_rule_path)
#     max_len = 0
#     for r in rules:
#         curr_len =  len([x for x in r.split() if x != '-1'])
#         max_len =  max(max_len,curr_len)
#         if curr_len>10:
#             print(r)
#     print('max len: %s' % max_len)
#     print('max iter: %s' % (max_len-1))

# # max_len: pt: 3. mx: 7, tf: 12
# # max_iter: pt: 2. mx: 6, tf: 11
# main('./mining_data/tf/subtree_rule.yaml')    
# main('./mining_data/pt/subtree_rule.yaml')    
# main('./mining_data/mx/subtree_rule.yaml')  
# 
# 
# 
# def main(sample_list1, sample_list2, save_path):
#     sample1 = read_yaml(sample_list1)
#     sample2 = read_yaml(sample_list2)     
#     sample = sample1 + sample2
#     save_yaml(save_path, sample)

# # main('./sample/tf_list_batch1', './sample/tf_list_batch2', './sample/tf_list')
# # main('./sample/pt_list_batch1', './sample/pt_list_batch2', './sample/pt_list')
# main('./sample/mx_list_batch1', './sample/mx_list_batch2', './sample/mx_list')



# from util import *
# import os
# def main(constr_folder, ):
#     file_list = get_file_list(constr_folder)
#     doc_dtype = []
#     for fpath in file_list:
#         data = read_yaml(os.path.join(constr_folder, fpath))
#         for arg in data['constraints']:
#             if 'doc_dtype' in data['constraints'][arg]:
#                 doc_dtype += data['constraints'][arg]['doc_dtype']
#     prettyprint(doc_dtype)

# def prettyprint(l):
#     for x in l:
#         print(x)


# main('../collect_doc/pytorch/pt15_all_src/')
# main('../collect_doc/mxnet/mx16_all_src/')