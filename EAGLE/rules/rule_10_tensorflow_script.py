import numpy as np
import tensorflow as tf
import os
from datetime import datetime
import argparse
import traceback
import pickle
import importlib
import random

from rules.equiv_util import get_func_ptr, main, load_argument_file, load_input_file, get_log_file, save_output_data


def test_rule_time_major(input_data, argument, argument_cell, target_fun, cell_fun, bidirectional, log_file):
    seed = 0
    # fix seed
    tf.random.set_seed(seed)
    random.seed(seed)
    np.random.seed(seed)

    # run batch major function and input
    try:
        argument["time_major"] = False
        if cell_fun is not None:
            cell = cell_fun(**argument_cell)
            argument["cell"] = cell
        (a, b, input_size) = np.array(input_data).shape

        input = tf.keras.Input(shape=(b, input_size), batch_size=a)
        # print(input_dict)
        rnn_layer_1 = target_fun(**argument)
        if bidirectional:
            rnn_layer_1 = tf.keras.layers.Bidirectional(rnn_layer_1)
        output_1 = rnn_layer_1(input)
        model_1 = tf.keras.Model(inputs=input, outputs=output_1)

        weights = rnn_layer_1.get_weights()
        # print(len(weights))
        new_w = []
        for weight_i in weights:
            # print(weight_i.shape)
            shape = np.array(weight_i).shape
            new_w.append(np.random.randn(*shape).astype(np.float32))
        rnn_layer_1.set_weights(new_w)

        output_1 = model_1(input_data)

        print(output_1)
    except:
        with open(log_file, "a+") as f:
            f.write(traceback.format_exc())
        print(traceback.format_exc())
        output_1 = None

    # reset seed
    tf.random.set_seed(seed)
    random.seed(seed)
    np.random.seed(seed)

    # run time major function and input
    try:
        argument["time_major"] = True
        if cell_fun is not None:
            cell = cell_fun(**argument_cell)
            argument["cell"] = cell
        input_data_t = np.array(input_data).transpose([1, 0, 2])
        (a, b, input_size) = np.array(input_data_t).shape

        input_t = tf.keras.Input(shape=(b, input_size), batch_size=b)
        rnn_layer_2 = target_fun(**argument)

        # add bidirectional layer if needed
        if bidirectional:
            rnn_layer_2 = tf.keras.layers.Bidirectional(rnn_layer_2)

        output_2_t = rnn_layer_2(input_t)

        model_2 = tf.keras.Model(inputs=input_t, outputs=output_2_t)

        weights = rnn_layer_1.get_weights()
        rnn_layer_2.set_weights(weights)

        output_2_t = model_2(input_data_t)

        if isinstance(output_2_t, list):
            output_2 = []
            for output in output_2_t:
                output_2.append(np.array(output))
            if 'return_sequences' in argument.keys() and argument['return_sequences']:
                output_2[0] = output_2[0].transpose([1, 0, 2])
        else:
            output_2 = np.array(output_2_t)
            if 'return_sequences' in argument.keys() and argument['return_sequences']:
                output_2 = output_2.transpose([1, 0, 2])

        # print(output_2)
        # print(output_2.shape)
    except:
        with open(log_file, "a+") as f:
            f.write(traceback.format_exc())
        print(traceback.format_exc())
        output_2 = None

    #if output_1 is not None and output_2 is not None:
    #    print(output_1, output_2)
    #    print(np.max(np.abs(output_1 - output_2)))
    return [output_1, output_2]


def run(in_dir, out_dir, lib, version, api_config, input_index):
    # parse api config
    preprocess_line = api_config.split("-")
    api_name = preprocess_line[0]
    cell_name = preprocess_line[1]
    if preprocess_line[2] == "True":
        bidirectional = True
    else:
        bidirectional = False
    print(api_name)

    argument = load_argument_file(in_dir, lib, version, api_name.lower(), input_index)
    if cell_name != "None":
        argument_cell = load_argument_file(in_dir, lib, version, cell_name.lower(), input_index)
    else:
        argument_cell = None
    input_data = load_input_file(in_dir, input_index)
    input_data = input_data[0]
    log_file = get_log_file(out_dir, lib, version, 'rule_10', api_config, input_index)
    print(input_data.shape)

    print(argument)
    print(input_data)

    # get function pointers
    package = "tensorflow"
    mod = importlib.import_module(package)
    target_fun = get_func_ptr(mod, api_name)
    if cell_name != "None":
        mod = importlib.import_module(package)
        cell_fun = get_func_ptr(mod, cell_name)
    else:
        cell_fun = None
        
    # run test
    [output_1, output_2] = test_rule_time_major(input_data, argument, argument_cell, target_fun, cell_fun,
                                                bidirectional, log_file)

    save_output_data([output_1, output_2], out_dir, lib, version, 'rule_10', api_config, input_index)

    return output_1 is not None and output_2 is not None


if __name__ == "__main__":
    main(run)
