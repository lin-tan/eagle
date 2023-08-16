import sys
sys.path.insert(0,'..')

from extract_utils import *
import random 
import csv


source_path = {
    'tf': '../tf/tf21_all/changed/',
    'pytorch': '../pytorch/pt15_all/',
    'mxnet': '../mxnet/mx16_all/',
    'sklearn': '../sklearn/constr_all/changed/'
}

all_target = ['dtype', 'ndim', 'shape', 'range', 'enum', 'tensor_t', 'structure']



def get_sample_file(files, cnt, save = ''):
    samples = random.sample(files,cnt)
    if save:
        save_file(save, '\n'.join(samples))
    return samples






def concat_doc_dtype(info, arg):
    doc_dtype = info['constraints'][arg].get('doc_dtype', [])
    if doc_dtype:
        separator = ', '
        return separator.join(doc_dtype)

    else: 
        return ''

        

def main(framework, update_list=False):
    # settings
    group = {
        'prim_dtype': ['dtype'],
        'nonprim_dtype': ['tensor_t', 'structure'],
        'shape': ['shape', 'ndim'],
        'validvalue': ['enum', 'range']
    }


    files = get_file_list(source_path[framework])
    
    file_saved = []
    #save_list(files, './{}_list'.format(framework))

    save_dir = './{}/'.format(framework)
    create_dir(save_dir, clean=True)

    for f in files:
            
        info = read_yaml(source_path[framework]+f)

        for arg in info['constraints']:
            # skip deprecated 
            if arg in info['inputs'].get('deprecated', []):
                continue
            filename = save_dir+f.replace('.yaml', '')+'-'+arg.replace('*', '_')+'.csv'
            file_saved.append(filename)
            with open(filename, 'w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(["descp1", "descp2", "default", "attribute", "constraint", "in_doc", "extracted"])

                atleastone=False
                doc_dtype = concat_doc_dtype(info, arg)
                descp = info['constraints'][arg]['descp']

                
                num_sent=0
                if parse_sentences(descp)!=['']:
                    num_sent = len(parse_sentences(descp))
                if doc_dtype:
                    num_sent += 1

                for big_cat in group:
                    constraint = []
                    for cat in group[big_cat]:
                        if cat in info['constraints'][arg]:
                            tmp = ', '.join(info['constraints'][arg][cat])
                            constraint.append('{}({})'.format(cat, tmp))

                    if constraint:   
                        atleastone = True    
                        constraint_str = ', '.join(constraint)
                        writer.writerow([doc_dtype, descp, info['constraints'][arg].get('default', ''), big_cat, constraint_str, '', 1])

                if not atleastone:
                    writer.writerow([doc_dtype, info['constraints'][arg]['descp'], info['constraints'][arg].get('default', ''), '', '', 0, 0])




    random.shuffle(file_saved)

    print(len(file_saved))
    if update_list:
        save_list(file_saved, './{}_list'.format(framework))






if __name__ == "__main__":

    framework = sys.argv[1]

    update_list = bool(int(sys.argv[2]))

    main(framework, update_list)