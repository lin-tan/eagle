import numpy as np
import torch
import traceback
import importlib
import random

from rules.equiv_util import get_func_ptr, main, load_argument_file, load_input_file, get_log_file, save_output_data


def test_rule_implement_batchnorm(input, argument, target_fun, log_file):
    seed = 0
    # fix seed
    torch.manual_seed(seed)
    random.seed(seed)
    np.random.seed(seed)

    # run batchnorm
    try:
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

    # run implementation according to the formula
    try:
        reduce_dim = [0]
        i = 2
        while i < len(list(input.size())):
            reduce_dim.append(i)
            i += 1

        if layer_1.weight is not None:
            gamma = layer_1.weight
        else:
            gamma = torch.ones(argument["num_features"])

        if layer_1.bias is not None:
            beta = layer_1.bias
        else:
            beta = torch.zeros(argument["num_features"])

        if layer_1.running_mean is not None and layer_1.running_var is not None:
            mean = layer_1.running_mean
            variance = layer_1.running_var
        else:
            mean = torch.mean(input, dim=reduce_dim)
            variance = torch.var(input, dim=reduce_dim, unbiased=False)

        shape = list(input.size())
        for dim in reduce_dim:
            shape[dim] = 1

        mean = torch.reshape(mean, shape)
        variance = torch.reshape(variance, shape)
        gamma = torch.reshape(gamma, shape)
        beta = torch.reshape(beta, shape)

        epsilon = layer_1.eps

        # batchnorm formula: (input - mean) / sqrt(variance + epsilon) * gamma + beta
        output_2_t = torch.div(input - mean, torch.sqrt(variance + epsilon)) * gamma + beta
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

    argument = load_argument_file(in_dir, lib, version, api_name, input_index)
    input_data = load_input_file(in_dir, input_index)
    input_data = torch.tensor(input_data)
    log_file = get_log_file(out_dir, lib, version, 'rule_7', api_name, input_index)

    # get function pointers
    package = "torch"
    mod = importlib.import_module(package)
    target_fun = get_func_ptr(mod, api_name)

    # run test
    [output_1, output_2] = test_rule_implement_batchnorm(input_data, argument, target_fun, log_file)

    save_output_data([output_1, output_2], out_dir, lib, version, 'rule_7', api_name, input_index)

    return output_1 is not None and output_2 is not None


if __name__ == "__main__":
    main(run)
