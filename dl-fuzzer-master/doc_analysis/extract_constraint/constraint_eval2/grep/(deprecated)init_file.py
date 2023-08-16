import sys
sys.path.insert(0,'../..')

from extract_utils import *
import random 
import csv


source_path = {
    'tf': '../../grep/tf/changed/',
    'pytorch': '../../grep/pytorch/changed/',
    'mxnet': '../../grep/mxnet/changed/'
}

all_target = ['dtype', 'tensor_t', 'structure']

def concat_doc_dtype(info, arg):
    doc_dtype = info['constraints'][arg].get('doc_dtype', [])
    if doc_dtype:
        separator = ', '
        return separator.join(doc_dtype)

    else: 
        return ''

        

def main(framework, eval_list_path, save_dir, list_saveto, update_list=False):
    # settings
    group = {
        'dtype': ['dtype'],
        'structure': ['tensor_t', 'structure'],
    }

    #files = get_file_list(source_path[framework])
    eval_list = read_yaml(eval_list_path)

    file_saved = []
    create_dir(save_dir, clean=True)

    for line in eval_list:
        f, arg, cat = line
        info = read_yaml(source_path[framework]+f)

        if arg in info['inputs'].get('deprecated', []):
            continue
        filename = save_dir+f.replace('.yaml', '')+'-'+arg.replace('*','')+'-'+cat+'.csv'
        file_saved.append(filename)
        with open(filename, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["descp1", "descp2", "default", "attribute", "constraint", "in_doc", "extracted"])

            atleastone=False
            doc_dtype = concat_doc_dtype(info, arg)
            descp = info['constraints'][arg]['descp']

            
            # num_sent=0
            # if parse_sentences(descp)!=['']:
            #     num_sent = len(parse_sentences(descp))
            # if doc_dtype:
            #     num_sent += 1

            constraint = []
            for subcat in group[cat]:
                if subcat in info['constraints'][arg]:
                    tmp = ', '.join(info['constraints'][arg][subcat])
                    constraint.append('{}({})'.format(subcat, tmp))

            if constraint:   
                atleastone = True    
                constraint_str = ', '.join(constraint)
                writer.writerow([doc_dtype, descp, info['constraints'][arg].get('default', ''), cat, constraint_str, '', 1])

            if not atleastone:
                writer.writerow([doc_dtype, info['constraints'][arg]['descp'], info['constraints'][arg].get('default', ''), '', '', 0, 0])




    random.shuffle(file_saved)

    print(len(file_saved))
    if update_list:
        save_list(file_saved, list_saveto)








main('tf','../../grep/tf_evallist', './tf/', './tf_list', update_list=True)
main('pytorch','../../grep/pytorch_evallist',  './pytorch/', './pytorch_list', update_list=True)
main('mxnet','../../grep/mxnet_evallist',  './mxnet/', './mxnet_list', update_list=True)

# 3272
# 1422
# 5918