import os

import argparse

import input_generation.matrix_generation
import input_generation.docter_argument_generation

import running_utils

from config import DATA_DIR, TF_NAME, PT_NAME, NUM_OF_ARGS, NUM_OF_INPUT

ARGS_DONE_COLS = ['lib', 'version', 'api']
ARGS_DONE_FILE = "args_gen_done.csv"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("lib", choices=['tensorflow', 'pytorch'])
    parser.add_argument("version", type=str)
    args = parser.parse_args()
    config = vars(args)

    lib = config['lib']
    version = config['version']

    src_dir = os.path.join(os.getcwd(), '..')
    # address for generated inputs
    out_dir = os.path.join(DATA_DIR, "generated_input")
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)

    # create a done file if it doesn't exist
    args_done_set, args_done_out_f = running_utils.setup_done_file(out_dir, ARGS_DONE_FILE, ARGS_DONE_COLS)
    args_done_out_f.close()

    # load list of APIs to generate inputs for
    tf_api_list = running_utils.load_list(os.path.join('input_generation', 'input_gen_tensorflow_api_list.txt'))
    pt_api_list = running_utils.load_list(os.path.join('input_generation', 'input_gen_pytorch_api_list.txt'))

    apis_map = {
        TF_NAME: tf_api_list,
        PT_NAME: pt_api_list
    }

    # generate inputs for each API
    for api in apis_map[lib]:
        if (lib, version, api) not in args_done_set:
            print("Generating args for %s %s %s" % (lib, version, api))

            args_gen_time = input_generation.docter_argument_generation.generate_single_api_argument(
                out_dir, src_dir, lib, version, api, NUM_OF_ARGS)
            conf = {
                'lib': lib,
                'version': version,
                'api': api
            }

            running_utils.write_done(conf, args_gen_time, out_dir, ARGS_DONE_FILE, ARGS_DONE_COLS)

    # generating 4D matrix inputs
    if not os.path.exists(os.path.join(out_dir, 'input')):
        print("Generating 4D input")
        input_generation.matrix_generation.generate_single_api_input(out_dir, NUM_OF_INPUT)
    
    if lib == TF_NAME:
        from gen_tf_model_input import save_model_and_inputs
    else:
        from gen_pt_model_input import save_model_and_inputs
    save_model_and_inputs()


if __name__ == "__main__":
    main()
