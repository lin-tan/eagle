import numpy as np
import torch
import os
from datetime import datetime
import argparse
import traceback
import pickle
import importlib
import random
from timeit import default_timer as timer

from rules.equiv_util import get_func_ptr, main, load_argument_file, load_input_file, get_log_file, save_output_data

def copy_layer_weights(src_layer, dst_layer):
    # helper function to copy weights from src_layer to dst_layer
    with torch.no_grad():
        src_names_list = src_layer._all_weights
        src_weights_list = src_layer.all_weights
        # dst_names_list = dst_layer._all_weights
        # dst_weights_list = dst_layer.all_weights
        for index in range(len(src_layer._all_weights)):
            src_names = src_names_list[index]
            src_weights = src_weights_list[index]
            # dst_names = dst_names_list[index]
            # dst_weights = dst_weights_list[index]
            for weight_i, name_i in zip(src_weights, src_names):
                dst_layer.__setattr__(name_i, weight_i)

def test_rule_time_major(input, argument, target_fun, log_file):
    seed = 0
    # fix seed
    torch.manual_seed(seed)
    random.seed(seed)
    np.random.seed(seed)

    # run original function and input
    try:
        layer_func = target_fun(**argument).eval()
        output_1, _ = layer_func(input)
        output_1_numpy = output_1.cpu().detach().numpy()
    except:
        with open(log_file, "a+") as f:
            f.write(traceback.format_exc())
        print(traceback.format_exc())
        output_1_numpy = None

    # reset seed
    torch.manual_seed(seed)
    random.seed(seed)
    np.random.seed(seed)

    # transpose input and mutate batch_first argument
    try:
        if "batch_first" in argument.keys():
            if argument["batch_first"]:
                argument["batch_first"] = False
            else:
                argument["batch_first"] = True
        else:
            argument["batch_first"] = True

        input_t = input.permute(1, 0, 2)
        layer_func_r = target_fun(**argument).eval()
        copy_layer_weights(layer_func, layer_func_r)
        output_t, _ = layer_func_r(input_t)
        output_2 = output_t.permute(1, 0, 2)
        output_2_numpy = output_2.cpu().detach().numpy()
    except:
        with open(log_file, "a+") as f:
            f.write(traceback.format_exc())
        print(traceback.format_exc())
        output_2_numpy = None

    return [output_1_numpy, output_2_numpy]


def run(in_dir, out_dir, lib, version, api_config, input_index):

    api_name = api_config

    argument = load_argument_file(in_dir, lib, version, api_name.lower(), input_index)
    log_file = get_log_file(out_dir, lib, version, 'rule_10', api_config, input_index)

    # get function pointers
    package = "torch"
    mod = importlib.import_module(package)
    target_fun = get_func_ptr(mod, api_name)

    input = argument["input"]
    argument.pop("input")

    # run test
    [output_1, output_2] = test_rule_time_major(input, argument, target_fun, log_file)

    save_output_data([output_1, output_2], out_dir, lib, version, 'rule_10', api_config, input_index)

    return output_1 is not None and output_2 is not None


if __name__ == "__main__":
    main(run)
