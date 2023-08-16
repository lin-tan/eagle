import sys
sys.path.insert(0,'..')
from extract_utils import *


source_path = {
    'tf': '../tf/constraint_4/changed/',
    'pytorch': '../pytorch/constraint_1/changed/',
    'mxnet': '../mxnet/constraint_2/changed/'
}
check_cat = ['enum', 'range']
stop_list = ['**kwargs', '*args']

for framework in source_path:
    ret = {}
    api_cnt = 0
    param_cnt = 0
    file_list = get_file_list(source_path[framework])
    for f in file_list:
        info = read_yaml(source_path[framework]+f)
        for arg in info['constraints']:
            if arg in info['inputs'].get('deprecated', []):
                continue
            if arg[0]=='*':
                continue
            has_constr = False
            for cc in check_cat:
                if cc in info['constraints'][arg]:
                    has_constr = True
                    break

            if not has_constr:
                # add arg to the result
                if f not in ret:
                    ret[f] = []
                    api_cnt+=1
                ret[f].append(arg)
                param_cnt+=1

    save_yaml('./{}.yaml'.format(framework), ret)
    print('{}:   {} APIs {} parameters'.format(framework, api_cnt, param_cnt))
    save_list(ret.keys(), './{}_APIs'.format(framework))
