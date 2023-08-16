import numpy as np
import torch
from torch.utils.data import Dataset, DataLoader
import torchvision
import os
from datetime import datetime
import argparse
import traceback
import pickle
import importlib
import random
from timeit import default_timer as timer

from rules.equiv_util import get_func_ptr, main, load_argument_file, load_input_file, get_log_file, save_output_data

def test_rule_image_norm(input, argument, target_fun, functional, log_file):
    seed = 0
    # fix seed
    torch.manual_seed(seed)
    random.seed(seed)
    np.random.seed(seed)

    # run original function and input
    try:
        if functional:
            output_1_t = target_fun(**argument)
        else:
            layer_1 = target_fun(**argument)
            output_1_t = layer_1(input)
            # print(output_1_t)
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

    # print("here1")
    # run normalized function and input
    try:
        if functional:
            if "tensor" in argument.keys():
                image_key = "tensor"
            else:
                raise Exception("didn't find the image argument in functional function")
            image_input = argument[image_key]

            argument_2 = argument
            if torch.max(image_input) > 1.001:
                # if the image is between 0 and 255, then normalize it to [0.0, 1.0]
                image_input /= 255.0
            else:
                # if the image is between 0.0 and 1.0, then normalize it to [0, 255]
                image_input *= 255.0
            argument_2["mean"] = torch.mean(image_input, dim=[1, 2])
            argument_2["std"] = torch.std(image_input, dim=[1, 2], unbiased=False)
            argument_2[image_key] = image_input
            output_2_t = target_fun(**argument_2)
        else:
            if torch.max(input) > 1.001:
                # if the image is between 0 and 255, then normalize it to [0.0, 1.0]
                input /= 255.0
            else:
                # if the image is between 0.0 and 1.0, then normalize it to [0, 255]
                input *= 255.0
            argument["mean"] = torch.mean(input, dim=[1, 2])
            argument["std"] = torch.std(input, dim=[1, 2], unbiased=False)
            layer_2 = target_fun(**argument)
            output_2_t = layer_2(input)
        # print(output_2_t)

        output_2 = output_2_t.cpu().detach().numpy()
    except:
        with open(log_file, "a+") as f:
            f.write(traceback.format_exc())
        # print(traceback.format_exc())
        output_2 = None

    return [output_1, output_2]


def run(in_dir, out_dir, lib, version, api_config, input_index):

    api_name = api_config

    argument = load_argument_file(in_dir, lib, version, api_name, input_index)
    input_data = load_input_file(in_dir, input_index)
    log_file = get_log_file(out_dir, lib, version, 'rule_9', api_config, input_index)

    if len(input_data.shape) > 3:
        input_data = input_data[0]
    if input_data.shape[0] > 3:
        input_data = input_data[:3]
    input_data = torch.tensor(input_data)

    # if img in arguments, then the api is a functional api, otherwise it is a class api.
    if "img" in argument.keys() and isinstance(argument["img"], np.ndarray):
        argument["img"] = torch.tensor(argument["img"])
        functional = True
    else:
        functional = False

    # get function pointers
    package = "torch"
    mod = importlib.import_module(package)
    target_fun = get_func_ptr(mod, api_name)

    # run test
    [output_1, output_2] = test_rule_image_norm(input_data, argument, target_fun, functional, log_file)

    save_output_data([output_1, output_2], out_dir, lib, version, 'rule_9', api_config, input_index)

    return output_1 is not None and output_2 is not None


if __name__ == "__main__":
    main(run)
