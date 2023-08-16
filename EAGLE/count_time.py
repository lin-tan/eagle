import os

import running_utils
from config import DATA_DIR, NUM_OF_INPUT, TEST_DONE_COLS, TEST_DONE_FILE, TIMEOUT

def count_time():
    global TEST_DONE_COLS

    out_dir = os.path.join(DATA_DIR, "rule_output")

    TEST_DONE_COLS += ["time"]

    done_set, done_out_f = running_utils.setup_done_file(out_dir, TEST_DONE_FILE, TEST_DONE_COLS)
    done_out_f.close()

    count_time_tf = 0
    count_time_pt = 0
    count_num = 0
    for done_item in done_set:
        (rule, lib, version, api, input_index, done, time) = done_item
        count_num += 1
        if lib == "tensorflow":
            count_time_tf += float(time)
        elif lib == "pytorch":
            count_time_pt += float(time)

    print("tensorflow running time:")
    print(count_time_tf)
    print("pytorch running time:")
    print(count_time_pt)
    print(count_num)

def count_equi_graphs():
    lib_list = ["tensorflow", "pytorch"]
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
        "rule_16"
    ]
    count_eq_graph_tf = 0
    count_eq_graph_pt = 0

    for lib in lib_list:
        for rule in rule_list:
            rule_script = "%s_%s_script" % (rule, lib)
            if os.path.isfile(os.path.join("rules", "%s.py" % rule_script)):
                api_list_file = os.path.join("rules", "%s_%s_api_list.txt" % (rule, lib))
                api_list = running_utils.load_list(api_list_file)
                if lib == "tensorflow":
                    count_eq_graph_tf += len(api_list)
                elif lib == "pytorch":
                    count_eq_graph_pt += len(api_list)
    print(count_eq_graph_tf)
    print(count_eq_graph_pt)

if __name__ == "__main__":
    count_time()
    # count_equi_graphs()

