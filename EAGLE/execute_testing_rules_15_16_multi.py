import multiprocessing
import os
import subprocess
import argparse

from timeit import default_timer as timer

import time

import traceback

from multiprocessing import Lock, Queue, Process

import running_utils
from config import DATA_DIR, TEST_DONE_COLS, TEST_DONE_FILE

# number of processes running at the same time
NUM_PROCESSES = 12


# start and execute one process
def execute_one_single_run(task_queue, global_lockfile, process_lockfile, out_dir, p_index):
    try:
        lock_acquired = False
        while True:
            # get the run
            try:
                (command, conf) = task_queue.get(block=False)
            except Exception:
                return

            print('RUNNING: ' + command)

            start_time = timer()
            status = subprocess.call(command, shell=True)
            end_time = timer()
            test_time = end_time - start_time

            if status != 1:
                # check return status
                if status == 0:
                    conf['done'] = 'done'
                elif status == 2:
                    conf['done'] = 'timeout'
                else:
                    conf['done'] = 'error'

                # get the queue lock
                while not lock_acquired:
                    try:
                        os.link(process_lockfile, global_lockfile)
                    except:
                        time.sleep(3)
                    else:
                        lock_acquired = True

                # write the done file
                running_utils.write_done(conf, test_time, out_dir, TEST_DONE_FILE, cols=TEST_DONE_COLS)

                # return the lock
                os.unlink(global_lockfile)
                lock_acquired = False

    except Exception:
        print(traceback.format_exc())
        if lock_acquired:
            os.unlink(global_lockfile)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("lib", choices=['tensorflow', 'pytorch'],
                        help='Library to test. Either tensorflow or pytorch.')
    parser.add_argument("version", type=str, 
                        help='Version of the library to test. Currently EAGLE support tensorflow 2.1, 2.2, 2.3 and pytorch 1.6, 1.9.')
    args = parser.parse_args()
    config = vars(args)

    lib = config['lib']
    version = config['version']

    # address for generated inputs
    in_dir = os.path.join(DATA_DIR, "generated_input")
    # address for rule output
    out_dir = os.path.join(DATA_DIR, "rule_output")
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)

    global_lockfile = os.path.join(out_dir, 'queue_lock')

    # create a done file if it doesn't exist
    done_set, done_out_f = running_utils.setup_done_file(out_dir, TEST_DONE_FILE, TEST_DONE_COLS)
    done_out_f.close()

    # list of rules to test
    rule_list = [
        "rule_15", 
        "rule_16"
        ]

    #create task queue
    queue = multiprocessing.Queue()
    for rule in rule_list:
        rule_script = "%s_%s_script" % (rule, lib)
        if os.path.isfile(os.path.join("rules", "%s.py" % rule_script)):
            api_list_file = os.path.join("rules", "%s_%s_api_list.txt" % (rule, lib))
            api_list = running_utils.load_list(api_list_file)
            for api in api_list:
                input_index = 0
                if (rule, lib, version, api, str(input_index), 'done') not in done_set and (rule, lib, version, api,
                                                                                            str(input_index),
                                                                                            'error') not in done_set:
                    # construct the command
                    command = "python -m rules.%s '%s' '%s' %s %s %s %d" % (rule_script, in_dir, out_dir, lib, version,
                                                                            api, input_index)
                    # define the configuration
                    conf = {
                        'rule': rule,
                        'lib': lib,
                        'version': version,
                        'api': api,
                        'input_index': str(input_index),
                        'done': ''
                    }

                    queue.put((command, conf))
                    #print("Executing: %s" % command)

    # start up processes
    processes = []
    for p_index in range(NUM_PROCESSES):
        process_lockfile = os.path.join(out_dir, 'P_%s_%s_%d.lock' % (lib, version, p_index))

        # create the file if necessary (only once, at the beginning of each process)
        with open(process_lockfile, 'w') as f:
            f.write('\n')

        # start each processes
        process = Process(target=execute_one_single_run,
                          args=(queue, global_lockfile, process_lockfile, out_dir, p_index))
        process.start()
        processes.append(process)

    # wait for all processes to finish
    for process in processes:
        process.join()


if __name__ == "__main__":
    main()
