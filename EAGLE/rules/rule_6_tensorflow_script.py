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


def test_rule_implement_dilated_with_conv(input, argument, target_fun, log_file):
    seed = 0
    # fix seed
    tf.random.set_seed(seed)
    random.seed(seed)
    np.random.seed(seed)

    # run dilated convolution function
    try:
        layer_1 = target_fun(**argument)
        output_1 = layer_1(input)
    except:
        with open(log_file, "a+") as f:
            f.write(traceback.format_exc())
        print(traceback.format_exc())
        output_1 = None

    # reset seed
    tf.random.set_seed(seed)
    random.seed(seed)
    np.random.seed(seed)

    # run convolution function
    # dilated convolution function can be regarded as a convolution function with a mutated kernel 
    try:
        if len(layer_1.get_weights()) == 2:
            weight, bias = layer_1.get_weights()
        elif len(layer_1.get_weights()) == 1:
            weight = layer_1.get_weights()[0]
            bias = np.zeros(weight.shape[-1])
        else:
            raise Exception('Unknown weights')

        (dim_batch_shape, dim_in_height, dim_in_width, dim_in_channel) = input.shape
        (dim_filter_height, dim_filter_width, _, dim_out_channels) = weight.shape
        if len(layer_1.dilation_rate) == 0:
            rate_height = layer_1.dilation_rate
            rate_width = layer_1.dilation_rate
        else:
            (rate_height, rate_width) = layer_1.dilation_rate
        dim_filter_height_dilated = dim_filter_height + (dim_filter_height - 1) * (rate_height - 1)
        dim_filter_width_dilated = dim_filter_width + (dim_filter_width - 1) * (rate_width - 1)

        # mutate kernel by adding zeros between original kernel elements
        weight_dilated = np.zeros(
            (dim_filter_height_dilated, dim_filter_width_dilated, dim_in_channel, dim_out_channels))
        # print(dim_filter_height, dim_filter_width, (rate_height, rate_width), dim_filter_height_dilated,dim_filter_width_dilated)
        for i1 in range(dim_filter_height):
            for i2 in range(dim_filter_width):
                for i3 in range(dim_in_channel):
                    for i4 in range(dim_out_channels):
                        weight_dilated[i1 * rate_height, i2 * rate_width, i3, i4] = weight[i1, i2, i3, i4]

        argument["kernel_size"] = (dim_filter_height_dilated, dim_filter_width_dilated)
        argument["dilation_rate"] = 1

        # run convolution with mutated kernel and original input
        conv_layer = target_fun(**argument)
        output_2 = conv_layer(input)
        conv_layer.set_weights((weight_dilated, bias))
        output_2 = conv_layer(input)

    except:
        with open(log_file, "a+") as f:
            f.write(traceback.format_exc())
        # print(traceback.format_exc())
        output_2 = None

    #if output_1 is not None and output_2 is not None:
    #    print(output_1, output_2)
    #    print(np.max(np.abs(output_1 - output_2)))
    return [output_1, output_2]


def run(in_dir, out_dir, lib, version, api_arg_name, input_index):
    # parse api config
    # * in api name represents a custom constraints added manually. The purpose is to increase the input valid rate. 
    if '*' in api_arg_name:
        api_name, _ = api_arg_name.split('*')
    else:
        api_name = api_arg_name

    argument = load_argument_file(in_dir, lib, version, api_arg_name, input_index)
    input_data = load_input_file(in_dir, input_index)
    log_file = get_log_file(out_dir, lib, version, 'rule_6', api_arg_name, input_index)

    # get function pointers
    package = "tensorflow"
    mod = importlib.import_module(package)
    target_fun = get_func_ptr(mod, api_name)

    # run test
    [output_1, output_2] = test_rule_implement_dilated_with_conv(input_data, argument, target_fun, log_file)

    save_output_data([output_1, output_2], out_dir, lib, version, 'rule_6', api_arg_name, input_index)

    return output_1 is not None and output_2 is not None


if __name__ == "__main__":
    main(run)
