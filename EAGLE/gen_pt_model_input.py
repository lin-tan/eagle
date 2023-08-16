import pickle
import os
import random

import torch
import torchvision
import numpy as np
from config import DATA_DIR

model_list = [
    torchvision.models.resnet18,
    torchvision.models.alexnet,
    torchvision.models.vgg16,
    torchvision.models.squeezenet1_0,
    torchvision.models.densenet161,
    torchvision.models.inception_v3,
    torchvision.models.googlenet,
    torchvision.models.shufflenet_v2_x1_0,
    torchvision.models.mobilenet_v2,
    torchvision.models.resnext50_32x4d,
    torchvision.models.wide_resnet50_2,
    torchvision.models.mnasnet1_0,
]


def save_model_and_inputs():
    model_save_dir = os.path.join(DATA_DIR, "saved_model")
    if not os.path.exists(model_save_dir):
        os.makedirs(model_save_dir)
    for index in range(len(model_list)):
        if index == 5:
            input_shape = (3, 299, 299)
        else:
            input_shape = (3, 224, 224)
        print(input_shape)
        if len(input_shape) == 3:
            dim0, dim1, dim2 = input_shape
        elif len(input_shape) == 4:
            _, dim0, dim1, dim2 = input_shape
        else:
            print(input_shape)
            raise Exception("Unkown input shape")

        x_list = np.random.randn(10, dim0, dim1, dim2)
        input_file = x_list

        input_save_path = os.path.join(model_save_dir, "input_pt_{}".format(index))
        with open(input_save_path, "wb") as f:
            pickle.dump(input_file, f)


if __name__ == "__main__":
    save_model_and_inputs()