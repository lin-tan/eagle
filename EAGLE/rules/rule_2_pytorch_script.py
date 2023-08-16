import numpy as np
import torch
import traceback
import importlib
import random

from rules.equiv_util import get_func_ptr, main, load_argument_file, load_input_file, get_log_file, save_output_data


def test_rule_padding(input, argument, target_fun, log_file):
    seed = 0

    # fix seed 
    torch.manual_seed(seed)
    random.seed(seed)
    np.random.seed(seed)
    argument["stride"] = 1

    # run function and input with padding parameter set to same
    try:
        argument["padding"] = "same"
        layer_1 = target_fun(**argument)
        layer_1.eval()
        output_1_t = layer_1(input)
        output_1 = output_1_t.cpu().detach().numpy()
    except:
        with open(log_file, "a+") as f:
            f.write(traceback.format_exc())
        # print(traceback.format_exc())
        output_1 = None

    # reset seed
    torch.manual_seed(seed)
    random.seed(seed)
    np.random.seed(seed)

    # change padding parameter to valid and add paddding to input
    try:
        argument["padding"] = "valid"

        if isinstance(layer_1.stride, int):
            dim_strides_height = layer_1.stride
            dim_strides_width = dim_strides_height
        else:
            dim_strides_height, dim_strides_width = layer_1.stride

        (_, dim_in_height, dim_in_width, _) = input.shape

        if isinstance(layer_1.kernel_size, int):
            dim_filter_height = layer_1.kernel_size
            dim_filter_width = dim_filter_height
        else:
            (dim_filter_height, dim_filter_width) = layer_1.kernel_size

        if isinstance(layer_1.dilation, int):
            dilation = (layer_1.dilation, layer_1.dilation)
        else:
            dilation = layer_1.dilation

        kernel_size = (dim_filter_height, dim_filter_width)

        # calculate padding values
        padding_matrix = [0, 0] * len(kernel_size)
        for d, k, i in zip(dilation, kernel_size, range(len(kernel_size) - 1, -1, -1)):
            total_padding = d * (k - 1)
            left_pad = total_padding // 2
            padding_matrix[2 * i] = left_pad
            padding_matrix[2 * i + 1] = (total_padding - left_pad)

        # pad different constant value given different apis
        if isinstance(layer_1, torch.nn.Conv2d):
            input = torch.nn.functional.pad(input, padding_matrix, value=0)
        elif isinstance(layer_1, torch.nn.MaxPool2d):
            input = torch.nn.functional.pad(input, padding_matrix, value=np.NINF)
        else:
            raise Exception("unknown function")

        layer_2 = target_fun(**argument)
        layer_2.eval()
        output_2_t = layer_2(input)
        output_2 = output_2_t.cpu().detach().numpy()

    except:
        with open(log_file, "a+") as f:
            f.write(traceback.format_exc())
        # print(traceback.format_exc())
        output_2 = None

    #if output_1 is not None and output_2 is not None:
    #    print(output_1, output_2)
    #    print(np.max(np.abs(output_1-output_2)))
    return [output_1, output_2]


def run(in_dir, out_dir, lib, version, api_name, input_index):
    # load argument and input tensor file
    argument = load_argument_file(in_dir, lib, version, api_name, input_index)
    input_data = load_input_file(in_dir, input_index)
    input_data = torch.tensor(input_data)
    log_file = get_log_file(out_dir, lib, version, 'rule_2', api_name, input_index)

    # get function pointer
    package = "torch"
    mod = importlib.import_module(package)
    target_fun = get_func_ptr(mod, api_name)

    # run test
    [output_1, output_2] = test_rule_padding(input_data, argument, target_fun, log_file)

    save_output_data([output_1, output_2], out_dir, lib, version, 'rule_2', api_name, input_index)

    return output_1 is not None and output_2 is not None


if __name__ == "__main__":
    main(run)
