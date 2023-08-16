import numpy as np
import torch
import traceback
import importlib
from timeit import default_timer as timer
import random

from rules.equiv_util import get_func_ptr, main, load_argument_file, load_input_file, get_log_file, save_output_data


def map_args_dictionary(mapping_list, source_dict, sparse_to_dense=True):
    # update key in source_dict according to mapping_list
    length = int(len(mapping_list) / 2)
    for i in range(length):
        if sparse_to_dense:
            if mapping_list[i] in source_dict.keys():
                source_dict[mapping_list[i + 1]] = source_dict.pop(mapping_list[i], None)
        else:
            if mapping_list[i + 1] in source_dict.keys():
                source_dict[mapping_list[i]] = source_dict.pop(mapping_list[i + 1], None)

    return source_dict


def map_args(mapping_list, source_list, sparse_to_dense=True):
    # update list of arguments in source_list according to mapping_list
    map_dict = {}
    length = int(len(mapping_list) / 2)
    for i in range(length):
        if sparse_to_dense:
            map_dict[mapping_list[i]] = mapping_list[i + 1]
        else:
            map_dict[mapping_list[i + 1]] = mapping_list[i]

    dest_list = []
    for source in source_list:
        if source in map_dict.keys():
            dest_list.append(map_dict[source])
        else:
            dest_list.append(source)
    return dest_list


def test_rule_sparse(fun_sparse, fun_dense, input, sparse_mutate_key_list, sparse_fixed_key_list, mapping_api_arg,
                     log_path):
    seed = 0
    # fix seed 
    torch.manual_seed(seed)
    random.seed(seed)
    np.random.seed(seed)
    # print(input)

    # convert dense arguments in sparse_fixed_key_list to sparse since the inputs are all dense tensors
    for sparse_fixed_key in sparse_fixed_key_list:
        input[sparse_fixed_key] = input[sparse_fixed_key].to_sparse()
    # print(input)
    # print("test_rule_sparse_1")

    # run dense function
    try:
        output_1 = fun_dense(**input)
        if output_1.is_sparse:
            output_1 = output_1.to_dense()
        output_1_np = output_1.cpu().detach().numpy()
    except:
        # print(traceback.format_exc())
        with open(log_path, "a") as f:
            f.write(traceback.format_exc() + "\n")
        output_1_np = None

    # reset seed 
    torch.manual_seed(seed)
    random.seed(seed)
    np.random.seed(seed)

    # convert argument key according to mapping_api_arg
    input = map_args_dictionary(mapping_api_arg, input, False)
    sparse_mutate_key_list = map_args(mapping_api_arg, sparse_mutate_key_list, False)
    # print(input)
    # print(sparse_mutate_key_list)
    # print("test_rule_sparse_2")

    # run sparse function
    try:
        # convert dense arguments in sparse_mutate_key_list to sparse since the inputs are all dense tensors
        for sparse_mutate_key in sparse_mutate_key_list:
            input[sparse_mutate_key] = input[sparse_mutate_key].to_sparse()
        # print("test_rule_sparse_2.5")
        # print(input)
        output2 = fun_sparse(**input)
        # print("test_rule_sparse_2.6")
        # print(output2)
        # print(output2.is_sparse)
        if output2.is_sparse:
            output2 = output2.to_dense()
        # print("test_rule_sparse_2.7")
        output_2_np = output2.cpu().detach().numpy()
    except:
        # print(traceback.format_exc())
        with open(log_path, "a") as f:
            f.write(traceback.format_exc() + "\n")
        output_2_np = None
    # print("test_rule_sparse_3")
    # print([output_1_np, output_2_np])
    # print(np.allclose(output_1_np, output_2_np))
    return [output_1_np, output_2_np]


def run(in_dir, out_dir, lib, version, api_config, input_index):
    # parse api config
    line = api_config.replace("\n", "")
    preprocess_line = line.split("_")
    if len(preprocess_line) < 2:
        exit()
    sparse_api_arg = preprocess_line[0].split("-")
    sparse_api_name = sparse_api_arg[0]
    sparse_api_key = []
    if len(sparse_api_arg) > 1:
        sparse_api_key = sparse_api_arg[1:]
    dense_api_arg = preprocess_line[1].split("-")
    dense_api_name = dense_api_arg[0]
    dense_api_key = []
    if len(dense_api_arg) > 1:
        dense_api_key = dense_api_arg[1:]
    mapping_api_arg = []
    if len(preprocess_line) > 2:
        mapping_api_arg = preprocess_line[2].split("-")

    sparse_mutate_key_list = []
    sparse_fixed_key_list = []

    # compare sparse_api_key and dense_api_key to generate sparse_mutate_key_list and sparse_fixed_key_list
    # sparse_mutate_key_list is the list of keys that are sparse and mutated during the mutation
    # sparse_fixed_key_list is the list of keys that are sparse and fixed during the mutation
    sparse_api_key = map_args(mapping_api_arg, sparse_api_key, True)
    # print(dense_api_key)
    for sparse_key in sparse_api_key:
        if sparse_key in dense_api_key:
            sparse_fixed_key_list.append(sparse_key)
        else:
            sparse_mutate_key_list.append(sparse_key)

    argument = load_argument_file(in_dir, lib, version, dense_api_name, input_index)
    log_file = get_log_file(out_dir, lib, version, 'rule_8', api_config, input_index)

    # argument = {}
    # argument["mat"] = torch.tensor([[-0.8196], [-1.4280]])
    # argument["mat1"] = torch.tensor([[0.1602, 0.2102], [0.3482, -0.7791]])
    # argument["mat2"] = torch.tensor([[1.0358], [1.1674]])

    # get function pointers
    package = "torch"
    mod = importlib.import_module(package)
    target_func_sparse = get_func_ptr(mod, sparse_api_name)
    target_func_dense = get_func_ptr(mod, dense_api_name)

    # run test
    [output_1, output_2] = test_rule_sparse(target_func_sparse, target_func_dense, argument, sparse_mutate_key_list,
                                            sparse_fixed_key_list, mapping_api_arg, log_file)

    save_output_data([output_1, output_2], out_dir, lib, version, 'rule_8', api_config, input_index)
    # print([output_1, output_2])
    # print(np.allclose(output_1, output_2))

    return output_1 is not None and output_2 is not None


if __name__ == "__main__":
    main(run)
