import sys
sys.path.insert(0,'..')

from util import * 
import argparse

dtype_anno = 'D_TYPE'
ds_anno = 'D_STRUCTURE'
anno_dict = [
    {'dtype': dtype_anno},
    {'structure': ds_anno},
    {'tensor_t': ds_anno}
]

# collection_anno = {
#     r'D_TYPE((\s|,|and|or|a|an)+D_TYPE)+': 'D_TYPE',
#     r'D_STRUCTURE((\s|,|and|or|a|an)+D_STRUCTURE)+': 'D_STRUCTURE',
#     r'D_STRUCTURE/D_STRUCTURE': 'D_STRUCTURE',
#     r'D_TYPE/D_TYPE': 'D_TYPE',

# }

pre_normalize ={
    r'floating point': 'float',
    r'floating-point': 'float',
    # r'data\s+type': 'dtype',

}

def sub_kw(src_text, framework):
    anno_map = {dtype_anno: [], ds_anno:[]}

    normalized_text = src_text
    dtype_ls = read_yaml('./dtype_ls.yaml')[framework]
    # dtype_ls = read_yaml('../config/dtype_ls.yaml')[framework]
    for pre_re in pre_normalize:
        normalized_text = re.sub(pre_re, pre_normalize[pre_re], normalized_text, flags=re.IGNORECASE)


    for anls in anno_dict:
        category = next(iter(anls))
        keywords = dtype_ls[category]
        keywords = sorted(keywords, key=len, reverse=True)
        p = get_bigrex(sorted(keywords, key=len, reverse=True), boundary=True, escape=True)
        p = r'`*({})`*'.format(p)
        anno_map[anls[category]] += re.findall(p, normalized_text, flags=re.IGNORECASE)
        normalized_text = re.sub(p, anls[category], normalized_text, flags=re.IGNORECASE)
        # regex = re.compile(r'{}'.format(p))
        # normalized_text = regex.sub(normalized_text, anls[category])
    normalized_text = re.sub(consecutive_anno_regex(dtype_anno), dtype_anno, normalized_text)
    normalized_text = re.sub(consecutive_anno_regex(ds_anno), ds_anno, normalized_text)

    # for pattern in collection_anno:
    #     normalized_text = re.sub(pattern, collection_anno[pattern], normalized_text)
    # print(src_text)
    # print(normalized_text)
    # print(anno_map)
    # print()
    return normalized_text, anno_map


def test(framework='tensorflow'):
    test_case = {
        'a integer list' : 'a D_TYPE D_STRUCTURE', 
        'a tensor of dtype `tf.int`': 'a D_STRUCTURE of dtype D_TYPE',
        'must be one of the following dtypes: `int32`, `tf.float32`, `tf.uint8`.' : 'must be one of the following dtypes: D_TYPE.',
        'a tensor or a list of tensors': 'a D_STRUCTURE of D_STRUCTURE',
        "list/tuple of 2 ints,": "D_STRUCTURE of 2 D_TYPE,",
        "a floating point tensor": "a D_TYPE D_STRUCTURE",
        "data type of the output": "data type of the output",   # remain the same
        
    }
    # dtype_ls = read_yaml('./dtype_ls.yaml')[framework]
    for s in test_case:
        normalized, _ = sub_kw(s, framework)
        if normalized==test_case[s]:
            print('PASS')
        else:
            print('FAIL')
            print('Original text: %s'% s)
            print('Normalized text: %s'% normalized)


if __name__ == '__main__':
    test()
    # parser=argparse.ArgumentParser()
    # parser.add_argument('--test', default=True, action='store_true')

    # args = parser.parse_args()
    # if args.test:
    #     test()

