import re
from utils import *
import yaml
import csv
from collections.abc import Iterable


# extract list of APIs which takes objects of other class as inputs.

stop_word = ['of', 'the', 'a', 'an', 'all', 'be', 'for', 'this', 'that', 'each', 'or', 'sampled', 'custom', 'true', 'predicted', 'use', 'optional']
pat = {
    '(?<!not\sa)(?<!not\san)\s([\d\w`\'\".]+)\s+\\bobjects*\\b': 1,
    '(([\d\w`\'\".]+)\s+or\s+([\d\w`\'\".]+))\s+\\bobjects*\\b': 1,
    '([\w\d.`\'\"]+)\s\\bclass\s\\b': 1, 
    '(?<!not\s)\b(a|an)\b\s+[`\'\"]([\w\d.]+)[`\'\"]': 2,
    '(?<!not\sa)(?<!not\san)\s([\d\w`\'\".]+)\s+\\binstances*\\b': 1,
    '(([\d\w`\'\".]+)\s+or\s+([\d\w`\'\".]+))\s+\\binstances*\\b': 1,
    'an\s+instance\s+of\s+([\d\w`\'\".]+)': 1
}


folder = './web_clean/'
save = './constraint_1/'

def parse_dtype(dt_str, stop_word = ['and', 'or'], min_len = 3):
    '''
    e.g. from `complex64`, or `complex128`. to [`complex64`, `complex128`]
    '''
    p = '[,`\'\"]'
    dt_p = re.sub(p,'!', dt_str)
    big_regex = re.compile(r'\b%s\b' % r'\b|\b'.join(map(re.escape, stop_word)))
    dt_p = big_regex.sub("!", dt_p)

    dt_s = dt_p.split('!')
    ret = []
    for dt in dt_s:
        tmp = dt.replace(' ', '')
        
        if len(tmp)<min_len or tmp.lower() in stop_word:
            continue
        ret.append(tmp)
    return ret
        
def check_dtype(dt_l, map):
    # dt_l is a list of dtype
    # check if they are in the list and map them to the standard name
    # e.g. string -> tf.string,  positive -> x (not a type)
    ret = []
    for dt in dt_l:
        if dt.lower() in map:
            pass
        else:
            ret.append(dt)
    return ret


# read files
files = []
for _,_, filenames in os.walk(folder):
    files.extend(filenames)
    break
if '.DS_Store' in files:
    files.remove('.DS_Store')


# open dt_map.yml
with open('./dtype_map.yml') as yml_file:
    dt_map = yaml.load(yml_file, Loader=yaml.FullLoader)

# open tensor_type_map.yml
with open('./tensor_type_map.yml') as yml_file:
    tensor_type_map = yaml.load(yml_file, Loader=yaml.FullLoader)

ret = []
unique_api = 0
for f in files[:]:
    with open(folder+f) as yml_file:
        info = yaml.load(yml_file, Loader=yaml.FullLoader)
        detected = False
        for arg in info['constraints']: 
            nv_final = []
            if info['constraints'][arg].get('dtype', '') == 'deprecated':
                continue
            descp = info['constraints'][arg]['descp']
            for p in pat:
                rslt = re.findall(r'{}'.format(p), descp.lower())

                if rslt:
                    for nv in rslt:
                        if isinstance(nv, str):
                            nv_it = nv
                        else:
                            nv_it = nv[pat[p]-1]  # findall
                        nv_ls = parse_dtype(nv_it,  stop_word =stop_word)
                        #print('after parse dtype '+ str(nv_ls))
                        nv_ret = check_dtype(nv_ls, dt_map)
                        nv_ret = check_dtype(nv_ret, tensor_type_map)
                        if len(nv_ret)>0:
                            nv_final+=nv_ret
                            detected = True

            if len(nv_final)>0:
                nv_final = list(set(nv_final))
                for nr in nv_final:
                    ret.append([info['target'], arg, nr, descp])
            
        if detected:
            unique_api += 1
            

with open('./calling_class_obj.csv', 'w', newline='') as csvfile:
    csv_writer = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    csv_writer.writerow(['API', 'arg' , 'obj', 'descp'])
    for r in ret:
        csv_writer.writerow(r)

print(unique_api)
