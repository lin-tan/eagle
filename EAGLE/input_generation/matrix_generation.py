import os
import numpy as np
from timeit import default_timer as timer

from config import MAX_MATRIX_VALUE


def generate_single_api_input(data_dir, max_num):

    output_path = os.path.join(data_dir, 'input')

    start_time = timer()

    generate_4d_numpy_tensors(output_path, max_num)

    end_time = timer()

    return end_time - start_time


def generate_4d_numpy_tensors(outpath, max_num):
    os.makedirs(outpath, exist_ok=True)

    for i in range(max_num):
        a = np.random.randint(1, MAX_MATRIX_VALUE)
        b = np.random.randint(1, MAX_MATRIX_VALUE)
        c = np.random.randint(1, MAX_MATRIX_VALUE)
        d = np.random.randint(1, MAX_MATRIX_VALUE)
        input_t = (np.random.rand(a, b, c, d) - 0.5) * 2000
        np.save(os.path.join(outpath, "{}.npy".format(i)), input_t)


def generate_4d_numpy_tensors_for_keras(outpath, max_num):
    os.makedirs(outpath, exist_ok=True)

    for i in range(max_num):
        a = np.random.randint(1, MAX_MATRIX_VALUE)
        b = np.random.randint(1, MAX_MATRIX_VALUE)
        c = np.random.randint(1, MAX_MATRIX_VALUE)
        d = np.random.randint(1, MAX_MATRIX_VALUE)
        input_t = (np.random.rand(a, b, c, d) - 0.5) * 2000
        np.save(os.path.join(outpath, "{}.npy".format(i)), input_t)


def generate_4d_tensors_for_pytorch(outpath, max_num):
    os.makedirs(outpath, exist_ok=True)

    for i in range(max_num):
        a = np.random.randint(1, MAX_MATRIX_VALUE)
        b = np.random.randint(1, MAX_MATRIX_VALUE)
        c = np.random.randint(1, MAX_MATRIX_VALUE)
        d = np.random.randint(1, MAX_MATRIX_VALUE)
        input_t = (np.random.rand(a, b, c, d) - 0.5) * 2000
        np.save(os.path.join(outpath, "{}.npy".format(i)), input_t)
