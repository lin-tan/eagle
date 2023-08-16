

additional_anno = 'ONE_WORD'
def process_oneword(src_text, anno=additional_anno):
    if len(src_text.strip().split())==1:
        src_text = anno + ' '+ src_text
    return src_text