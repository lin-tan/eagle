from pathlib import Path
import pandas as pd
import ntpath
import os
import importlib


def create_directory(filepath):
    dir = ntpath.dirname(filepath)
    os.makedirs(dir, exist_ok=True)


def chmod_directory(dirpath):
    os.chmod(dirpath, 0o777)


DONE_COLS = ['id', 'run_type', 'try']


def get_done_set(result_dir, filename, cols=DONE_COLS):
    done_path = os.path.join(result_dir, filename)
    if os.path.exists(done_path):
        done_data = pd.read_csv(done_path, skipinitialspace=True)

        # Run list
        special_cols_data = [done_data[col].values for col in cols]

        run_set = [
            tuple([str(col_data[r]) for col_data in special_cols_data]) for r in range(len(special_cols_data[0]))
        ]

        return run_set
    else:
        return None


def setup_done_file(result_dir, filename, cols=DONE_COLS):
    done_path = result_dir + '/' + filename
    done_file = Path(done_path)
    if not done_file.is_file():
        run_set = []

        done_out_f = open(done_path, "w")
        for col in cols:
            done_out_f.write('%s,' % col)
        done_out_f.write('time\n')
    else:
        run_set = get_done_set(result_dir, filename, cols)

        done_out_f = open(done_path, "a")

    return set(run_set), done_out_f


def write_done(done_dict, time, result_dir, filename, cols=DONE_COLS):
    done_path = os.path.join(result_dir, filename)
    with open(done_path, 'a') as done_f:
        for col in cols:
            done_f.write('%s,' % done_dict[col])
        done_f.write('%.5f\n' % (time))


def load_list(file_path):
    # Using readlines()
    f = open(file_path, 'r')
    lines = f.readlines()

    # Strips the newline character
    striped_lines = [line.strip() for line in lines]

    return striped_lines


def load_rule(rule_name, lib):
    name = "rules.%s_%s_script" % (rule_name, lib)
    mod = importlib.import_module(name)
    return mod


def get_arg_file_name(gen_order_path, index):
    orders = load_list(gen_order_path)
    index_input = orders[index]
    filename = index_input.split(',')[0]
    filename = filename.split('/')[-1]
    return filename