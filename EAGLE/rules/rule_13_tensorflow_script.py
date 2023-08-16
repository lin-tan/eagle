import numpy as np
import tensorflow as tf
import os
from datetime import datetime
import argparse
import traceback
import pickle
import importlib
import random
from timeit import default_timer as timer

from rules.equiv_util import get_func_ptr, main, load_argument_file, load_input_file, get_log_file, save_output_data


def test_rule_decode_encode(input, encode_fun, decode_fun, file_saving_path, log_file):
    seed = 0
    # fix seed
    tf.random.set_seed(seed)
    random.seed(seed)
    np.random.seed(seed)

    try:
        # encode input tensor to image
        input_uint8 = tf.cast(input, tf.uint8, name=None)
        encoded_file = encode_fun(input_uint8)
        tf.io.write_file(file_saving_path, encoded_file)

        # decode image to tensor
        input_decoded = decode_fun(tf.io.read_file(file_saving_path))
        output_1 = input_uint8
        output_2 = input_decoded
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

    # argument = load_argument_file(in_dir, lib, version, encode_fun_name, input_index)
    log_file = get_log_file(out_dir, lib, version, 'rule_13', api_config, input_index)

    argument = np.random.randn(10, 13, 13, 3)

    # get function pointer, some functions are from tensorflow_io
    if encode_fun_name.startswith("tfio"):
        package = "tensorflow_io"
        mod = importlib.import_module(package)
        encode_fun = get_func_ptr(mod, encode_fun_name)
    else:
        package = "tensorflow"
        mod = importlib.import_module(package)
        encode_fun = get_func_ptr(mod, encode_fun_name)

    if decode_fun_name.startswith("tfio"):
        package = "tensorflow_io"
        mod = importlib.import_module(package)
        decode_fun = get_func_ptr(mod, decode_fun_name)
    else:
        package = "tensorflow"
        mod = importlib.import_module(package)
        decode_fun = get_func_ptr(mod, decode_fun_name)

    file_saving_path = "/tmp/encoding_file"

    # run test
    [output_1, output_2] = test_rule_decode_encode(argument, encode_fun, decode_fun, file_saving_path, log_file)
    # print(np.allclose(output_1, output_2))

    save_output_data([output_1, output_2], out_dir, lib, version, 'rule_13', api_config, input_index)

    return output_1 is not None and output_2 is not None


if __name__ == "__main__":
    main(run)
