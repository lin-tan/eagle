import os
import pickle
import numpy as np
import subprocess
import argparse
import traceback
import csv

import running_utils
from config import DATA_DIR, NUM_OF_INPUT, TEST_DONE_COLS, TEST_DONE_FILE

def compare_nested_list(list_1, list_2):
    # this function compares two lists by checking the contents of the lists
    if isinstance(list_1, list):
        results = True
        for i, j in zip(list_1, list_2):
            if not compare_nested_list(i, j):
                results = False
        return results
    else:
        a = np.array(list_1)
        b = np.array(list_2)
        if not np.allclose(a, b):
            return False
        else:
            return True

def main():
    # this file is used to compare the results of the testing rules
    parser = argparse.ArgumentParser()
    parser.add_argument("lib", choices=['tensorflow', 'pytorch'])
    parser.add_argument("version", type=str)
    args = parser.parse_args()
    config = vars(args)

    lib = config['lib']
    version = config['version']

    results_dir = os.path.join(DATA_DIR, "rule_output")

    csv_file_path = "{}_{}_output_file.csv".format(lib, version)
    with open(csv_file_path, mode='w') as csv_file:
        fieldnames = ["rule", 'api_name', 'Linf', "result_file"]
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)

        writer.writeheader()

        # the list of rules to analyze
        rule_list = [
            "rule_1",
            "rule_2",  # pass
            "rule_3",  # pass
            "rule_4",
            "rule_5",
            "rule_6",
            "rule_7",  # pass
            "rule_8",
            "rule_9",  # pass
            "rule_10",
            "rule_11",  # pass
            "rule_12",  # pass
            "rule_13",
            "rule_14",
            "rule_15",
            "rule_16",
            # "rule_17"
        ]

        for rule in rule_list:
            api_list_file = os.path.join("rules", "%s_%s_api_list.txt" % (rule, lib))
            if os.path.exists(api_list_file):
                api_list = running_utils.load_list(api_list_file)
                for api in api_list:
                    for output_index in range(NUM_OF_INPUT):
                        result_file = os.path.join(results_dir, lib, version, rule, api, "{}.output".format(output_index))
                        if os.path.exists(result_file):
                            try:
                                with open(result_file, "rb") as f:
                                    output_1, output_2 = pickle.load(f)
                                # print(output_1, output_2)

                                if rule == "rule_15" or rule == "rule_16":
                                    # for rule_15 and rule_16, the output_1 and output_2 are lists
                                    has_inconsistency = False
                                    if output_1 is not None and output_2 is not None:
                                        if lib == "tensorflow":
                                            [[output_1, metrics_value_1, config_1, weight_1], [output_2, metrics_value_2, config_2, weight_2]] = output_1, output_2
                                            if not np.allclose(output_1, output_2):
                                                print("Found difference! at {} for {}".format(output_index, 'prediction'))
                                                print(np.max(np.abs(output_1 - output_2)))
                                                has_inconsistency = True
                                            metrics_value_1 = np.array(metrics_value_1)
                                            metrics_value_2 = np.array(metrics_value_2)
                                            if not np.allclose(metrics_value_1, metrics_value_2):
                                                print(metrics_value_1, metrics_value_2)
                                                print("Found difference! at {} for {}".format(output_index, 'metrics'))
                                                print(np.max(np.abs(metrics_value_1 - metrics_value_2)))
                                                has_inconsistency = True
                                            if not config_1 == config_2:
                                                print("Found difference! at {} for {}".format(output_index, 'config'))
                                                has_inconsistency = True
                                                # print(config_1, config_2)
                                            # weight_1 = np.array(flatten(weight_1))
                                            # weight_2 = np.array(flatten(weight_2))
                                            if not compare_nested_list(weight_1, weight_2):
                                                print("Found difference! at {} for {}".format(output_index, 'weight'))
                                                print(weight_1)
                                                print(weight_2)
                                                has_inconsistency = True
                                        elif lib == "pytorch":
                                            [[output_1, state_dict_1], [output_2, state_dict_2]] = output_1, output_2
                                            if not np.allclose(output_1, output_2):
                                                print("Found difference! at {} for {}".format(output_index, 'prediction'))
                                                print(np.max(np.abs(output_1 - output_2)))
                                                print(output_1, output_2)
                                                has_inconsistency = True

                                            for key in state_dict_1.keys():
                                                w1 = state_dict_1[key]
                                                w2 = state_dict_2[key]
                                                w1_np = w1.cpu().detach().numpy()
                                                w2_np = w2.cpu().detach().numpy()
                                                if not np.allclose(w1_np, w2_np):
                                                    print("Found difference! at {} for {}".format(output_index, key))
                                                    print(np.max(np.abs(w1_np - w2_np)))
                                                    has_inconsistency = True
                                        if has_inconsistency:
                                            writer.writerow({"rule": rule, 'api_name': api, 'Linf': has_inconsistency, "result_file": result_file})
                                else:
                                    # for rule_1 to rule_14, the output_1 and output_2 are values
                                    if output_1 is not None and output_2 is not None:
                                        # print(np.allclose(output_1, output_2))
                                        if not np.allclose(output_1, output_2):
                                            print("difference, {}".format(result_file))
                                            diff_Linf = np.max(np.abs(output_1 - output_2))
                                            writer.writerow({"rule": rule, 'api_name': api, 'Linf': diff_Linf, "result_file": result_file})
                            except:
                                print("error, {}".format(result_file))
                                # print(traceback.format_exc())

if __name__ == "__main__":
    main()
