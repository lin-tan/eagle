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


def copy_dict(input_dict):
    # return a copy of input_dict
    results = {}
    for key in input_dict:
        results[key] = input_dict[key]
    return results


def test_rule_sparse(fun, input, sparse_key, log_file):
    seed = 0
    # fix seed
    tf.random.set_seed(seed)
    random.seed(seed)
    np.random.seed(seed)

    # convert numpy argument to tf.constant
    for key in input:
        if isinstance(input[key], np.ndarray) or isinstance(input[key], list):
            input[key] = tf.constant(input[key])

    # run dense function
    try:
        output_1 = fun(**input)
    except:
        with open(log_file, "a+") as f:
            f.write(traceback.format_exc())
        # print(traceback.format_exc())
        output_1 = None

    # reset seed 
    tf.random.set_seed(seed)
    random.seed(seed)
    np.random.seed(seed)

    # run sparse function
    try:
        # convert argument key according to sparse_key
        input_2 = copy_dict(input)
        input_2[sparse_key] = tf.sparse.from_dense(input_2[sparse_key])
        # print(input_2)
        output2 = fun(**input_2)
        if isinstance(output2, tf.sparse.SparseTensor):
            output2 = tf.sparse.to_dense(output2)
        # print(input[sparse_key])
    except:
        with open(log_file, "a+") as f:
            f.write(traceback.format_exc())
        # print(traceback.format_exc())
        output_2 = None

    return [output_1, output_2]


def run(in_dir, out_dir, lib, version, api_config, input_index):
    # parse api config
    api_name, sparse_key = api_config.split("-")

    argument = load_argument_file(in_dir, lib, version, api_name, input_index)
    log_file = get_log_file(out_dir, lib, version, 'rule_8', api_config, input_index)

    # get function pointers
    package = "tensorflow"
    mod = importlib.import_module(package)
    target_fun = get_func_ptr(mod, api_name)

    # run test
    [output_1, output_2] = test_rule_sparse(target_fun, argument, sparse_key, log_file)

    save_output_data([output_1, output_2], out_dir, lib, version, 'rule_8', api_config, input_index)

    return output_1 is not None and output_2 is not None


if __name__ == "__main__":
    main(run)
