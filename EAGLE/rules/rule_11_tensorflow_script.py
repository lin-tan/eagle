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
    # helper function to copy input_dict
    results = {}
    for key in input_dict:
        results[key] = input_dict[key]
    return results


def test_rule_dataset_map(input, fun, log_file):
    seed = 0
    # fix seed
    tf.random.set_seed(seed)
    random.seed(seed)
    np.random.seed(seed)

    # convert numpy argument to tf.constant
    for key in input:
        if isinstance(input[key], np.ndarray) or isinstance(input[key], list):
            input[key] = tf.constant(input[key])

    # run original function and input
    try:
        output1 = fun(**input)
    except Exception:
        with open(log_file, "a+") as f:
            f.write(traceback.format_exc())
        # print(traceback.format_exc())
        output1 = None

    # reset seed
    tf.random.set_seed(seed)
    random.seed(seed)
    np.random.seed(seed)

    # wrap input in Dataset
    try:
        if "image" in input.keys():
            image_key = "image"
        if "images" in input.keys():
            image_key = "images"
        if "input" in input.keys():
            image_key = "input"
        image_input = input[image_key]

        input_2 = copy_dict(input)
        input_2.pop(image_key)

        def fun_wrapper(image, args):
            return fun(image, **args)

        def generator():
            yield image_input

        data_type = image_input.dtype

        dataset = tf.data.Dataset.from_generator(generator, output_types=data_type)
        dataset = dataset.map(lambda image: fun_wrapper(image, input_2))
        output2 = next(iter(dataset))
    except Exception:
        with open(log_file, "a+") as f:
            f.write(traceback.format_exc())
        # print(traceback.format_exc())
        output2 = None

    return [output1, output2]


def run(in_dir, out_dir, lib, version, api_config, input_index):

    api_name = api_config

    argument = load_argument_file(in_dir, lib, version, api_name, input_index)
    # argument["image"] = np.random.randn(1, 6, 14, 3)
    # print(argument)
    log_file = get_log_file(out_dir, lib, version, 'rule_11', api_config, input_index)

    # get function pointers
    package = "tensorflow"
    mod = importlib.import_module(package)
    fun = get_func_ptr(mod, api_name)

    # run test
    [output_1, output_2] = test_rule_dataset_map(argument, fun, log_file)
    # print(output_1, output_2)
    # diff = np.abs(output_1 - output_2)
    # print(np.max(diff))
    # indicies = np.where(diff == np.max(diff))
    # index = []
    # for i in indicies:
    #     index.append(i[0])
    # print(index)
    # print(output_1[index])
    # print(output_2[index])
    # eq_result = np.equal(output_1, output_2)
    # print(np.sum(eq_result))
    # print(np.max(argument["images"]))

    save_output_data([output_1, output_2], out_dir, lib, version, 'rule_11', api_config, input_index)

    return output_1 is not None and output_2 is not None


if __name__ == "__main__":
    main(run)
