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


def test_rule_image_norm(input, fun, log_file):
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

    # run normalized function and input
    try:
        if "image" in input.keys():
            image_key = "image"
        elif "images" in input.keys():
            image_key = "images"
        elif "input" in input.keys():
            image_key = "input"
        else:
            raise Exception
        image_input = input[image_key]

        input_2 = input
        if np.max(image_input) > 1.5:
            # if the image is between 0 and 255, then normalize it to [0.0, 1.0]
            image_input /= 255.0
        else:
            # if the image is between 0.0 and 1.0, then normalize it to [0, 255]
            image_input *= 255.0
        input_2[image_key] = image_input
        output2 = fun(**input)
    except Exception:
        with open(log_file, "a+") as f:
            f.write(traceback.format_exc())
        # print(traceback.format_exc())
        output2 = None

    return [output1, output2]


def run(in_dir, out_dir, lib, version, api_config, input_index):

    api_name = api_config

    argument = load_argument_file(in_dir, lib, version, api_name, input_index)
    # argument["images"] = np.random.randn(6, 14, 3)
    # print(argument)
    log_file = get_log_file(out_dir, lib, version, 'rule_9', api_config, input_index)

    # get function pointers
    package = "tensorflow"
    mod = importlib.import_module(package)
    fun = get_func_ptr(mod, api_name)

    # run test
    [output_1, output_2] = test_rule_image_norm(argument, fun, log_file)

    save_output_data([output_1, output_2], out_dir, lib, version, 'rule_9', api_config, input_index)

    return output_1 is not None and output_2 is not None


if __name__ == "__main__":
    main(run)
