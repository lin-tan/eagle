import os
import pickle
import importlib
import numpy as np
import traceback
import sys
import multiprocessing
import time
import queue


def extract_and_save_inputs(base_dir, api_name):
    # extract and save input files to one file, if gen_order exists.
    # base_dir: the base working dir
    # api_name: the api name
    gen_order_path = os.path.join(base_dir, api_name, "gen_order")

    # read gen_order file and extract the list of input files
    input_names = []
    with open(gen_order_path, "r") as f:
        lines = f.readlines()
        for line in lines:
            input_names.append(line.split(", ")[0])

    # iterate over the list of input files and extract the inputs
    inputs = []
    for input_name in input_names:
        with open(input_name, "rb") as f:
            input = pickle.load(f)
            inputs.append(input)

    save_path = os.path.join(base_dir, api_name, "inputs_data")
    with open(save_path, "wb") as output_file:
        pickle.dump(inputs, output_file)


def extract_and_save_inputs_2(base_dir, api_name):
    # extract and save input files to one file, if gen_order doesn't exist. 
    # base_dir: the base working dir
    # api_name: the api name
    api_dir_path = os.path.join(base_dir, api_name)
    api_dir_files = os.listdir(api_dir_path)

    # iterate over all of input files in the folder and extract the inputs
    inputs = []
    for file_name in api_dir_files:
        if file_name.endswith(".p"):
            with open(os.path.join(base_dir, file_name), "rb") as f:
                input = pickle.load(f)
                inputs.append(input)

    save_path = os.path.join(base_dir, api_name, "inputs_data")
    with open(save_path, "wb") as output_file:
        pickle.dump(inputs, output_file)


def load_inputs(base_dir, api_name):
    # load inputs from the input file. If the input file doesn't exist, call either extract_and_save_inputs or extract_and_save_inputs_2 to generate the input file.
    inputs_path = os.path.join(base_dir, api_name, "inputs_data")
    if not os.path.exists(inputs_path):
        gen_order_path = os.path.join(base_dir, api_name, "gen_order")
        if os.path.exists(gen_order_path):
            extract_and_save_inputs(base_dir, api_name)
        else:
            extract_and_save_inputs_2(base_dir, api_name)

    with open(inputs_path, "rb") as f:
        inputs = pickle.load(f)

    return inputs


def get_func_ptr(package, title):
    # return the function pointer
    # package: the package object (get from importlib)
    # title: tensorflow.keras.layers.GlobalMaxPooling3D
    # title_toks: something like ['tensorflow', 'keras', 'layers', 'GlobalMaxPool3D']
    title_toks = title.split('.')
    mod = package
    for i, t in enumerate(title_toks):
        if i == 0:  # the root module (e.g. tf in case of tensorflow)
            continue
        if i < len(title_toks) - 1:  # until the second last
            try:
                mod = getattr(mod, t)
            except AttributeError:
                import_statement = '.'.join(title_toks[:i + 1])
                mod = importlib.import_module(import_statement)
        else:
            break
    try:
        target_func = getattr(mod, title_toks[-1])
        return target_func
    except:
        return None


def get_complex_api_name_list():
    sparse_api_arg_path = "/mnt/tmp/tf2.1_complex"

    sparse_api_arg_list = []
    api_name_list = []
    with open(sparse_api_arg_path, "r") as f:
        lines = f.readlines()
        for line in lines:
            sparse_api_arg_list.append(line.split("-"))
            api_name = line.split("-")[0]
            if api_name not in api_name_list:
                api_name_list.append(api_name)
    print(sparse_api_arg_list)
    print(api_name_list)
    return api_name_list


import argparse
from running_utils import write_done, get_arg_file_name
from config import TEST_DONE_COLS, TEST_DONE_FILE, TIMEOUT


def main(run_func, timelimit=TIMEOUT):
    # the main function to run the rule
    parser = argparse.ArgumentParser()
    parser.add_argument("in_dir", type=str)
    parser.add_argument("out_dir", type=str)
    parser.add_argument("lib", type=str)
    parser.add_argument("version", type=str)
    parser.add_argument("api_name", type=str)
    parser.add_argument("input_index", type=int)

    print("in main...")

    args = parser.parse_args()
    config = vars(args)

    in_dir = config["in_dir"]
    out_dir = config["out_dir"]

    lib = config["lib"]
    version = config["version"]
    api_name = config["api_name"]
    input_index = config["input_index"]

    try:
        res_queue = multiprocessing.Queue(1)
        p = multiprocessing.Process(target=run_rule,
                                    args=(run_func, in_dir, out_dir, lib, version, api_name, input_index, res_queue))
        print("start process")
        # run_rule(run_func, in_dir, out_dir, lib, version, api_name, input_index, res_queue)
        p.start()
        print("process started")
        def check_process(process, tlimit):
            start_time = time.time()
            while time.time() - start_time < tlimit:
                try:
                    res = res_queue.get(timeout=0.1)
                    print(res)
                    break
                except queue.Empty:
                    if not process.is_alive():
                        res = -1
                        break
            else:  # time limit reached
                process.terminate()
                res = 2

            process.join()
            return res

        status = check_process(p, timelimit)
        print(status)
    except KeyboardInterrupt:
        return sys.exit(1)
    except:
        print(traceback.format_exc())
        return sys.exit(-1)

    if not status:
        sys.exit(-1)


def run_rule(run_func, in_dir, out_dir, lib, version, api_name, input_index, res_queue):
    print("in run_rule...")
    try:
        success = run_func(in_dir, out_dir, lib, version, api_name, input_index)
        res_queue.put((success))
    except:
        print(traceback.format_exc())


def load_argument_file(in_dir, lib, version, api_name, input_index):
    args_dir = os.path.join(in_dir, 'args', lib, version, api_name)
    argument_list_file = os.path.join(args_dir, 'gen_order')
    if not os.path.exists(argument_list_file):
        api_dir_files = os.listdir(args_dir)
        contents = ""
        count = 1
        for file_name in api_dir_files:
            if file_name.endswith(".p"):
                contents += str(os.path.join(args_dir, file_name)) + ", {}\n".format(count)
                count += 1
        with open(argument_list_file, "wb") as f:
            f.write(contents)
    argument_filename = get_arg_file_name(argument_list_file, input_index)
    argument_file = os.path.join(args_dir, argument_filename)
    with open(argument_file, "rb") as f:
        argument = pickle.load(f)
    return argument

def get_argument_file_path(in_dir, lib, version, api_name, input_index):
    args_dir = os.path.join(in_dir, 'args', lib, version, api_name)
    argument_list_file = os.path.join(args_dir, 'gen_order')
    if not os.path.exists(argument_list_file):
        api_dir_files = os.listdir(args_dir)
        contents = ""
        count = 1
        for file_name in api_dir_files:
            if file_name.endswith(".p"):
                contents += str(os.path.join(args_dir, file_name)) + ", {}\n".format(count)
                count += 1
        with open(argument_list_file, "wb") as f:
            f.write(contents)
    argument_filename = get_arg_file_name(argument_list_file, input_index)
    argument_file = os.path.join(args_dir, argument_filename)
    return argument_file

def load_input_file(in_dir, input_index):
    input_dir = os.path.join(in_dir, 'input')
    input_file = os.path.join(input_dir, "%d.npy" % input_index)
    input_data = np.load(input_file)
    return input_data


def load_image_file(in_dir, lib, version, input_file):
    input_dir = os.path.join(in_dir, 'images', lib, version)
    input_file = os.path.join(input_dir, input_file)
    with open(input_file, "rb") as f:
        input_data = pickle.load(f)
    return input_data


def get_log_file(out_dir, lib, version, rule, api_name, input_index):
    out_dir = os.path.join(out_dir, lib, version, rule, api_name)
    os.makedirs(out_dir, exist_ok=True)

    log_file = os.path.join(out_dir, "%d.log" % input_index)
    return log_file


def save_output_data(output, out_dir, lib, version, rule, api_name, input_index):
    out_dir = os.path.join(out_dir, lib, version, rule, api_name)

    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, "%d.output" % input_index), "wb") as f:
        pickle.dump(output, f)
