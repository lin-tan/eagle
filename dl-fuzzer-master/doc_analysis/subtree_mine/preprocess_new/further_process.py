import sys
sys.path.insert(0,'..')

from util import * 
from sub_num import *
import argparse


def further_process(src_text):
    
    # normalized_text = remove_stopwords(normalized_text)

    # replace all non-(alphanumeric or '_') char with space
    normalized_text = re.sub('[^0-9a-zA-Z_,]+', ' ', src_text)
    normalized_text, anno_map = sub_num(normalized_text)
    # incase there is individual '_'    
    word_set = list(filter(lambda s: (len(s)>0 and not s.isspace()) and s!='_', normalized_text.split()))
    # remove "_" from begining or end of each
    normalized_text = ' '.join([w.strip('_') for w in word_set])
    normalized_text = re.sub('__', '_', normalized_text)


    normalized_text = re.sub(r'cannot', 'can not', normalized_text, flags=re.IGNORECASE)

    # hardcoded
    normalized_text = re.sub('constant_num\s+d\s', 'CONSTANT_NUM-D ', normalized_text, flags=re.IGNORECASE)
    # TODO: this may affect the subtree-filtering process

    
    return normalized_text, anno_map

def test():
    test_case = {
        'An object exposing the D_STRUCTURE interface, an object whose __array__ method returns an D_STRUCTURE or any BSTR D_STRUCTURE':
        'An object exposing the D_STRUCTURE interface, an object whose array method returns an D_STRUCTURE or any BSTR D_STRUCTURE',
        "fdgd group__imgproc__transfdddddf fgdgf": "fdgd group_imgproc_transfdddddf fgdgf", 
        "A CONSTANT_NUM D D_STRUCTURE of type D_TYPE": "A CONSTANT_NUM-D D_STRUCTURE of type D_TYPE",
        "A D_STRUCTURE of CONSTANT_NUM D_TYPE": "A D_STRUCTURE of CONSTANT_NUM D_TYPE"
    }
    for s in test_case:
        normalized, _ = further_process(s)
        if normalized==test_case[s]:
            print('PASS')
        else:
            print('FAIL')
            print('Original text: %s'% s)
            print('Normalized text: %s'% normalized)


if __name__ == '__main__':
    test()