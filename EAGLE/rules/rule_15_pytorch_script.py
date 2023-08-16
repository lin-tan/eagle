import numpy as np
import torch
from torch.utils.data import Dataset, DataLoader
import os
from datetime import datetime
import argparse
import traceback
import pickle
import importlib
import random
from timeit import default_timer as timer

from rules.equiv_util import get_func_ptr, main, load_argument_file, load_input_file, load_image_file, get_log_file, save_output_data

# larger time out since this rule performs on models
TIMEOUT = 300


def test_rule_eval_batch_size(model_class, test_x, test_y, s1, s2, log_file):
    seed = 0
    # fix seed
    torch.manual_seed(seed)
    random.seed(seed)
    np.random.seed(seed)

    model = model_class(pretrained=True)
    model.eval()

    class MyDataset(Dataset):
        def __init__(self, x, y):
            self.x = x
            self.y = y

        def __len__(self):
            return len(self.x)

        def __getitem__(self, idx):
            x = self.x[idx]
            y = self.y[idx]
            return x, y

    # evaluate model on test set with batch_size=s1
    try:
        dataset = MyDataset(test_x, test_y)
        loader_1 = DataLoader(dataset, batch_size=s1)
        output_1 = []
        for x, y in loader_1:
            output_1_tmp = model(x)
            output_1_tmp_np = output_1_tmp.cpu().detach().numpy()
            output_1.extend(output_1_tmp_np)
        stat_dict_1 = model.state_dict()
        output_1_np = np.array(output_1)
    except:
        with open(log_file, "a") as f:
            f.write(traceback.format_exc())
        # print(traceback.format_exc())
        output_1_np = None
        stat_dict_1 = None

    # reset seed
    torch.manual_seed(seed)
    random.seed(seed)
    np.random.seed(seed)

    # evaluate model on test set with batch_size=s2
    try:
        dataset = MyDataset(test_x, test_y)
        loader_2 = DataLoader(dataset, batch_size=s2)
        output_2 = []
        for x, y in loader_2:
            output_2_tmp = model(x)
            output_2_tmp_np = output_2_tmp.cpu().detach().numpy()
            output_2.extend(output_2_tmp_np)
        stat_dict_2 = model.state_dict()
        output_2_np = np.array(output_2)
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
    s1 = int(preprocess_line[2])
    s2 = int(preprocess_line[2])

    # argument = load_argument_file(in_dir, lib, version, api_name, input_index)
    log_file = get_log_file(out_dir, lib, version, 'rule_15', api_config, input_index)
    test_x, test_y = load_image_file(in_dir, lib, version, input_file)

    # get function pointer
    package = "torchvision"
    mod = importlib.import_module(package)
    model_class = get_func_ptr(mod, model_path)

    test_x = torch.tensor(test_x).to(torch.float)

    # run test
    [output_1, output_2] = test_rule_eval_batch_size(model_class, test_x, test_y, s1, s2, log_file)

    save_output_data([output_1, output_2], out_dir, lib, version, 'rule_15', api_config, input_index)

    return output_1 is not None and output_2 is not None


if __name__ == "__main__":
    main(run, TIMEOUT)
