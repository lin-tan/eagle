from nltk.stem import WordNetLemmatizer
from sub_kw import *
from sub_re import *
from sub_brackets import *
from sub_param import *
from sub_num import *
from sub_qs import *
from further_process import * 
from oneword import *
from sub_default import *

import sys
sys.path.insert(0,'..')
from util import * 


lemmatizer = WordNetLemmatizer()

def normalize_sent(src_text, framework=None, arg_list=None, argname=None):
    anno_map = {}
    normalized_text = src_text

    if src_text=='' or src_text.isspace():
        return src_text, anno_map
    
    
    def _update(input):
        new_text, new_map = input
        return new_text, merge_dict(anno_map, new_map)
    
    normalized_text, anno_map = _update(sub_kw(normalized_text, framework))
    normalized_text, anno_map = _update(sub_param(normalized_text, arg_list, argname))
    # normalized_text = sub_bool(normalized_text)
    normalized_text, anno_map = _update(sub_brackets(normalized_text))
    normalized_text, anno_map = _update(sub_re(normalized_text))
    normalized_text, anno_map = _update(sub_num(normalized_text))
    normalized_text, anno_map = _update(sub_qs(normalized_text))
    normalized_text, anno_map = _update(further_process(normalized_text))

    normalized_text = lemmatizer.lemmatize(normalized_text)
    normalized_text = process_oneword(normalized_text)
    # normalized_text = ' '.join(lemmatize_sentence(normalized_text))
    # record.add(nltk.sent_tokenize(normalized_text))

    # print(src_text)
    # print(normalized_text)
    # print(anno_map)
    # print()
    return normalized_text, anno_map


def normalize_docdtype(src_text, framework=None, arg_list=None, argname=None):
    # the same with normalize_sent
    anno_map = {}
    normalized_text = src_text

    if src_text=='' or src_text.isspace():
        return src_text, anno_map

    def _update(input):
        new_text, new_map = input
        return new_text, merge_dict(anno_map, new_map)

    normalized_text, anno_map = _update(sub_kw(normalized_text, framework))
    normalized_text, anno_map = _update(sub_param(normalized_text, arg_list, argname))
    # normalized_text = sub_bool(normalized_text)
    normalized_text, anno_map = _update(sub_brackets(normalized_text))
    normalized_text, anno_map = _update(sub_re(normalized_text))
    normalized_text, anno_map = _update(sub_num(normalized_text))
    normalized_text, anno_map = _update(sub_qs(normalized_text))
    normalized_text, anno_map = _update(further_process(normalized_text))

    normalized_text = lemmatizer.lemmatize(normalized_text)

    # normalized_text = lemmatizer.lemmatize(normalized_text)

    normalized_text = process_oneword(normalized_text)

    return normalized_text, anno_map

def normalize_default(src_text, all_anno, framework=None, arg_list=None, argname=None):
    anno_map = {}
    normalized_text = src_text
    

    if not src_text or src_text=='' or src_text.isspace():
        return src_text, anno_map

    def _update(input):
        new_text, new_map = input
        return new_text, merge_dict(anno_map, new_map)

    normalized_text, anno_map = _update(sub_kw(normalized_text, framework))
    # normalized_text, anno_map = _update(sub_param(normalized_text, arg_list, argname))
    # normalized_text = sub_bool(normalized_text)
    normalized_text, anno_map = _update(sub_num(normalized_text))
    normalized_text, anno_map = _update(sub_brackets(normalized_text))
    normalized_text, anno_map = _update(sub_re(normalized_text))
    normalized_text, anno_map = _update(sub_qs(normalized_text))
    normalized_text, anno_map = _update(sub_default(normalized_text, all_anno))
    
    normalized_text, anno_map = _update(further_process(normalized_text))
    
    normalized_text = lemmatizer.lemmatize(normalized_text)

    # normalized_text = lemmatizer.lemmatize(normalized_text)

    normalized_text = process_oneword(normalized_text, anno='DEFAULT')

    return normalized_text, anno_map