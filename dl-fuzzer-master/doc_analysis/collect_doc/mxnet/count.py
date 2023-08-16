import os
import yaml
import sys
sys.path.insert(0,'..')
from parse_utils import *


# count total number of class and func
module_stat = read_yaml('./stat/module_stat.yaml')

num_class = 0
num_func = 0
for url in module_stat:
    num_class += module_stat[url]['num_class']
    num_func += module_stat[url]['num_func']

print('#function detected: '+str(num_func))
print('#class detected: '+str(num_class))


# how many actually saved

yaml_folder = './doc1.6_parsed'

file_collected = get_file_list(yaml_folder)
print('Collected(saved) File: '+ str(len(file_collected)))

print('\nStat in running_stat.yaml')
running_stat = read_yaml('./stat/running_stat.yaml')
for cat in running_stat:
    if isinstance(running_stat[cat], list):
        print('{}: {}'.format(cat, len(running_stat[cat])))
    
print('collected: '+str(len(running_stat['collected'])))
# count function with multiple version
# mul_cnt = 0
# for mul in running_stat['multi_func']:
#     mul_cnt+=running_stat['multi_func'][mul]
# print('{} function with {} unique func name'.format(mul_cnt, len(list(running_stat['multi_func'].keys()))))


# count number of word
word_cnt = 0
for url in running_stat['word_cnt']:
    word_cnt+=running_stat['word_cnt'][url]
print('Total word: '+str(word_cnt))