from util import *
import random
import argparse

anno_dict = {
    'dtype': 'D_TYPE',
    'structure': 'D_STRUCTURE',
    'tensor_t': 'D_STRUCTURE',
    'shape': 'BSTR',
    'ndim': 'CONSTANT_VAL',
    'enum': 'QSTR'
}

def sampling(text_folder, all_exclude, sample_ratio):
    dataset = []        # list of pair [fpath, argname] to be sampled 
    yaml_files = get_file_list(text_folder)
    count = 0
    for fpath in yaml_files:
        info = read_yaml(os.path.join(text_folder, fpath))
        for arg in info['constraints']:
            descp = info['constraints'][arg]['descp']
            if not (descp=='' or descp.isspace()):
                count += 1
                if not arg in all_exclude.get(fpath, []):
                    dataset.append([fpath, arg, info['title']])
    sample_size = int(count*sample_ratio)
    sampled = random.sample(dataset, sample_size)
    return sampled


# def get_sampled_dataset(framework, text_folder, save_path=None):
#     def _update_dict(d, key, val):
#         if key not in d:
#             d[key] = []
#         if isinstance(val, list):
#             d[key] += val
#         else:
#             d[key].append(val)
#         return d

#     saving_path = os.path.join(save_path, framework+'_list')
#     all_exclude = {}
#     for fpath, arg, _ in old_sample_list:
#         all_exclude = _update_dict(all_exclude, fpath, arg)

#     for fpath in exclude_list:
#         all_exclude = _update_dict(all_exclude, fpath, exclude_list[fpath])
    
    
#     sampled_dataset = sampling(text_folder, all_exclude, sample_ratio)
#     save_yaml(saving_path, sampled_dataset)
#     return sampled_dataset

def prepare_constraint(ground_truth, arg, normalize=True):
    if ground_truth:
        arg_info = ground_truth['constraints'][arg]
    else:
        arg_info = {}

    def helper(label):
        constr = [str(c) for c in arg_info.get(label, [])]
        if constr and normalize and label in anno_dict:
            return anno_dict[label]

        return ';'.join((constr))

    ret = []
    ret.append(helper('dtype'))
    tensor = helper('tensor_t')
    ds = helper('structure')
    if tensor or ds:
        ret.append(anno_dict['structure'])
    ret.append(helper('shape'))
    ret.append(helper('ndim'))
    ret.append(helper('range'))
    ret.append(helper('enum'))
    return ret

def main(framework, sample_list_path,  text_folder, ground_truth_folder, save_path=None):
    # ground_truth_folder: folder that contains extracted constraints
    # yaml_files = get_file_list(text_folder)
    ground_truth_files = get_file_list(ground_truth_folder)
    sample_list= read_yaml(sample_list_path)
    # sampled_dataset = get_sampled_dataset(framework, text_folder, save_path)
    dataset = [['API', 'Arg',  'Descp', 'Normalized_descp', 'dtype', 'structure', 'shape', 'ndim', 'range', 'enum']]
    for fpath, arg, _ in sample_list:
        # for each param
        info = read_yaml(os.path.join(text_folder, fpath))
        ground_truth = read_yaml(os.path.join(ground_truth_folder, fpath)) if fpath in ground_truth_files else None
        normalized_descp = info['constraints'][arg]['normalized_descp']

        line_api = [info['title'], arg]
        line_constraint = prepare_constraint(ground_truth, arg, normalize=True)
        # append each normalized sentence to the csv file
        for nd in normalized_descp:
            if not (nd=='' or nd.isspace()):
                dataset.append( line_api + [info['constraints'][arg]['descp'], nd] + line_constraint )
        # add doc_dtype
        if 'doc_dtype' in info['constraints'][arg]:
            dataset.append(line_api + ['DD: '+ info['constraints'][arg]['doc_dtype'], info['constraints'][arg]['normalized_docdtype']] + line_constraint)
        # add default value
        if 'default' in info['constraints'][arg] and info['constraints'][arg]['default'] is not None:
            dataset.append(line_api + ['DF: '+ info['constraints'][arg]['default'], info['constraints'][arg]['normalized_default']] + line_constraint)

    # for fpath, arg, _ in old_sample_list:
    #     info = read_yaml(os.path.join(text_folder, fpath))
    #     ground_truth = read_yaml(os.path.join(ground_truth_folder, fpath)) if fpath in ground_truth_files else None
    #     line_api = [info['title'], arg]
    #     line_constraint = prepare_constraint(ground_truth, arg, normalize=True)
    #     if 'default' in info['constraints'][arg] and info['constraints'][arg]['default'] is not None:
    #         dataset.append(line_api + ['DF: '+ info['constraints'][arg]['default'], info['constraints'][arg]['normalized_default']] + line_constraint)

    write_csv(os.path.join(save_path, framework+'_sample_rebuttal.csv'), dataset)


main('tf', './sample/tf_list_batch1', './normalized_doc_icse/tf', '../extract_constraint/tf/tf21_all/changed/',  save_path='./sample')
main('pt', './sample/pt_list_batch1', './normalized_doc_icse/pt', '../extract_constraint/pytorch/pt15_all', save_path='./sample')
main('mx', './sample/mx_list_batch1', './normalized_doc_icse/mx', '../extract_constraint/mxnet/mx16_all',  save_path='./sample')
