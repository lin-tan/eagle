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


def test_rule_implement_seperable_with_conv(input, argument, origin_fun, target_fun_depth, target_fun_conv, log_file):
    seed = 0

    # fix seed
    tf.random.set_seed(seed)
    random.seed(seed)
    np.random.seed(seed)

    # run seperable function
    try:
        layer_1 = origin_fun(**argument)
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

    # run convolution function
    # separable function can be regarded as a depthwise convolution followed by a convolution
    try:
        depthwise_arg = {}
        conv_arg = {}
        for key, value in argument.items():
            if key == "filters":
                conv_arg[key] = value
            elif key == "kernel_size":
                depthwise_arg[key] = value
                conv_arg[key] = (1, 1)
            elif key.startswith("strides"):
                depthwise_arg[key] = value
                conv_arg[key] = (1, 1)
            elif key == "depth_multiplier":
                depthwise_arg[key] = value
            elif key.startswith("depthwise"):
                depthwise_arg[key] = value
            elif key.startswith("pointwise"):
                new_key = key.replace("pointwise", "kernel")
                conv_arg[new_key] = value
            else:
                conv_arg[key] = value
                depthwise_arg[key] = value

        if len(layer_1.get_weights()) == 3:
            weight_1, weight_2, bias = layer_1.get_weights()
        elif len(layer_1.get_weights()) == 2:
            weight_1, weight_2 = layer_1.get_weights()
            bias = np.zeros(weight_2.shape[-1])
        else:
            raise Exception('Unknown weights')
        # print(weight_1.shape, weight_2.shape, bias.shape)
        dim_k_size, _, dim_in_channel, dim_out_multiplier = weight_1.shape

        # depthwise convolution
        depthwiseconv_layer = target_fun_depth(**depthwise_arg)
        # print(depthwise_arg)
        depthwise_result = depthwiseconv_layer(input)
        zero_bias = np.zeros(dim_in_channel * dim_out_multiplier)
        depthwiseconv_layer.set_weights((weight_1, zero_bias))
        depthwise_result = depthwiseconv_layer(input)

        # convolution (pointwise)
        dim_k_size, _, dim_in_channel, filter = weight_2.shape
        conv_layer = target_fun_conv(**conv_arg)
        # print(conv_arg)
        output_2 = conv_layer(depthwise_result)
        conv_layer.set_weights((weight_2, bias))
        output_2 = conv_layer(depthwise_result)

    except:
        with open(log_file, "a+") as f:
            f.write(traceback.format_exc())
        # print(traceback.format_exc())
        output_2 = None

    #if output_1 is not None and output_2 is not None:
    #    print(output_1, output_2)
    #    print(np.max(np.abs(output_1 - output_2)))
    return [output_1, output_2]


def run(in_dir, out_dir, lib, version, api_config, input_index):
    # parse api config
    origin_fun_name, target_fun_1_name, target_fun_2_name = api_config.split('-')

    argument = load_argument_file(in_dir, lib, version, origin_fun_name, input_index)
    input_data = load_input_file(in_dir, input_index)
    log_file = get_log_file(out_dir, lib, version, 'rule_5', api_config, input_index)

    # get function pointers
    package = "tensorflow"
    mod = importlib.import_module(package)
    origin_fun = get_func_ptr(mod, origin_fun_name)
    mod = importlib.import_module(package)
    target_fun_1 = get_func_ptr(mod, target_fun_1_name)
    mod = importlib.import_module(package)
    target_fun_2 = get_func_ptr(mod, target_fun_2_name)

    # run test
    [output_1, output_2] = test_rule_implement_seperable_with_conv(input_data, argument, origin_fun, target_fun_1,
                                                                   target_fun_2, log_file)

    save_output_data([output_1, output_2], out_dir, lib, version, 'rule_5', api_config, input_index)

    return output_1 is not None and output_2 is not None


if __name__ == "__main__":
    main(run)
