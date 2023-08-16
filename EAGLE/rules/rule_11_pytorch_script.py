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


def copy_dict(input_dict):
    # helper function to copy input_dict
    results = {}
    for key in input_dict:
        results[key] = input_dict[key]
    return results


def test_rule_dataset_map(input_data, argument, target_fun, log_file):
    seed = 0
    # fix seed
    torch.manual_seed(seed)
    random.seed(seed)
    np.random.seed(seed)

    # run original function and input
    try:
        if "img" in argument.keys():
            output_1_t = target_fun(**argument)
        else:
            layer_1 = target_fun(**argument)
            layer_1.eval()
            output_1_t = layer_1(input_data)
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
    # wrap input in Dataset
    try:
        if "img" in argument.keys():
            image_key = "img"
            input_data = argument[image_key]

            argument_2 = copy_dict(argument)
            argument_2.pop(image_key)

            def fun_wrapper(image):
                return target_fun(img=image, **argument_2)
        else:
            def fun_wrapper(image):
                layer_2 = target_fun(**argument)
                layer_2.eval()
                return layer_2(image)

        class MyDataset(Dataset):
            def __init__(self, image):
                self.x = image

            def __len__(self):
                return 1

            def __getitem__(self, index):
                return fun_wrapper(self.x)

        dataset = MyDataset(input_data)
        loader = DataLoader(dataset, num_workers=1)
        output_2_t = next(iter(loader))

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
    log_file = get_log_file(out_dir, lib, version, 'rule_11', api_config, input_index)

    if len(input_data.shape) > 3:
        input_data = input_data[0]
    if input_data.shape[0] > 3:
        input_data = input_data[:3]
    input_data = torch.tensor(input_data)

    if "img" in argument.keys() and isinstance(argument["img"], np.ndarray):
        if len(argument["img"].shape) > 3:
            argument["img"] = argument["img"][0]
        argument["img"] = torch.tensor(argument["img"])

    # get function pointers
    package = "torch"
    mod = importlib.import_module(package)
    fun = get_func_ptr(mod, api_name)

    # run test
    [output_1, output_2] = test_rule_dataset_map(input_data, argument, fun, log_file)

    save_output_data([output_1, output_2], out_dir, lib, version, 'rule_11', api_config, input_index)

    return output_1 is not None and output_2 is not None


if __name__ == "__main__":
    main(run)
