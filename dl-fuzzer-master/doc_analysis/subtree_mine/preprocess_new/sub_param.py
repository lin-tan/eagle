import sys
sys.path.insert(0,'..')
from util import * 
import argparse


param_anno = ' PARAM'
# itself_anno = ' THIS_PARAM'


def sub_param(src_text, arg_list, argname):
    sub_arglist = []
    anno_map = {}
    for arg in arg_list:
        if not (arg == argname or '*' in arg) and  len(arg)>1:
            sub_arglist.append(arg)
    normalized_text = src_text
    if sub_arglist:
        param_p = get_bigrex(sorted(sub_arglist, key=len, reverse=True), boundary=True, escape=True)
        param_p = r"[`'\"]*({})[`'\"]*".format(param_p)
        anno_map[param_anno.strip()] = re.findall(param_p, normalized_text, flags=re.IGNORECASE)
        normalized_text = re.sub(param_p, param_anno, normalized_text, flags=re.IGNORECASE)
    # if '*' not in argname and len(argname)>1:
    #     p_this = r"[`'\"]*(\b{}\b)[`'\"]*".format(argname)
    #     anno_map[itself_anno.strip()] = re.findall(p_this, normalized_text, flags=re.IGNORECASE)
    #     normalized_text = re.sub(p_this, itself_anno, normalized_text, flags=re.IGNORECASE)
    #normalized_text = re.sub(r'\s+', ' ', normalized_text)

    return remove_extra_space(normalized_text), anno_map


def test(framework='tensorflow'):
    test_case = {
        "Second input (of size matching x1).": 'Second PARAM (of size matching PARAM).',
        "Has to match input size if it is a tuple.": 'Has to match PARAM size if it is a tuple.',
        "the input tensor of at least `signal_ndim` dimensions":"the PARAM tensor of at least PARAM dimensions",  
        'if "scale_height" parameter is not defined or input height multiplied by "scale_height" otherwise.': 'if THIS_PARAM parameter is not defined or PARAM height multiplied by THIS_PARAM otherwise.',
        'nothing to sub': "nothing to sub"
    }
    # dtype_ls = read_yaml('./dtype_ls.yaml')[framework]
    for s in test_case:
        normalized, _ = sub_param(s, ['x1', 'input', 'signal_ndim', 'scale_height'], 'scale_height')
        if normalized==test_case[s]:
            print('PASS')
        else:
            print('FAIL')
            print('Original text: %s'% s)
            print('Normalized text: %s'% normalized)


if __name__ == '__main__':
    test()


