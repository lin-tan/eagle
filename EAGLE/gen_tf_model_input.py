import pickle
import os
import random

import tensorflow as tf
import numpy as np
from config import DATA_DIR

model_list = [
    tf.keras.applications.DenseNet121,
    tf.keras.applications.DenseNet169,
    tf.keras.applications.DenseNet201,
    tf.keras.applications.InceptionResNetV2,
    tf.keras.applications.InceptionV3,
    tf.keras.applications.MobileNet,
    tf.keras.applications.MobileNetV2,
    tf.keras.applications.NASNetLarge,
    tf.keras.applications.NASNetMobile,
    tf.keras.applications.ResNet101,
    tf.keras.applications.ResNet101V2,
    tf.keras.applications.ResNet152,
    tf.keras.applications.ResNet152V2,
    tf.keras.applications.ResNet50,
    tf.keras.applications.ResNet50V2,
    tf.keras.applications.VGG16,
    tf.keras.applications.VGG19,
    tf.keras.applications.Xception
]

def save_model_and_inputs():
    model_save_dir = os.path.join(DATA_DIR, "saved_model")
    if not os.path.exists(model_save_dir):
        os.makedirs(model_save_dir)
    for index in range(len(model_list)):
        model = model_list[index]()
        input_shape = model.input_shape
        print(input_shape)
        if len(input_shape) == 3:
            dim0, dim1, dim2 = input_shape
        elif len(input_shape) == 4:
            _, dim0, dim1, dim2 = input_shape
        else:
            print(input_shape)
            raise Exception("Unkown input shape")

        x_list = np.random.randn(10, dim0, dim1, dim2)
        y_list = np.random.randint(0, 1000, size=10)
        input_file = [x_list, y_list]

        model_save_path = os.path.join(model_save_dir, "model_{}".format(index))
        tf.keras.models.save_model(model, model_save_path)

        input_save_path = os.path.join(model_save_dir, "input_{}".format(index))
        with open(input_save_path, "wb") as f:
            pickle.dump(input_file, f)

if __name__ == "__main__":
    save_model_and_inputs()