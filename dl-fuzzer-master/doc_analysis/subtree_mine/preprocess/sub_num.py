import sys
sys.path.insert(0,'..')

from util import * 
import argparse

constant_anno = ' CONSTANT_NUM'
float_anno = ' CONSTANT_FLOAT'
bool_anno = ' CONSTANT_BOOL'
# p_num = r'(`|\'|"|^|\s)[\+\-]*(\d+([e\+\-\.]+\d+)?)(`|\'|"|\b)'
p_num = r'((`|\'|"|^|\s|[^0-9a-zA-Z])([+-]?(\d+(\.\d*)?|\.\d+)([eE][+-]?\d+)?)(`|\'|"|\b))'
p_bool = r'[`\'"]*\b(true|false)\b[`\'"]*'

# p1 = r'(`|^|\s)[\+\-]*(\d+)([e\+\-\.]+\d+)?(`|\b)'
# p2 = r'`*\b(true|false|none|zero)\b`*'
# p3 = r''
# annotation = ' CONSTANT_VAL '

def detect_intfloat(src_text):
    re_result = re.findall(p_num, src_text, flags=re.IGNORECASE)
    normalized_text = src_text
    anno_map = {constant_anno.strip(): [], float_anno.strip(): []}
    for rr in re_result:
        all_word = rr[0]
        num = rr[2]
        target_anno = constant_anno # by default, CONSTANT_NUM
        try:
            int(num)
        except:
            try:
                float(num)
                target_anno = float_anno    # only when it is not a integer, and can be converted into float, use CONSTANT_FLOAT
            except:
                pass
        # print(rr)
        normalized_text = normalized_text.replace(all_word, target_anno)
        #re.sub(all_word, target_anno, normalized_text, flags=re.IGNORECASE)
        anno_map[target_anno.strip()].append(num)
    return normalized_text, anno_map

def sub_num(src_text):
    normalized_text = src_text
    # preprocess, 3d -> 3 d
    normalized_text = re.sub(r'(\b\d)(d\s)', r'\1 \2', normalized_text, flags=re.IGNORECASE)

    # anno_map = {}
    
    # anno_map[constant_anno.strip()] = [x[1] for x in re.findall(p_num, normalized_text, flags=re.IGNORECASE)]
    # normalized_text = re.sub(p_num, constant_anno, normalized_text, flags=re.IGNORECASE)
    
    normalized_text, anno_map = detect_intfloat(normalized_text)

    anno_map[bool_anno.strip()] = re.findall(p_bool, normalized_text, flags=re.IGNORECASE)
    normalized_text = re.sub(p_bool, bool_anno, normalized_text, flags=re.IGNORECASE)

    normalized_text = re.sub(consecutive_anno_regex(constant_anno), constant_anno, normalized_text)
    normalized_text = re.sub(consecutive_anno_regex(bool_anno), bool_anno, normalized_text)

    # print(src_text)
    # print(normalized_text)
    # print(anno_map)
    # print()
    return remove_extra_space(normalized_text), anno_map
 
def test():
    test_case = {
        "Defaults to 1.": "Defaults to CONSTANT_NUM.",
        "start index of the consecutive 4 coordinate .": "start index of the consecutive CONSTANT_NUM coordinate .",
        "Factor by which to downscale. E.g. 2 will halve the input size.": "Factor by which to downscale. E.g. CONSTANT_NUM will halve the input size.",
        "Lower limit of norm of weight. If lower_bound <= 0": "Lower limit of norm of weight. If lower_bound <= CONSTANT_NUM",
        "Default value 0.01": "Default value CONSTANT_FLOAT",
        "4-D Tensor of shape": "CONSTANT_NUM-D Tensor of shape",
        "4D Tensor of shape": "CONSTANT_NUM D Tensor of shape",
        "If `type` is not `1`, `2` or `3`,": "If `type` is not CONSTANT_NUM,",
        "dtype FP32": "dtype FP32",
        "An int or list of `ints` that has length `1`, `N` or `N+2`.": "An int or list of `ints` that has length CONSTANT_NUM, `N` or `N+2`.",
        '1D D_STRUCTURE of size PARAM where the entry i encodes': 'CONSTANT_NUM D D_STRUCTURE of size PARAM where the entry i encodes',
        'if `true`, set ...': 'if CONSTANT_BOOL, set ...',
        'default=9.9999999392252903e-09': 'default CONSTANT_FLOAT',
        "default='0'": 'default CONSTANT_NUM',
        "default=-1.3": 'default CONSTANT_FLOAT',
        "Subclasses may choose to throw if reset_state is set to 'False'.": "Subclasses may choose to throw if reset_state is set to CONSTANT_BOOL."
    }
    for s in test_case:
        normalized, _ = sub_num(s)
        if normalized.lstrip()==test_case[s]:
            print('PASS')
        else:
            print('FAIL')
            print('Original text: %s'% s)
            print('Normalized text: %s'% normalized)


if __name__ == '__main__':
    test()