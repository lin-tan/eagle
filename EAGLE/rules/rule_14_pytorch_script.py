import numpy as np
import torch
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


def test_rule_pad_unpad(input, argument, pad_fun, unpad_fun, log_file):
    seed = 0
    # fix seed
    torch.manual_seed(seed)
    random.seed(seed)
    np.random.seed(seed)

    try:
        # pad input
        layer_1 = pad_fun(**argument)
        padded_input = layer_1(input)
        print(padded_input.shape)
        padding = argument["padding"]
        if isinstance(argument["padding"], int):
            padding = (argument["padding"], argument["padding"], argument["padding"], argument["padding"])
        elif len(argument["padding"]) == 4:
            padding = argument["padding"]

        padded_input_im = torchvision.transforms.ToPILImage()(padded_input).convert("RGB")

        # unpad input and compare
        argument_2 = {}  # convert argument accordingly
        argument_2["img"] = padded_input_im
        argument_2["top"] = padding[2]
        argument_2["left"] = padding[0]
        argument_2["height"] = input.shape[-2]
        argument_2["width"] = input.shape[-1]
        # print(argument_2)

        unpadded_input_im = unpad_fun(**argument_2)
        unpadded_input = torchvision.transforms.ToTensor()(unpadded_input_im)
        unpadded_input = (unpadded_input*255).to(torch.uint8)

        output_1 = input.cpu().detach().numpy()
        output_2 = unpadded_input.cpu().detach().numpy()
    except:
        with open(log_file, "a+") as f:
            f.write(traceback.format_exc())
        # print(traceback.format_exc())
        output_1 = None
        output_2 = None

    return [output_1, output_2]


def run(in_dir, out_dir, lib, version, api_config, input_index):
    # parse api config
    preprocess_line = api_config.split("-")
    pad_api_name = preprocess_line[0]
    unpad_api_name = preprocess_line[1]

    argument = load_argument_file(in_dir, lib, version, pad_api_name, input_index)
    input_data = load_input_file(in_dir, input_index)
    if len(input_data.shape) > 3:
        input_data = input_data[0]
    if input_data.shape[0] > 3:
        input_data = input_data[:3]
    input_data = torch.tensor(input_data).to(torch.uint8)

    log_file = get_log_file(out_dir, lib, version, 'rule_14', api_config, input_index)

    # get function pointers
    package = "torch"
    mod = importlib.import_module(package)
    pad_fun = get_func_ptr(mod, pad_api_name)
    mod = importlib.import_module(package)
    unpad_fun = get_func_ptr(mod, unpad_api_name)

    # run test
    [output_1, output_2] = test_rule_pad_unpad(input_data, argument, pad_fun, unpad_fun, log_file)

    save_output_data([output_1, output_2], out_dir, lib, version, 'rule_14', api_config, input_index)

    return output_1 is not None and output_2 is not None


if __name__ == "__main__":
    main(run)
