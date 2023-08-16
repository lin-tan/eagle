import numpy as np
import tensorflow as tf
import os
from datetime import datetime
import argparse
import traceback
import pickle
import importlib
import random
from timeit import default_timer as timer

from rules.equiv_util import get_func_ptr, main, load_argument_file, load_input_file, get_log_file, save_output_data


def test_rule_pad_unpad(input, argument, pad_fun, unpad_fun, log_file):
    seed = 0
    # fix seed
    tf.random.set_seed(seed)
    random.seed(seed)
    np.random.seed(seed)

    try:
        # pad input
        layer_1 = pad_fun(**argument)
        padded_input = layer_1(input)
        # print(padded_input.shape)
        padding = argument["padding"]
        if isinstance(argument["padding"], int):
            padding = ((argument["padding"], argument["padding"]), (argument["padding"], argument["padding"]))
        elif len(argument["padding"]) == 2:
            if isinstance(argument["padding"][0], int):
                padding = ((argument["padding"][0], argument["padding"][0]), (argument["padding"][1],
                                                                              argument["padding"][1]))
            elif len(argument["padding"][0]) == 2:
                padding = argument["padding"]

        # unpad input and compare
        argument_2 = {}  # convert argument accordingly
        argument_2["centered"] = False
        argument_2["normalized"] = False
        argument_2["input"] = padded_input
        argument_2["size"] = input.shape[1:3]

        offset_i = [padding[0][0], padding[1][0]]
        offsets = []
        for i in range(input.shape[0]):
            offsets.append(offset_i)
        argument_2["offsets"] = offsets
        # print(argument_2)

        unpadded_input = unpad_fun(**argument_2)

        output_1 = input
        output_2 = unpadded_input
    except:
        with open(log_file, "a+") as f:
            f.write(traceback.format_exc())
        # print(traceback.format_exc())
        output_1 = None
        output_2 = None

    return [output_1, output_2]


def run(in_dir, out_dir, lib, version, api_config, input_index):
    # parse api config
    preprocess_line = api_config.split("-")
    pad_api_name = preprocess_line[0]
    unpad_api_name = preprocess_line[1]

    argument = load_argument_file(in_dir, lib, version, pad_api_name, input_index)
    input_data = load_input_file(in_dir, input_index)
    log_file = get_log_file(out_dir, lib, version, 'rule_14', api_config, input_index)

    # get function pointers
    package = "tensorflow"
    mod = importlib.import_module(package)
    pad_fun = get_func_ptr(mod, pad_api_name)
    mod = importlib.import_module(package)
    unpad_fun = get_func_ptr(mod, unpad_api_name)

    # run test
    [output_1, output_2] = test_rule_pad_unpad(input_data, argument, pad_fun, unpad_fun, log_file)
    # print(output_1.shape, output_2.shape)

    save_output_data([output_1, output_2], out_dir, lib, version, 'rule_14', api_config, input_index)

    return output_1 is not None and output_2 is not None


if __name__ == "__main__":
    main(run)
