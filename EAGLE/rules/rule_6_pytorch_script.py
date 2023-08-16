import numpy as np
import torch
import traceback
import importlib
import random

from rules.equiv_util import get_func_ptr, main, load_argument_file, load_input_file, get_log_file, save_output_data


def test_rule_implement_dilated_with_conv(input, argument, target_fun, log_file):
    seed = 0
    # fix seed
    torch.manual_seed(seed)
    random.seed(seed)
    np.random.seed(seed)

    # run dilated convolution function
    try:
        layer_1 = target_fun(**argument)
        layer_1.eval()
        output_1_t = layer_1(input)
        output_1 = output_1_t.cpu().detach().numpy()
    except:
        with open(log_file, "a+") as f:
            f.write(traceback.format_exc())
        print(traceback.format_exc())
        output_1 = None

    # reset seed
    torch.manual_seed(seed)
    random.seed(seed)
    np.random.seed(seed)

    # run convolution function
    # dilated convolution function can be regarded as a convolution function with a mutated kernel 
    try:
        weight = layer_1.weight.data
        if layer_1.bias is not None:
            bias = layer_1.bias.data
        else:
            bias = torch.zeros(list(weight.size())[-1])

        (dim_batch_shape, dim_in_channel, dim_in_height, dim_in_width) = list(input.size())
        (dim_out_channels, _, dim_filter_height, dim_filter_width) = list(weight.size())
        if len(layer_1.dilation) == 0:
            rate_height = layer_1.dilation
            rate_width = layer_1.dilation
        else:
            (rate_height, rate_width) = layer_1.dilation
        dim_filter_height_dilated = dim_filter_height + (dim_filter_height - 1) * (rate_height - 1)
        dim_filter_width_dilated = dim_filter_width + (dim_filter_width - 1) * (rate_width - 1)

        # mutate kernel by adding zeros between original kernel elements
        weight_dilated = torch.zeros(
            (dim_out_channels, dim_in_channel, dim_filter_height_dilated, dim_filter_width_dilated))
        #print(dim_filter_height, dim_filter_width, (rate_height, rate_width), dim_filter_height_dilated, dim_filter_width_dilated)
        for i1 in range(dim_filter_height):
            for i2 in range(dim_filter_width):
                for i3 in range(dim_in_channel):
                    for i4 in range(dim_out_channels):
                        weight_dilated[i4, i3, i1 * rate_height, i2 * rate_width] = weight[i4, i3, i1, i2]

        argument["kernel_size"] = (dim_filter_height_dilated, dim_filter_width_dilated)
        argument["dilation"] = 1

        # run convolution with mutated kernel and original input
        conv_layer = target_fun(**argument)
        conv_layer.eval()
        conv_layer(input)
        conv_layer.weight = torch.nn.Parameter(weight_dilated)
        conv_layer.bias = torch.nn.Parameter(bias)
        output_2_t = conv_layer(input)
        output_2 = output_2_t.cpu().detach().numpy()

    except:
        with open(log_file, "a+") as f:
            f.write(traceback.format_exc())
        print(traceback.format_exc())
        output_2 = None

    #if output_1 is not None and output_2 is not None:
    #    print(output_1, output_2)
    #    print(np.max(np.abs(output_1-output_2)))
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
    input_data = torch.tensor(input_data)
    log_file = get_log_file(out_dir, lib, version, 'rule_6', api_arg_name, input_index)

    # get function pointers
    package = "torch"
    mod = importlib.import_module(package)
    target_fun = get_func_ptr(mod, api_name)

    # run test
    [output_1, output_2] = test_rule_implement_dilated_with_conv(input_data, argument, target_fun, log_file)

    save_output_data([output_1, output_2], out_dir, lib, version, 'rule_6', api_arg_name, input_index)

    return output_1 is not None and output_2 is not None


if __name__ == "__main__":
    main(run)
