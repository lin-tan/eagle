import numpy as np
import torch
import torchvision
import os
from datetime import datetime
import argparse
import traceback
import pickle
import importlib
import random
from timeit import default_timer as timer

from rules.equiv_util import get_func_ptr, main, load_argument_file, load_input_file, get_log_file, save_output_data


def test_rule_datatype(input, target_fun, arg_key, src_dtype, dst_dtype, log_file):
    seed = 0
    # fix seed 
    torch.manual_seed(seed)
    random.seed(seed)
    np.random.seed(seed)

    # run function with input in src_dtype
    input[arg_key] = input[arg_key].to(src_dtype)
    try:
        output_1 = target_fun(**input)
        # print(input_list)
        output_1_numpy = output_1.cpu().detach().numpy()
    except:
        with open(log_file, "a+") as f:
            f.write(traceback.format_exc())
        # print(traceback.format_exc())
        output_1_numpy = None

    # reset seed 
    torch.manual_seed(seed)
    random.seed(seed)
    np.random.seed(seed)

    # run function with input in dst_dtype
    input[arg_key] = input[arg_key].to(dst_dtype)
    try:
        output_2 = target_fun(**input)
        # print(type2_input_list)
        output_2_numpy = output_2.cpu().detach().numpy()
    except:
        with open(log_file, "a+") as f:
            f.write(traceback.format_exc())
        # print(traceback.format_exc())
        output_2_numpy = None

    return [output_1_numpy, output_2_numpy]


def run(in_dir, out_dir, lib, version, api_config, input_index):
    # parse api config
    preprocess_line = api_config.split("-")
    api_name = preprocess_line[0]
    arg_key = preprocess_line[1]
    src_dtype_name = preprocess_line[2]
    dst_dtype_name = preprocess_line[3]

    argument = load_argument_file(in_dir, lib, version, api_name, input_index)
    input_data = load_input_file(in_dir, input_index)
    log_file = get_log_file(out_dir, lib, version, 'rule_12', api_config, input_index)

    # argument = {}
    # argument["dim"] = -1
    # argument["x1"] = torch.tensor([ 47.8993, -27.2694,  20.9548, -13.5573, -54.0388, -76.8524,  -7.4037, -95.7477, 108.9276, -44.5625])
    # argument["x2"] = torch.tensor([ 47.8993, -27.2694,  20.9548, -13.5573, -54.0388, -76.8524,  -7.4037, -95.7477, 108.9276, -44.5625])

    # get function pointers
    package = "torch"
    mod = importlib.import_module(package)
    target_func = get_func_ptr(mod, api_name)
    src_dtype = get_func_ptr(mod, src_dtype_name)
    dst_dtype = get_func_ptr(mod, dst_dtype_name)

    # run test
    [output_1, output_2] = test_rule_datatype(argument, target_func, arg_key, src_dtype, dst_dtype, log_file)
    # print(output_1, output_2)

    save_output_data([output_1, output_2], out_dir, lib, version, 'rule_12', api_config, input_index)

    return output_1 is not None and output_2 is not None


if __name__ == "__main__":
    main(run)
