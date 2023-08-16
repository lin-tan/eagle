import numpy as np
import torch
import traceback
import importlib
import random

from rules.equiv_util import get_func_ptr, main, load_argument_file, load_input_file, get_log_file, save_output_data


def test_rule_implement_depthwise_with_conv(input, argument, origin_fun, target_fun, log_file):
    seed = 0
    # fix seed
    torch.manual_seed(seed)
    random.seed(seed)
    np.random.seed(seed)

    # run depthwise function
    try:
        layer_1 = origin_fun(**argument)
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
 
    # run convolution function
    # depthwise function can be regarded as doing separate convolutions for each group of channels
    try:
        dim_out_multiplier = int(argument["out_channels"] / argument["in_channels"])
        dim_in_channel = argument["in_channels"]
        dim_out_channel = argument["out_channels"]
        input_split_size = int(dim_in_channel / argument["groups"])
        output_split_size = int(dim_out_channel / argument["groups"])

        weight = layer_1.weight.data
        if layer_1.bias is not None:
            bias = layer_1.bias.data
        else:
            bias = torch.zeros(list(weight.size())[-1])

        # split input, weight and bias on channel dimension
        split_input = torch.split(input, input_split_size, dim=1)
        split_weight = torch.split(weight, output_split_size, dim=0)
        if len(bias) % dim_in_channel == 0:
            split_bias = torch.split(bias, output_split_size, dim=-1)
        elif len(bias) == dim_out_multiplier:
            split_bias = [bias for i in range(dim_in_channel)]
        else:
            raise Exception("Unkown bias")

        argument["in_channels"] = 1
        argument["out_channels"] = dim_out_multiplier
        argument["groups"] = 1

        # run convolutions for each group of input channels
        result_list = []
        for i in range(len(split_input)):
            conv_layer = target_fun(**argument)
            conv_layer.eval()
            conv_item = conv_layer(split_input[i])
            conv_layer.weight = torch.nn.Parameter(split_weight[i])
            conv_layer.bias = torch.nn.Parameter(split_bias[i])
            result = conv_layer(split_input[i])
            #print(split_input[i].size())
            #print(split_weight[i].size())
            #print(split_bias[i].size())
            #print(result.size())
            result_list.append(result)
        output_2_t = torch.cat(result_list, dim=1)
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
    origin_fun_name, target_fun_name = api_config.split('-')

    argument = load_argument_file(in_dir, lib, version, origin_fun_name, input_index)
    input_data = load_input_file(in_dir, input_index)
    input_data = torch.tensor(input_data)
    log_file = get_log_file(out_dir, lib, version, 'rule_4', api_config, input_index)

    if not "groups" in argument:
        argument["groups"] = 1

    # get function pointers
    package = "torch"
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
