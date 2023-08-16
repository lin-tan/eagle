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
import subprocess

from rules.equiv_util import get_func_ptr, main, load_argument_file, load_input_file, load_image_file, get_log_file, save_output_data

# larger time out since this rule performs on models
TIMEOUT = 300


def test_rule_model_save(model, test_x, test_y, metric, save_load_mode, model_save_path, log_file):
    seed = 0
    # fix seed
    tf.random.set_seed(seed)
    random.seed(seed)
    np.random.seed(seed)

    # evaluate model 
    model.compile(**metric)

    try:
        output_1 = model.predict(test_x)
        # print(output_1.shape)
        # print(test_y.shape)
        metrics_value_1 = model.evaluate(test_x, test_y)
        config_1 = model.get_config()
        weight_1 = model.get_weights()
    except:
        with open(log_file, "a") as f:
            f.write(traceback.format_exc())
        # print(traceback.format_exc())
        output_1 = None
        metrics_value_1 = None
        config_1 = None
        weight_1 = None

    # save models to file and load them back
    try:
        if save_load_mode == 'model':
            tf.keras.models.save_model(model, model_save_path)
            reconstructed_model = tf.keras.models.load_model(model_save_path)
        elif save_load_mode == "config":
            config = model.get_config()
            if isinstance(model, tf.keras.Sequential):
                reconstructed_model = tf.keras.Sequential.from_config(config)
            elif isinstance(model, tf.keras.Model):
                reconstructed_model = tf.keras.Model.from_config(config)
            else:
                raise Exception("Unknown model object")
            reconstructed_model.set_weights(model.get_weights())
            reconstructed_model.compile(**metric)
        elif save_load_mode == "weight":
            model.save_weights(model_save_path)
            reconstructed_model = tf.keras.models.clone_model(model)
            reconstructed_model.load_weights(model_save_path)
            reconstructed_model.compile(**metric)
        else:
            raise Exception("Unkown save and load mode")
    except Exception as e:
        # print(e)
        with open(log_file, "a") as f:
            f.write(traceback.format_exc())

    # reset seed
    tf.random.set_seed(seed)
    random.seed(seed)
    np.random.seed(seed)

    # evaluate model again
    try:
        output_2 = reconstructed_model.predict(test_x)
        # print(output_2.shape)
        # print(test_y.shape)
        metrics_value_2 = reconstructed_model.evaluate(test_x, test_y)
        config_2 = reconstructed_model.get_config()
        weight_2 = reconstructed_model.get_weights()
    except:
        with open(log_file, "a+") as f:
            f.write(traceback.format_exc())
        # print(traceback.format_exc())
        output_2 = None
        metrics_value_2 = None
        config_2 = None
        weight_2 = None

    return [[output_1, metrics_value_1, config_1, weight_1], [output_2, metrics_value_2, config_2, weight_2]]


def run(in_dir, out_dir, lib, version, api_config, input_index):
    # parse api config
    preprocess_line = api_config.split("-")
    model_file = preprocess_line[0]
    input_file = preprocess_line[1]
    optimizer = preprocess_line[2]
    loss_fun = preprocess_line[3]
    metrics = preprocess_line[4]
    save_load_mode = preprocess_line[5]

    log_file = get_log_file(out_dir, lib, version, 'rule_16', api_config, input_index)
    x, y = load_image_file(in_dir, lib, version, input_file)
    model_path = os.path.join(in_dir, 'saved_models', lib, version, model_file)
    model = tf.keras.models.load_model(model_path, compile=False)

    # x, y = x[:10], y[:10]

    if loss_fun != 'sparse_categorical_crossentropy':
        y_onehot = np.zeros((len(y), 1000), np.float)
        for i in range(len(y)):
            y_onehot[i, y[i]] = 1
        y = y_onehot
    else:
        y = np.reshape(y, (len(y), 1))

    metric = {}
    metric['optimizer'] = optimizer
    metric['loss'] = loss_fun
    metric['metrics'] = [metrics]

    tmp_model_path = "/tmp/tmp_models_{}".format(api_config)

    # run test
    [output_1, output_2] = test_rule_model_save(model, x, y, metric, save_load_mode, tmp_model_path, log_file)

    # [[output_1_p, metrics_value_1, config_1, weight_1], [output_2_p, metrics_value_2, config_2, weight_2]] = [output_1, output_2]

    # print(config_1)
    # print(config_2)
    # print(config_1 == config_2)
    # print(metrics_value_1)
    # print(metrics_value_2)
    # print(metrics_value_1 == metrics_value_2)

    save_output_data([output_1, output_2], out_dir, lib, version, 'rule_16', api_config, input_index)

    delete_command = "rm -r " + tmp_model_path + "*"
    subprocess.call(delete_command, shell=True)

    return output_1 is not None and output_2 is not None


if __name__ == "__main__":
    main(run, TIMEOUT)
