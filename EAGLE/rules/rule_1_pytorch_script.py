import numpy as np
import torch
import os
from datetime import datetime
import argparse
import traceback
import pickle
import importlib
import random
from timeit import default_timer as timer
import subprocess
import shlex

from rules.equiv_util import get_func_ptr, main, load_argument_file, get_argument_file_path, load_input_file, get_log_file, save_output_data

def gen_one_api_one_input(api_name, input_file_path, output_file_path, log_file_path, script_path):
    # generate scripts for each input
    content = []
    content.append("import torch\n")
    content.append("import pickle\n")
    content.append("import traceback\n")
    content.append("input = pickle.load(open(\"{}\", \"rb\"))\n".format(input_file_path))
    content.append("fun = {}\n".format(api_name))

    # run function and input without optimization
    content.append("try:\n")
    content.append("    output1_t = fun(**input)\n")
    content.append("    output1 = output1_t.cpu().detach().numpy()\n")
    content.append("except:\n")
    content.append("    with open(\"{}\", \"w\") as f:\n".format(log_file_path))
    content.append("        f.write(traceback.format_exc())\n")
    content.append("    output1 = None\n")
    # content.append("    print(traceback.format_exc())\n")

    # run function and input with optimization
    content.append("try:\n")
    content.append("    @torch.jit.script\n")
    input = pickle.load(open(input_file_path, "rb"))
    # generate input-type specification as it is required by torch.jit.script
    argument_type_str = ""
    argument_key_str = ""
    count = 0
    for key in input:
        if count != 0:
            argument_type_str += ", "
            argument_key_str += ", "
        key_type = type(input[key]).__name__
        if key_type == "Tensor":
            key_type = "torch.Tensor"
        argument_type_str += key + ":" + key_type
        argument_key_str += key + "=" + key
        count += 1

    content.append("    def func_call_jit_script({}):\n".format(argument_type_str))
    content.append("        return fun({})\n".format(argument_key_str))
    content.append("    output2_t = func_call_jit_script(**input)\n")
    content.append("    output2 = output2_t.cpu().detach().numpy()\n")
    content.append("except:\n")
    content.append("    with open(\"{}\", \"w\") as f:\n".format(log_file_path))
    content.append("        f.write(traceback.format_exc())\n")
    # content.append("    print(traceback.format_exc())\n")
    content.append("    try:\n")

    # some functions' key name is different from the api documentation
    argument_key_str = ""
    count = 0
    for key in input:
        if count != 0:
            argument_key_str += ", "
        if key == "input":
            argument_key_str += "self" + "=" + key
        else:
            argument_key_str += key + "=" + key
        count += 1

    content.append("        @torch.jit.script\n")
    content.append("        def func_call_jit_script_2({}):\n".format(argument_type_str))
    content.append("            return fun({})\n".format(argument_key_str))
    content.append("        output2_t = func_call_jit_script_2(**input)\n")
    content.append("        output2 = output2_t.cpu().detach().numpy()\n")

    content.append("    except:\n")
    content.append("        with open(\"{}\", \"w\") as f:\n".format(log_file_path))
    content.append("            f.write(traceback.format_exc())\n")
    content.append("        output2 = None\n")
    # content.append("        print(traceback.format_exc())\n")
    content.append("output = [output1, output2]\n")
    content.append("pickle.dump(output, open(\"{}\", \"wb\"))\n".format(output_file_path))

    with open(script_path, "w") as file:
        for c in content:
            file.write(c)


def run(in_dir, out_dir, lib, version, api_config, input_index):
    # get api name
    api_name = api_config

    # load arguments
    # argument = load_argument_file(in_dir, lib, version, api_name, input_index)
    # print(argument)
    # print(argument.keys())
    log_file = get_log_file(out_dir, lib, version, 'rule_1', api_config, input_index)
    argument_file_name = get_argument_file_path(in_dir, lib, version, api_name, input_index)
    output_file_path = os.path.join(out_dir, lib, version, 'rule_1', api_config, "%d.output" % input_index)

    script_path = "/tmp/rule_1_{}_{}.py".format(api_name, input_index)

    # generate run script
    gen_one_api_one_input(api_name, argument_file_name, output_file_path, log_file, script_path)

    # execute run script and delete it after finished
    try:
        run_p = None
        delete_p = None

        run_command = "python " + script_path
        run_args = shlex.split(run_command)
        run_p = subprocess.Popen(run_args)

        run_p.communicate()

        delete_command = "rm -r " + script_path
        delete_args = shlex.split(delete_command)
        delete_p = subprocess.Popen(delete_args)

        delete_p.communicate()
    except:
        pass
    finally:
        if run_p is not None:
            run_p.terminate()
        if delete_p is not None:
            delete_p.terminate()

    [output_1, output_2] = pickle.load(open(output_file_path, "rb"))

    # print(output_1 is not None and output_2 is not None)

    return output_1 is not None and output_2 is not None


if __name__ == "__main__":
    main(run)
