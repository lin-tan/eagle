import numpy as np
import tensorflow as tf
from tensorflow.keras.preprocessing import image
import os
from datetime import datetime
import argparse
import traceback
import pickle
import importlib
import random
from timeit import default_timer as timer

# larger time out since this rule performs on models
TIMEOUT = 300

from rules.equiv_util import get_func_ptr, main, load_argument_file, load_input_file, load_image_file, get_log_file, save_output_data

# list of models and preprocessing. deprecated
# keras_model_preprocessing_list = [
#     tf.keras.applications.densenet.preprocess_input, tf.keras.applications.densenet.preprocess_input,
#     tf.keras.applications.densenet.preprocess_input, tf.keras.applications.inception_resnet_v2.preprocess_input,
#     tf.keras.applications.inception_v3.preprocess_input, tf.keras.applications.mobilenet.preprocess_input,
#     tf.keras.applications.mobilenet_v2.preprocess_input, tf.keras.applications.nasnet.preprocess_input,
#     tf.keras.applications.nasnet.preprocess_input, tf.keras.applications.resnet.preprocess_input,
#     tf.keras.applications.resnet_v2.preprocess_input, tf.keras.applications.resnet.preprocess_input,
#     tf.keras.applications.resnet_v2.preprocess_input, tf.keras.applications.resnet.preprocess_input,
#     tf.keras.applications.resnet_v2.preprocess_input, tf.keras.applications.vgg16.preprocess_input,
#     tf.keras.applications.vgg19.preprocess_input, tf.keras.applications.xception.preprocess_input
# ]

# model_list = [
#     tf.keras.applications.DenseNet121, tf.keras.applications.DenseNet169, tf.keras.applications.DenseNet201,
#     tf.keras.applications.InceptionResNetV2, tf.keras.applications.InceptionV3, tf.keras.applications.MobileNet,
#     tf.keras.applications.MobileNetV2, tf.keras.applications.NASNetLarge, tf.keras.applications.NASNetMobile,
#     tf.keras.applications.ResNet101, tf.keras.applications.ResNet101V2, tf.keras.applications.ResNet152,
#     tf.keras.applications.ResNet152V2, tf.keras.applications.ResNet50, tf.keras.applications.ResNet50V2,
#     tf.keras.applications.VGG16, tf.keras.applications.VGG19, tf.keras.applications.Xception
# ]


def test_rule_eval_batch_size(model, test_x, test_y, metric, s1, s2, log_file):
    seed = 0
    # fix seed
    tf.random.set_seed(seed)
    random.seed(seed)
    np.random.seed(seed)

    model.compile(**metric)

    # evaluate model on test set with batch_size=s1
    try:
        output_1 = model.predict(test_x)
        metrics_value_1 = model.evaluate(test_x, test_y, s1)
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

    # reset seed
    tf.random.set_seed(seed)
    random.seed(seed)
    np.random.seed(seed)

    # evaluate model on test set with batch_size=s2
    try:
        output_2 = model.predict(test_x)
        metrics_value_2 = model.evaluate(test_x, test_y, s2)
        config_2 = model.get_config()
        weight_2 = model.get_weights()
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
    s1 = int(preprocess_line[5])
    s2 = int(preprocess_line[6])

    log_file = get_log_file(out_dir, lib, version, 'rule_15', api_config, input_index)
    x, y = load_image_file(in_dir, lib, version, input_file)
    model_path = os.path.join(in_dir, 'saved_models', lib, version, model_file)
    model = tf.keras.models.load_model(model_path, compile=False)

    # if loss function is not sparse_categorical_crossentropy, then y should be one-hot encoded
    if loss_fun != 'sparse_categorical_crossentropy':
        y_onehot = np.zeros((len(y), 1000), np.float)
        for i in range(len(y)):
            y_onehot[i, y[i]] = 1
        y = y_onehot

    metric = {}
    metric['optimizer'] = optimizer
    metric['loss'] = loss_fun
    metric['metrics'] = [metrics]

    # run test
    [output_1, output_2] = test_rule_eval_batch_size(model, x, y, metric, s1, s2, log_file)

    save_output_data([output_1, output_2], out_dir, lib, version, 'rule_15', api_config, input_index)

    return output_1 is not None and output_2 is not None


if __name__ == "__main__":
    main(run, TIMEOUT)
