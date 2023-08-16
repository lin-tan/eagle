import os
import yaml

def diff(l1, l2):
    ret = []
    for ll1 in l1:
        if ll1 not in l2:
            ret.append(ll1)
    return ret

def print_list(l):
    for ll in l:
        print(ll)
  


yaml_folder = './doc2.1_parsed/'
running_stat_path = './stat/running_stat'
uniqueurl_path = './stat/tf2.1_py_uniqueurl.yaml'
title_cnt_path = './stat/tf2.1_py_fromweb.yaml'

with open(title_cnt_path) as yml_file:
    title_cnt = yaml.load(yml_file, Loader=yaml.FullLoader)
print('Total API: {}'.format(len(list(title_cnt.keys()))))

with open(uniqueurl_path) as yml_file:
    uniqueurl = yaml.load(yml_file, Loader=yaml.FullLoader)
print('Total uniqu url: {}'.format(len(list(uniqueurl.keys()))))


files = []
for _,_, filenames in os.walk(yaml_folder):
    files.extend(filenames)
    break

if '.DS_Store' in files:
    files.remove('.DS_Store')

print("Collected File: {}".format(len(files)))


# # tmp: check which files are overwritten
# files2 = []
# for _,_, filenames in os.walk('../../doc2.1_parsed/'):
#     files2.extend(filenames)
#     break

# if '.DS_Store' in files2:
#     files2.remove('.DS_Store')

# for f in files:
#     if f not in files2:
#         print(f)

############

with open(running_stat_path) as yml_file:
    running_stat = yaml.load(yml_file, Loader=yaml.FullLoader)



for k in running_stat:
    if isinstance(running_stat[k], list):
        print('{}: {}'.format(k, len(running_stat[k])))

# count number of word
word_cnt = 0
for url in running_stat['word_cnt']:
    if 'tf/compat/v1/' in url:
        continue
    word_cnt+=running_stat['word_cnt'][url]
print('Total word (filtered tf v1): '+str(word_cnt))



# with open('./stat/old_except_url') as yml_file:
#     old_running_stat = yaml.load(yml_file, Loader=yaml.FullLoader)


# print(len(diff(running_stat['collected'], old_running_stat['collected'])))
# print_list(diff(running_stat['collected'], old_running_stat['collected']))
#print(len(diff(old_running_stat['collected'], running_stat['collected'])))



# print('before not collected, now has arg warnning:')
# for url in running_stat['warning_arg']:
#     if url not in old_running_stat['collected']:
#         print(url)