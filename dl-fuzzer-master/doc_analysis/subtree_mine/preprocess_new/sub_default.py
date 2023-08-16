import re

str_anno = 'DF_STR'
def sub_default(src_text, all_anno):
    if str(src_text).lower()  in ['none', 'null',  '_null']:
        return src_text, {}
    for an in all_anno:
        if an in src_text:
            return src_text, {}

    if len(src_text)>0 and str(src_text)[0] in ['(', '[']:
        return src_text, {}
    
    if re.match(r'.*\..*', str(src_text))!=None or str(src_text).startswith('<'):
        return src_text, {}
    
    return str_anno, {str_anno: src_text}