import numpy as np
import tensorflow as tf
import traceback
import importlib
import random

from rules.equiv_util import get_func_ptr, main, load_argument_file, load_input_file, get_log_file, save_output_data


def test_rule_implement_2d_with_3d(input, argument, target_2d_fun, target_3d_fun, log_file):
    seed = 0
    # fix seed
    tf.random.set_seed(seed)
    random.seed(seed)
    np.random.seed(seed)

    try:
        layer_1 = target_2d_fun(**argument)
        output_1 = layer_1(input)
    except:
        with open(log_file, "a+") as f:
            f.write(traceback.format_exc())
        # print(traceback.format_exc())
        output_1 = None

    tf.random.set_seed(seed)
    random.seed(seed)
    np.random.seed(seed)

    try:
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

        # add an extra dimension of 1 to arguments and tensors
        input = tf.expand_dims(input, 1)
        if layer_type == "pooling":
            if "pool_size" in argument.keys():
                argument["pool_size"] = tf.expand_dims(argument["pool_size"], 0)
            else:
                argument["pool_size"] = (1, 2, 2)
            argument["strides"] = (1, dim_strides_height, dim_strides_width)
        elif layer_type == "convolution":
            if len(layer_1.get_weights()) == 2:
                (weight, bias) = layer_1.get_weights()
            elif len(layer_1.get_weights()) == 1:
                weight = layer_1.get_weights()[0]
                bias = np.zeros(weight.shape[-1])
            else:
                raise Exception("Unknown weights")
            new_weight = tf.expand_dims(weight, 0)
            filter = weight.shape[3]
            argument["kernel_size"] = new_weight.shape[:3]
            argument["strides"] = (1, dim_strides_height, dim_strides_width)

            if "dilation_rate" in argument.keys() and not isinstance(argument["dilation_rate"], int):
                argument["dilation_rate"] = tf.expand_dims(argument["dilation_rate"], 0)
        else:
            raise Exception("unknown function")

        # run function and input with 3d function
        layer_2 = target_3d_fun(**argument)
        output_2 = layer_2(input)
        if layer_type == "convolution":
            layer_2.set_weights((new_weight, bias))
            output_2 = layer_2(input)
        output_2 = tf.squeeze(output_2, axis=1)

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
    api_name_2d, api_name_3d = api_config.split('-')

    argument = load_argument_file(in_dir, lib, version, api_name_2d, input_index)

    input_data = load_input_file(in_dir, input_index)
    log_file = get_log_file(out_dir, lib, version, 'rule_3', api_config, input_index)

    # get function pointers
    package = "tensorflow"
    mod = importlib.import_module(package)
    target_fun_2d = get_func_ptr(mod, api_name_2d)
    mod = importlib.import_module(package)
    target_fun_3d = get_func_ptr(mod, api_name_3d)

    # run test
    [output_1, output_2] = test_rule_implement_2d_with_3d(input_data, argument, target_fun_2d, target_fun_3d, log_file)

    save_output_data([output_1, output_2], out_dir, lib, version, 'rule_3', api_config, input_index)

    return output_1 is not None and output_2 is not None


if __name__ == "__main__":
    main(run)
