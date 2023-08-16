import numpy as np
import tensorflow as tf
import os
from datetime import datetime
import argparse
import traceback
import pickle
import importlib
import random

from rules.equiv_util import get_func_ptr, main, load_argument_file, load_input_file, get_log_file, save_output_data


def test_rule_implement_batchnorm(input, argument, target_fun, log_file):
    seed = 0
    # fix seed
    tf.random.set_seed(seed)
    random.seed(seed)
    np.random.seed(seed)

    # run batchnorm
    try:
        layer_1 = target_fun(**argument)
        output_1 = layer_1(input)
    except:
        with open(log_file, "a+") as f:
            f.write(traceback.format_exc())
        # print(traceback.format_exc())
        output_1 = None

    # reset seed
    tf.random.set_seed(seed)
    random.seed(seed)
    np.random.seed(seed)

    # run implementation according to the formula
    try:
        if len(layer_1.get_weights()) == 4:
            (gamma, beta, mean, variance) = layer_1.get_weights()
        elif len(layer_1.get_weights()) == 3:
            mean = np.array(layer_1.moving_mean)
            variance = np.array(layer_1.moving_variance)
            gamma = layer_1.gamma
            if gamma is None:
                gamma = np.ones(mean.shape)
            else:
                gamma = np.array(gamma)
            beta = layer_1.beta
            if beta is None:
                beta = np.zeros(mean.shape)
            else:
                beta = np.array(beta)
        else:
            raise Exception("unknown batchnorm weights")
        epsilon = layer_1.epsilon

        # batchnorm formula: (input - mean) / sqrt(variance + epsilon) * gamma + beta
        output_2 = tf.divide(input - mean, tf.sqrt(variance + epsilon)) * gamma + beta

    except:
        with open(log_file, "a+") as f:
            f.write(traceback.format_exc())
        # print(traceback.format_exc())
        output_2 = None

    #if output_1 is not None and output_2 is not None:
    #    print(output_1, output_2)
    #    print(np.max(np.abs(output_1 - output_2)))
    return [output_1, output_2]


def run(in_dir, out_dir, lib, version, api_name, input_index):

    argument = load_argument_file(in_dir, lib, version, api_name, input_index)
    input_data = load_input_file(in_dir, input_index)
    log_file = get_log_file(out_dir, lib, version, 'rule_7', api_name, input_index)

    # get function pointers
    package = "tensorflow"
    mod = importlib.import_module(package)
    target_fun = get_func_ptr(mod, api_name)

    # run test
    [output_1, output_2] = test_rule_implement_batchnorm(input_data, argument, target_fun, log_file)

    save_output_data([output_1, output_2], out_dir, lib, version, 'rule_7', api_name, input_index)

    return output_1 is not None and output_2 is not None


if __name__ == "__main__":
    main(run)
