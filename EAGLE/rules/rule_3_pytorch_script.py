import numpy as np
import torch
import traceback
import importlib
import random

from rules.equiv_util import get_func_ptr, main, load_argument_file, load_input_file, get_log_file, save_output_data


def test_rule_implement_2d_with_3d(input, argument, target_2d_fun, target_3d_fun, log_file):
    seed = 0
    # fix seed
    torch.manual_seed(seed)
    random.seed(seed)
    np.random.seed(seed)

    # run function and input with 2d function
    try:
        layer_1 = target_2d_fun(**argument)
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

    # implement 2d function using its 3d version
    try:
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

        # add an extra dimension of 1 to arguments and tensors
        argument["stride"] = (1, dim_strides_height, dim_strides_width)
        argument["kernel_size"] = (1, dim_filter_height, dim_filter_width)
        if "dilation_rate" in argument.keys() and not isinstance(argument["dilation_rate"], int):
            if isinstance(layer_1.dilation, int):
                dilation = (layer_1.dilation, layer_1.dilation)
            else:
                dilation = layer_1.dilation
            argument["dilation_rate"] = (1, dilation[0], dilation[1])

        input = torch.unsqueeze(input, 2)
        # print(input.shape)

        # run function and input with 3d function
        layer_2 = target_3d_fun(**argument)
        layer_2.eval()
        output_2_t = layer_2(input)
        if isinstance(layer_1, torch.nn.Conv2d):
            weight = layer_1.weight.data
            new_weight = torch.unsqueeze(weight, 2)
            layer_2.weight = torch.nn.Parameter(new_weight)
            if layer_1.bias is not None:
                bias = layer_1.bias.data
                layer_2.bias = torch.nn.Parameter(bias)
            output_2_t = layer_2(input)
        output_2_t = torch.squeeze(output_2_t, 2)
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


def run(in_dir, out_dir, lib, version, api_config, input_index):
    # parse api config
    api_name_2d, api_name_3d = api_config.split('-')

    argument = load_argument_file(in_dir, lib, version, api_name_2d, input_index)

    input_data = load_input_file(in_dir, input_index)
    input_data = torch.tensor(input_data)
    log_file = get_log_file(out_dir, lib, version, 'rule_3', api_config, input_index)

    # get function pointers
    package = "torch"
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
