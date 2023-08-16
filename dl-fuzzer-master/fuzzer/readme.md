# Usage of each script

## fuzzer-driver.py

The entry of the fuzzer 

The input it takes:

- **(required)**`target_config`: The configuration file (`.yaml`) for the ONE target function under test (i.e. the input information and constraints)
- **(required)**`dtype_config`: The configuration file to specify the valid data types, which is specific to each library.
- `workdir`: Work directory to store the suspicious inputs; if none provided, will store in current workdir
- `data_construct=None`: Optional constructor function for building the input. 
  
    - For `tensorflow`: use the defualt value (`None`) as tensorflow doesn't require any specific data structure to construct the input. 
    - For `pytorch`: pass `tensor` so that the fuzzer will use `torch.tensor` to construct inputs.
    - For `mxnet`: pass `nd.array` so that the fuzzer will use `mxnet.nd.array` to construct inputs.


- `fuzz_optional_p=1`: A float within in [0,1] that indicates the ratio of optional parameters to be genrated, i.e. `optional_ratio` in the paper. If non-zero value given, for each optional parameter, the fuzzer will generate it with probability `fuzz_optional_p`. 
- `model_test=False`: Flag indicating whether to generate input for the layer APIs. 
- `check_nan=False`: Flag indicating whether to report NaN errors of the layer API inference. 
- `mutate_p=0`: Probablity to mutate each parameter to one of the boundary cases. 
- `guided_mutate=False`: Flag indicating whether to use guided mutation to maximize mutation operation coverage, i.e., use the unused mutator first. 
- `special_value=False`: Flag indicating whether to include special values (e.g., `inf`, `nan`) when mutating inputs to boundary cases. (We set it to `False` as we decide not to include them)
- `gen_script=False`: Flag to specify whether to generate a python script for the testing
- `save=False`: Flag to specify whether to save all generated input and python script even it is not related to crash. (We set it to `False` to save space)
- `ignore=False`: If specified, the fuzzer ignores the given constraints
- `obey=False`: Flag indicating whether the fuzzer should obey(follow) the given constraints. If set to `False`, the fuzzer will violate the constraints. 
- `max_iter=0`: The maximum number of iterations the fuzzer runs
- (Deprecated)`max_time=0`: The maximum time in seconds the fuzzer runs. Will be overrided if `max_iter` is provided.
- `timeout=5`: Timeout limit for each testing run, default to 5 sec
- `verbose=False`: Verbose flag whether to block output during testing phase

  




Example of calling executing `fuzzer-driver.py`:

~~~python
python fuzzer-driver.py \
.../tf.linalg.cholesky_solve.yaml \
../tensorflow/tensorflow_dtypes.yml \
--workdir=../../../workdir/tf.gather.yaml_workdir \
--obey  --mutate_p=0.2 --fuzz_optional_p=0.6 --max_iter=1000 --gen_script --timeout=10 \
> .../output
~~~



### The parameter to pass when run the experiment:

#### The same parameter for each mode:
  - `target_config`
  - `dtype_config`
  - `workdir`
  - `--fuzz_optional_p=0.6`
  - `--max_iter=xxx` 
  - `--gen_script` 
  - `--timeout=10`
  - `--model_test`
  - `--check_nan`
  - `--data_data_construct=tensor` for pytorch, `--data_data_construct=nd.array` for mxnet
#### The parameter for **baseline**:
  - `--ignore`
  - `--obey`
  - `--mutate_p=0`
  - `--guided_mutate`  (will be ignored if `mutate_p=0`)
####  The parameter for **baseline+Boundary-case mutation**:
  - `--ignore`
  - `--obey`
  - `--mutate_p=0.2`
  - `--guided_mutate`
####  The parameter for **baseline+Constr,**:
  - `--obey` if CI mode
  - `--mutate_p=0`
  - `--guided_mutate`  (will be ignored if `mutate_p=0`)
####  The parameter for **baseline+Boundary-case mutation+Constr (`DocTer`)**:
  - `--obey` if CI mode
  - `--mutate_p=0.2`
  - `--guided_mutate`



### The output files of the fuzzer:

- `fuzzing_config`: the values of each input parameter (e.g. `mutation_p`, `obey`, etc) to the fuzzer are saved here.
- `gen_order`: the file path of the genrated input with its order
- `script_record`: the file path of the genrated python script with its order
- `failure_record` : the input that fails the test with its order (in CI mode, the input with exception is considered as **fail**, and in VI mode, the input that pass the validity checking is considered as fail.)
- `failure_script_record`: the generated python script that fails the test with its order
- `exception_record`: the exception file path with its order. Currently it is only used for keeping the count of the exception rate. The actual exception file is not saved unless with `--save=True` 
- `XX_record`: `XX` could be *Segmentation_fault*, *Abort*, *Floating_point_exception*, etc. The file keeps record of the input that triggered the corresponding crash. 
- `XX_script_record`: The file keeps record of the python script that triggered the corresponding crash. 
- `fuzz_time`: the total time used for generating and exercising  `max_iter` inputs for the API
- `mutate_op_coverage.csv`: it keeps record of the coverage information of each boundary-case mutator.





## fuzz_config.py

Save and pre-process the configuration of the fuzzer, including:

- Check the validity of the paramter and input files. 

- Parse the API config file and create `param` object for each parameters

- Set the generation order of the parameter by building a topological graph.

## fuzzer.py

 Implementation of the fuzzer (class `Fuzzer`).

The `fuzzer-driver.py` file first calls `Fuzzer.run(...)` function to starts fuzzing, which then calls `Fuzzer._run_max_iter` to run tests for `max_iter` iterations. In function `Fuzzer._run_max_iter`, it calls `Fuzzer._generate_new_input` to generate new inputs either conforming or violating the constraints if any, (only one parameter's constraints will be violdated in VI mode) then it calls `Fuzzer._test` to pass the input to the corresponding API. Then it creates new process and calls either `_expect_ok` (CI mode) or `_expect_exception`(VI mode) to exercise the input,  waits for the returned status or signals of the process, and saves the inputs if it crashes. 

The difference between `_expect_ok`  and  `_expect_exception`:

- (Deprecated) keep record of the passing inputs for further usage (adaptive generation). 

- (Deprecated) Keep record of the consecutive failure count. 

- Keep record of test success and failure, for example, in `_expect_ok`, `PASS` indicates no exceptions, `FAIL` indicates exceptions. Note that both `PASS` and `FAIL` means no crash. And we currently don't use this information. 

  

## param.py

Parameter class (`Param`) to store the information about each input parameter, it includes the implementation of

- constraint parsing and pre-processing
- generating inputs either conforming or violating the constraint in function `Param.gen`.
    - if there is `enum` constraints, skip all the other constraints, generate vlaues following/violating the `enum` constraints. 
    - Otherwise, the step-by-step process of input generation:
        - pick a `shape` of `ndim` dimension or generate one if not specified in the constraints.
        - generate data with the corresponding `dtype` and `shape`
        - If the parameter are chosen to be mutated to one of the boundary cases, the mutation is conducted here.
        - convert the data into corresponding data structure (list/tuple/tensor) as specified in the constraints. If not specificed, convert to the data structure specified as `data_construct` passed in `fuzzer-driver.py`. 
- **Constriant violation details** (in VI mode, the fuzzer will choose only ONE parameter WITH constraint to violate. If the parameter is chosen, only one of the following category will be violated. The fuzzer will NOT pick the category that the parameter has no constraints for.)
    - `dtype`: pick one dtype that is not specified in the constaints. Note that `int32` is not a violation of `int64`, and `float32` is not a violation of general `float`.
    - `ndim`: pick a integer within [0,5] that is not specified in the constaints.
    - `range`: If the range specified in the constraint is `[0,inf)`, the violated range will be `(-inf,0]`. If the specified range is `[0,1]`, the violated range will be either `(-inf,0]` or `[1,inf)`. Note that the boundary is not taken care of.
    - `enum`: If the enumerated values are integers, for example, `enum={1,2,3}`, generate 0 or 4 as violated values. Otherwise, pick one enumerated value and mutate it with one edit distance (delete/insert/replace one character), for example, mutate `VALID` to `VALD` or `VSLID`.



## param_util.py

The impelementation of the class of range (`Range`) and mutation (`Mutator`).

- The class `Range` keeps record of the range constraint and contains some useful methods like `set_boundary` and`get_boundary` which sets and gives the boundary value of the range. 

- The class `Mutator` conducts the (guided) boundary-case mutation for the parameters. It implements 6 boundary case mutators:

    - Extreme values: set the parameter or an element of the parameter to extreme value. Extreme value is chosen from the boundary values of the chosen "range" of the parameter in this iteration. For example, if the range is [0,1], the boundary cases will be 0 and 1. If there is no range constraints, the fuzzer will use the boundary values (MAX and -MAX) of the current chosen `dtype`.
    - None: set the parameter or an element of the parameter to `None`.
    - zero: set the parameter or an element of the parameter to 0
    - zero dimension: set the size of one of the dimension to zero. 
    - empty list
    - empty string

Besides, the mutator keeps record of the used mutator on the parameter, so that in the *guided*  mutation mode, the mutator will choose to use the unused mutator first.





## util.py

utility functions to aid the fuzzer



## constant.py

constants defined for the fuzzer


## errors.py

Defines the exception for the fuzzer
