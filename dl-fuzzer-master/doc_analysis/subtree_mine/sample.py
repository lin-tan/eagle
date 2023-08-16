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
def sampling(text_folder, sample_ratio):
    dataset = []        # list of pair [fpath, argname] to be sampled 
    yaml_files = get_file_list(text_folder)
    for fpath in yaml_files:
        info = read_yaml(os.path.join(text_folder, fpath))
        for arg in info['constraints']:
            descp = info['constraints'][arg]['descp']
            if not (descp=='' or descp.isspace()):
                dataset.append([fpath, arg, info['title']])
    sample_size = int(len(dataset)*sample_ratio)
    sampled = random.sample(dataset, sample_size)
    return sampled
    
def get_sampled_dataset(framework, text_folder, resample=False, save_path=None, sample_ratio=0.2):
    fpath = os.path.join(save_path, framework+'_list')

    if resample:
        sampled_dataset = sampling(text_folder, sample_ratio)
        save_yaml(fpath, sampled_dataset)
    else:
        sampled_dataset = read_yaml(fpath)
    return sampled_dataset

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
    ret.append(helper('tensor_t'))
    ret.append(helper('structure'))
    ret.append(helper('shape'))
    ret.append(helper('ndim'))
    ret.append(helper('range'))
    ret.append(helper('enum'))
    return ret

def main(framework, text_folder, ground_truth_folder, resample=False, save_path=None, sample_ratio=0.2):
    # ground_truth_folder: folder that contains extracted constraints
    # yaml_files = get_file_list(text_folder)
    ground_truth_files = get_file_list(ground_truth_folder)
    sampled_dataset = get_sampled_dataset(framework, text_folder, resample, save_path, sample_ratio)
    dataset = [['API', 'Arg',  'Descp', 'Normalized_descp', 'dtype', 'tensor_t', 'structure', 'shape', 'ndim', 'range', 'enum']]
    for fpath, arg, _ in sampled_dataset:
        info = read_yaml(os.path.join(text_folder, fpath))
        ground_truth = read_yaml(os.path.join(ground_truth_folder, fpath)) if fpath in ground_truth_files else None
        normalized_descp = info['constraints'][arg]['normalized_descp']

        line_api = [info['title'], arg]
        line_constraint = prepare_constraint(ground_truth, arg, normalize=True)
        # for nd in normalized_descp:
        #     if not (nd=='' or nd.isspace()):
        #         dataset.append( line_api + [info['constraints'][arg]['descp'], nd] + line_constraint )
        if 'doc_dtype' in info['constraints'][arg]:
            dataset.append(line_api + ['DD: '+ info['constraints'][arg]['doc_dtype'], info['constraints'][arg]['normalized_docdtype']] + line_constraint)


    write_csv(os.path.join(save_path, framework+'_sample2.csv'), dataset)


# if __name__ == "__main__":
#     parser=argparse.ArgumentParser()
#     parser.add_argument('framework')
#     parser.add_argument('text_folder')
#     parser.add_argument('ground_truth_folder')
#     parser.add_argument('--resample', default=False)


#     args = parser.parse_args()
#     # framework = args.framework
#     constr_folder = args.constr_folder
#     save_to = args.save_to
#     sent_path = args.sent_path
#     main(constr_folder, save_to, sent_path)

# main('tf', './normalized_doc/tf', '../extract_constraint/tf/tf21_all/changed/', resample=False, save_path='./sample', sample_ratio=0.1)
main('pt', './normalized_doc/pt2', '../extract_constraint/pytorch/pt15_all', resample=False, save_path='./sample', sample_ratio=0.1)
main('mx', './normalized_doc/mx2', '../extract_constraint/mxnet/mx16_all', resample=False, save_path='./sample', sample_ratio=0.1)
