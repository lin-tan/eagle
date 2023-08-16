import sys
sys.path.insert(0,'..')

from util import * 
import argparse

# p = r'[`''"]*[\[\(]([\w\.\(\)\+\-\*\/]+,\s*[\w\.\s,\(\)\+\-\*\/]+|[\w\.\(\)\+\-\*\/]+)[\]\)][`''"]*'
p = r'[`''"]*([\[\(][\w\s\.,\(\)\+\-\*\/]+[\]\)])[`''"]*'
annotation = ' BSTR'
def sub_brackets(src_text):
    anno_map = {}
    anno_map[annotation.strip()] = re.findall(p, src_text)
    normalized_text = re.sub(p, annotation, src_text)
    #normalized_text = re.sub(r'\s+', ' ', normalized_text)
    # print(src_text)
    # print(normalized_text)
    # print(anno_map)
    # print()

    return remove_extra_space(normalized_text), anno_map

def test():
    test_case = {
        'A name for the operation (optional).': 'A name for the operation BSTR.',
        'Must be in the range `[-rank(values), rank(values))`.': 'Must be in the range BSTR.',
        '`axis` must be in range`[-(D+1), D]` (inclusive).': '`axis` must be in range BSTR BSTR.',
        'Tensor with shape `(samples, state_size)`(no time dimension)':'Tensor with shape BSTR BSTR',
        'Tensor of temporal data of shape `(samples, time, ...)`(at least 3D)': 'Tensor of temporal data of shape BSTR BSTR',
        "Must be in range `[0, params.shape[axis])`.": "Must be in range BSTR."
    }
    for s in test_case:
        normalized, _ = sub_brackets(s)
        if normalized==test_case[s]:
            print('PASS')
        else:
            print('FAIL')
            print('Original text: %s'% s)
            print('Normalized text: %s'% normalized)


if __name__ == '__main__':
    test()