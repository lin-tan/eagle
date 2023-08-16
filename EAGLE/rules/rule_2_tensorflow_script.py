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


def test_rule_padding(input, argument, target_fun, log_file):
    seed = 0

    # fix seed 
    tf.random.set_seed(seed)
    random.seed(seed)
    np.random.seed(seed)

    # run function and input with padding set to same
    try:
        argument["padding"] = "same"
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

    # change padding parameter to valid and add paddding to input
    try:
        argument["padding"] = "valid"

        if isinstance(layer_1.strides, int):
            dim_strides_height = layer_1.strides
            dim_strides_width = dim_strides_height
        else:
            dim_strides_height, dim_strides_width = layer_1.strides

        (_, dim_in_height, dim_in_width, _) = input.shape

        if hasattr(layer_1, 'pool_size'):
            layer_type = "pooling"
            if isinstance(layer_1.pool_size, int):
                dim_filter_height = layer_1.pool_size
                dim_filter_width = dim_filter_height
            else:
                (dim_filter_height, dim_filter_width) = layer_1.pool_size
        elif hasattr(layer_1, 'get_weights'):
            layer_type = "convolution"
            if len(layer_1.get_weights()) == 2:
                (weight, bias) = layer_1.get_weights()
            elif len(layer_1.get_weights()) == 1:
                weight = layer_1.get_weights()[0]
                bias = np.zeros(weight.shape[-1])
            else:
                raise Exception('unknown weights')
            filter = weight.shape[3]

            (dim_filter_height, dim_filter_width, _, _) = weight.shape
        else:
            raise Exception("unknown function")

        # calculate padding values
        if dim_in_height % dim_strides_height == 0:
            pad_along_height = max((dim_filter_height - dim_strides_height), 0)
        else:
            pad_along_height = max(dim_filter_height - (dim_in_height % dim_strides_height), 0)

        if dim_in_width % dim_strides_width == 0:
            pad_along_width = max((dim_filter_width - dim_strides_width), 0)
        else:
            pad_along_width = max(dim_filter_width - (dim_in_width % dim_strides_width), 0)

        pad_top = pad_along_height // 2
        pad_bottom = pad_along_height - pad_top
        pad_left = pad_along_width // 2
        pad_right = pad_along_width - pad_left

        # pad different constant value given different apis
        if layer_type == "pooling":
            input = tf.pad(input, ((0, 0), (pad_top, pad_bottom), (pad_left, pad_right), (0, 0)),
                           mode='CONSTANT',
                           constant_values=np.NINF)
        elif layer_type == "convolution":
            new_pad_layer = tf.keras.layers.ZeroPadding2D(padding=((pad_top, pad_bottom), (pad_left, pad_right)),
                                                          name='padding')
            input = new_pad_layer(input)
        else:
            raise Exception("unknown function")

        layer_2 = target_fun(**argument)
        output_2 = layer_2(input)

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
    # load argument and input tensor file
    argument = load_argument_file(in_dir, lib, version, api_name, input_index)
    input_data = load_input_file(in_dir, input_index)
    log_file = get_log_file(out_dir, lib, version, 'rule_2', api_name, input_index)

    # get function pointer
    package = "tensorflow"
    mod = importlib.import_module(package)
    target_fun = get_func_ptr(mod, api_name)

    # run test
    [output_1, output_2] = test_rule_padding(input_data, argument, target_fun, log_file)

    save_output_data([output_1, output_2], out_dir, lib, version, 'rule_2', api_name, input_index)

    return output_1 is not None and output_2 is not None


if __name__ == "__main__":
    main(run)