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


def test_rule_optimized(argument, target_fun, log_file):
    seed = 0

    # fix seed
    tf.random.set_seed(seed)
    random.seed(seed)
    np.random.seed(seed)

    # run function and input without optimization
    try:
        output_1 = target_fun(**argument)
    except:
        with open(log_file, "a+") as f:
            f.write(traceback.format_exc())
        # print(traceback.format_exc())
        output_1 = None

    # reset seed
    tf.random.set_seed(seed)
    random.seed(seed)
    np.random.seed(seed)

    @tf.function()
    def func_call_tf_function(func, input):
        return func(**input)

    # run function and input with optimization
    try:
        output_2 = func_call_tf_function(target_fun, argument)
    except:
        with open(log_file, "a+") as f:
            f.write(traceback.format_exc())
        # print(traceback.format_exc())
        output_2 = None

    return [output_1, output_2]


def run(in_dir, out_dir, lib, version, api_config, input_index):
    # get api name
    api_name = api_config

    # load arguments
    argument = load_argument_file(in_dir, lib, version, api_name, input_index)
    # argument = {}
    # argument['input'] = np.arange(27).reshape((3, 3, 3))
    # argument['axis'] = np.array([0, 1, 1], dtype=np.int32)
    # tf.linalg.matrix_rank
    # argument["input"] = np.array([[-61980., -21980., -45000., -29470., -6244., -62880., 58700., 18750.,
    #                            -22600., 22030., 49440., ],
    #                           [42050., -16250., 9380., 55000., 11020., 52540., -22830., -29400.,
    #                            -12630., 22130., 9900., ],
    #                           [-10130., 3604., 19650., -24210., -15010., 5932., -34750., -36500.,
    #                            9950., 2720., 61100., ],
    #                           [24820., 50080., 34140., 48600., 46400., 42400., -28740., 53860.,
    #                            -19000., -1684., 36860., ],
    #                           [17340., 61250., -14130., -2552., 24820., -7052., -22880., -56580.,
    #                            -60350., -60600., -34500., ],
    #                           [-43400., 20130., 20350., 14740., -20910., 22160., 40930., 65200.,
    #                            -33700., 6536., -12410., ],
    #                           [-40030., 61060., -9064., -64350., -36580., -25870., 40900., -223.5,
    #                            -36160., -58600., 55200., ],
    #                           [-54140., -32750., -37920., -15450., -4270., 15430., 53220., 59870.,
    #                            -62940., -48770., 60670., ],
    #                           [13496., 22960., 45630., -40130., 34270., -8076., 28980., -60670.,
    #                            -36450., 35780., -28980., ],
    #                           [-43070., 65100., 50750., 36960., 10220., -12440., -16136., 65300.,
    #                            -13520., -36450., -63500., ]], dtype=np.float16)

    # print(argument)
    # print(argument.keys())

    log_file = get_log_file(out_dir, lib, version, 'rule_1', api_config, input_index)

    package = "tensorflow"
    mod = importlib.import_module(package)
    target_fun = get_func_ptr(mod, api_name)

    # execute test with one api and one input
    [output_1, output_2] = test_rule_optimized(argument, target_fun, log_file)
    # print(output_1)
    # print(output_2)

    save_output_data([output_1, output_2], out_dir, lib, version, 'rule_1', api_config, input_index)

    return output_1 is not None and output_2 is not None


if __name__ == "__main__":
    main(run)
