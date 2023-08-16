# EAGLE: Creating Equivalent Graphs to Test Deep Learning Libraries

This repo contains reproduction code for the [ICSE 2022](https://conf.researchr.org/track/icse-2022/icse-2022-papers?#program) paper *EAGLE: Creating Equivalent Graphs to Test Deep Learning Libraries*. 

## Folder/File Structure


The `EAGLE` directory contains codes for reproducing our experiment. It has four sub directories. 

Dir `rules` contains the 16 rules described in the EAGLE paper, along with api config for each rule. The formats of api configs are defined [here](EAGLE/rules/README.md).


Dir `docker_files` contains the docker file for creating containers for the specific enviroment. 

Dir `api_constraints` contains some customized api constraints we defined manually. 

Dir `input_generation` contains code which calls Ddoctor to generate inputs. It also contains two lists for the list of APIs for which we want to generate inputs. 

The `dl-fuzzer-master` directory contains codes from Ddoctor, which is a fuzzing tool to test deep learning libraries. We use it to generate inputs for EAGLE.

The `bug-reproduction` directory contains code for reproducing bugs detected in the EAGLE paper.


## Instruction

### Create enviroment
To use EAGLE, first you need to create an environment that can run EAGLE. 

We provide docker files under `EAGLE/docker_files` which can help you to create environments. 

We provide docker files for pytorch 1.6, 1.9 and tensorflow 2.1, 2.2, 2.3, which are the versions EAGLE tested.

To create the docker image: as a example, in project root, `docker build -f EAGLE/docker_files/tf2.1.dockerfile .`, which will create docker image for tensorflow 2.1.

We also provide example docker commands at `EAGLE/docker_command`.

### Generate input
After creating enviroment, we need to generate inputs using Ddoctor.

To generate inputs, under `EAGLE` directory, execute `bash generate_all_input.sh LIB VER` to generate inputs for specific library and version. 

The `LIB VER` can be `tensorflow 21`, `tensorflow 22`, `tensorflow 23`, `pytorch 16`, or `pytorch 19`.

### Execute EAGLE rules
To execute EAGLE, under `EAGLE` directory, execute `bash execute_testing_rules_multi.sh LIB VER` if you want to execute rule 1-14, or execute `bash execute_testing_rules_15_16_multi.sh LIB VER` if you want to execute rule 1-14. The `LIB VER` is the same as above.

If you don't want to run all rules, you can specify which rules to run by modifying the `rule_list` variable in `execute_testing_rules_multi.py` or `execute_testing_rules_15_16_multi.py`.

We also create a done file at `os.path.join(DATA_DIR, "rule_output", TEST_DONE_FILE)`. 

Both DATA_DIR and TEST_DONE_FILE are defined at `EAGLE\config.py`. 

The done file will record the config combination that are already executed so it won't be executed again. 

However, if you want to rerun the experiment, you should clean the done file first.

### Analyze results
After execution, run `python analyze_results.py LIB VER` under `EAGLE` directory to analyze the results for rules 1-16. Use `pythonanalyze_results_distributed.py` for the new rules regarding distributed versus non-distributed training and inference (e.g., rule 17). It will generate a `.csv` file which contains the api and input that cause inconsistent outputs. It contains four column: `rule, api_name, Linf, result_file`.

Noted that `EAGLE\config.py` defines a parameter `DATA_DIR` which is the location where all the input and output files are stored. Be sure that it is a valid path.
