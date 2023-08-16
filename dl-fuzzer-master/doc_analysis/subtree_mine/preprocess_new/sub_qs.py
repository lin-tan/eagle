import sys
sys.path.insert(0,'..')

from util import * 
import argparse

p1 = r"\'\s*s\s"        # 's 
p2 = r"(?<=`)\s*s\s"    #
# p3 = r'"[\s\w\+\-]+"'     
p3 = r'[`\'"]+[\s\w\+\-]+[`\'"]+'

annotation = ' QSTR '
def sub_qs(src_text):
    anno_map = {}

    normalized_text = re.sub(p1, ' ', src_text)
    normalized_text = re.sub(p2, ' ', normalized_text)

    anno_map[annotation.strip()] = re.findall(p3, normalized_text)
    normalized_text = re.sub(p3, annotation, normalized_text)

    # anno_map[annotation.strip()] +=  re.findall(p4, normalized_text)
    # normalized_text = re.sub(p4, annotation, normalized_text)
    normalized_text = re.sub(consecutive_anno_regex(annotation), annotation, normalized_text)
    # normalized_text = re.sub(r'\s+', ' ', normalized_text)

    return remove_extra_space(normalized_text), anno_map

def test():
    test_case = {
        "A `bytes`, `str`, or `unicode` object.": "A QSTR object.",
        "A `ClusterSpec` or `ClusterResolver` describing the cluster.": "A QSTR describing the cluster.",
        "The storage type of the empty array, such as 'row_sparse', 'csr', etc.": "The storage type of the empty array, such as QSTR , etc." ,
        "If true, lazy updates are applied if gradient's stype is row_sparse.": "If true, lazy updates are applied if gradient stype is row_sparse.",
        'string, `"max"` or `"avg"`.': 'string, QSTR .',
        'For N=1 it can be either "NWC" (default) or "NCW", for N=2 it can be either "NHWC" (default) or "NCHW" and for N=3 either "NDHWC" (default) or "NCDHW".':
        'For N=1 it can be either QSTR (default) or QSTR , for N=2 it can be either QSTR (default) or QSTR and for N=3 either QSTR (default) or QSTR .',
        "in `tf.function`s (graphs).": "in `tf.function` (graphs).",
        'An int or list of `ints` that has length `1`, `N` or `N+2`': 'An int or list of QSTR that has length QSTR ',
        'An optional `string` from `"NWC", "NCW"`.': 'Normalized text: An optional QSTR from QSTR .'
    }
    for s in test_case:
        normalized, _ = sub_qs(s)
        if normalized==test_case[s]:
            print('PASS')
        else:
            print('FAIL')
            print('Original text: %s'% s)
            print('Normalized text: %s'% normalized)


if __name__ == '__main__':
    test()