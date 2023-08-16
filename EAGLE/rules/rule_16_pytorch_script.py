import numpy as np
import torch
import os
from datetime import datetime
import argparse
import traceback
import pickle
import importlib
import random
from timeit import default_timer as timer
import subprocess

from rules.equiv_util import get_func_ptr, main, load_argument_file, load_input_file, load_image_file, get_log_file, save_output_data

# larger time out since this rule performs on models
TIMEOUT = 300

def test_rule_model_save(model_class, test_x, save_load_mode, model_save_path, log_file):
    seed = 0
    # fix seed
    torch.manual_seed(seed)
    random.seed(seed)
    np.random.seed(seed)

    # evaluate model
    model = model_class(pretrained=True)
    model.eval()

    try:
        output_1 = model(test_x)
        stat_dict_1 = model.state_dict()
        output_1_np = output_1.cpu().detach().numpy()
    except:
        with open(log_file, "a") as f:
            f.write(traceback.format_exc())
        # print(traceback.format_exc())
        output_1_np = None
        stat_dict_1 = None

    # save models to file and load them back
    try:
        if save_load_mode == 'model':
            torch.save(model, model_save_path)
            reconstructed_model = torch.load(model_save_path)
            reconstructed_model.eval()
        elif save_load_mode == "state_dict":
            torch.save(model.state_dict(), model_save_path)
            reconstructed_model = model_class()
            reconstructed_model.load_state_dict(torch.load(model_save_path))
            reconstructed_model.eval()
        else:
            raise Exception("Unkown save and load mode")
    except Exception as e:
        # print(e)
        with open(log_file, "a") as f:
            f.write(traceback.format_exc())

    # reset seed
    torch.manual_seed(seed)
    random.seed(seed)
    np.random.seed(seed)

    # evaluate model again
    try:
        output_2 = reconstructed_model(test_x)
        stat_dict_2 = reconstructed_model.state_dict()
        output_2_np = output_2.cpu().detach().numpy()
    except:
        with open(log_file, "a+") as f:
            f.write(traceback.format_exc())
        # print(traceback.format_exc())
        output_2_np = None
        stat_dict_2 = None

    return [[output_1_np, stat_dict_1], [output_2_np, stat_dict_2]]


def run(in_dir, out_dir, lib, version, api_config, input_index):
    # parse api config
    preprocess_line = api_config.split("-")
    model_path = preprocess_line[0]
    input_file = preprocess_line[1]
    save_load_mode = preprocess_line[2]

    # argument = load_argument_file(in_dir, lib, version, api_name, input_index)
    log_file = get_log_file(out_dir, lib, version, 'rule_16', api_config, input_index)
    test_x, test_y = load_image_file(in_dir, lib, version, input_file)

    # get function pointer
    package = "torchvision"
    mod = importlib.import_module(package)
    model_class = get_func_ptr(mod, model_path)

    test_x = torch.tensor(test_x).to(torch.float)

    tmp_model_path = "/tmp/tmp_models_{}".format(api_config)

    # run test
    [output_1, output_2] = test_rule_model_save(model_class, test_x, save_load_mode, tmp_model_path, log_file)

    # [[output_1_np, stat_dict_1], [output_2_np, stat_dict_2]] = [output_1, output_2]
    # print(np.allclose(output_1_np, output_2_np))
    # print(np.max(np.abs(output_1_np - output_2_np)))

    save_output_data([output_1, output_2], out_dir, lib, version, 'rule_16', api_config, input_index)

    delete_command = "rm -r " + tmp_model_path
    subprocess.call(delete_command, shell=True)

    return output_1 is not None and output_2 is not None


if __name__ == "__main__":
    main(run, TIMEOUT)
