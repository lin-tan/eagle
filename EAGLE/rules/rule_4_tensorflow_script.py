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


def test_rule_implement_depthwise_with_conv(input, argument, origin_fun, target_fun, log_file):
    seed = 0
    # fix seed
    tf.random.set_seed(seed)
    random.seed(seed)
    np.random.seed(seed)

    # run depthwise function
    try:
        layer_1 = origin_fun(**argument)
        output_1 = layer_1(input)
    except:
        with open(log_file, "a+") as f:
            f.write(traceback.format_exc())
        # print(traceback.format_exc())
        output_1 = None

    tf.random.set_seed(seed)
    random.seed(seed)
    np.random.seed(seed)

    # run convolution function
    # depthwise function can be regarded as doing separate convolutions for each group of channels
    try:
        old_value_list = ["depth_multiplier"]
        new_value_list = ["filters"]
        for old_value, new_value in zip(old_value_list, new_value_list):
            if old_value in argument.keys():
                argument[new_value] = dict.pop(old_value, None)
        if "filters" not in argument.keys():
            argument["filters"] = 1

        if len(layer_1.get_weights()) == 2:
            weight, bias = layer_1.get_weights()
        elif len(layer_1.get_weights()) == 1:
            weight = layer_1.get_weights()[0]
            bias = np.zeros(weight.shape[-1])
        else:
            raise Exception("Unknown weights")

        dim_k_size, _, dim_in_channel, dim_out_multiplier = weight.shape

        # split input, weight and bias on channel dimension
        split_input = tf.split(input, dim_in_channel, axis=-1)
        split_weight = tf.split(weight, dim_in_channel, axis=-2)
        if len(bias) % dim_in_channel == 0:
            split_bias = tf.split(bias, dim_in_channel, axis=-1)
        elif len(bias) == dim_out_multiplier:
            split_bias = [bias for i in range(dim_in_channel)]
        else:
            raise Exception("Unkown bias")

        # run convolutions for each group of input channels
        result_list = []
        for i in range(len(split_input)):
            conv_layer = target_fun(**argument)
            conv_item = conv_layer(split_input[i])
            conv_layer.set_weights((split_weight[i], split_bias[i]))
            result = conv_layer(split_input[i])
            result_list.append(result)
        concat_layer = tf.keras.layers.Concatenate(axis=-1)
        output_2 = concat_layer(result_list)

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
    origin_fun_name, target_fun_name = api_config.split('-')

    argument = load_argument_file(in_dir, lib, version, origin_fun_name, input_index)
    input_data = load_input_file(in_dir, input_index)
    log_file = get_log_file(out_dir, lib, version, 'rule_4', api_config, input_index)

    # get function pointers
    package = "tensorflow"
    mod = importlib.import_module(package)
    origin_fun = get_func_ptr(mod, origin_fun_name)
    mod = importlib.import_module(package)
    target_fun = get_func_ptr(mod, target_fun_name)

    # run test
    [output_1, output_2] = test_rule_implement_depthwise_with_conv(input_data, argument, origin_fun, target_fun,
                                                                   log_file)

    save_output_data([output_1, output_2], out_dir, lib, version, 'rule_4', api_config, input_index)

    return output_1 is not None and output_2 is not None


if __name__ == "__main__":
    main(run)
