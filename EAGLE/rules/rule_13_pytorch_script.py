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


def test_rule_decode_encode(argument, encode_fun, decode_fun, image_save_file, log_file):
    seed = 0
    # fix seed
    torch.manual_seed(seed)
    random.seed(seed)
    np.random.seed(seed)

    try:
        # encode input tensor to image
        argument["input"] = argument["input"].to(torch.uint8)
        encoded_file = encode_fun(**argument)
        torchvision.io.write_file(image_save_file, encoded_file)
        
        # decode image to tensor
        encoded_file = torchvision.io.read_file(image_save_file)
        input_decoded = decode_fun(encoded_file)
        output_1 = argument["input"].cpu().detach().numpy()
        output_2 = input_decoded.cpu().detach().numpy()
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
    encode_fun_name = preprocess_line[0]
    decode_fun_name = preprocess_line[1]

    argument = load_argument_file(in_dir, lib, version, encode_fun_name, input_index)
    argument["input"] = torch.Tensor(argument["input"])
    input_data = load_input_file(in_dir, input_index)
    log_file = get_log_file(out_dir, lib, version, 'rule_13', api_config, input_index)

    # get function pointer
    package = "torchvision"
    mod = importlib.import_module(package)
    encode_fun = get_func_ptr(mod, encode_fun_name)
    mod = importlib.import_module(package)
    decode_fun = get_func_ptr(mod, decode_fun_name)

    image_save_file = "/tmp/encoded_image"
    # run test
    [output_1, output_2] = test_rule_decode_encode(argument, encode_fun, decode_fun, image_save_file, log_file)

    save_output_data([output_1, output_2], out_dir, lib, version, 'rule_13', api_config, input_index)

    return output_1 is not None and output_2 is not None


if __name__ == "__main__":
    main(run)
