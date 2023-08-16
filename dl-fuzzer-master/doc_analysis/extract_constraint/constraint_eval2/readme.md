|                                 | TF    | Pytorch | MXNet |
|---------------------------------|-------|---------|-------|
| # args                          | 167   | 71      | 296   |
| # constraints manually detected | 346   | 113     | 442   |
| Accuracy                        | 86.8% | 94.4%   | 92.9% |
| Precision                       | 96.7% | 99.1%   | 97.3% |
| Recall                          | 93.6% | 96.5%   | 96.4% |


- format of the csv file: <APIname\>-<argname\>.csv, e.g. mxnet.autograd.backward-head_grads.csv

- Four categories: prim_dtype, nonprim_dtype, shape, validvalue

- format of constraints: <sub-category1\>(contraint1, constraint2, ..),<sub-category2\>(contraint1, constraint2, ..)
    - e.g. for shape: `shape([a,b], [a,b,c]), ndim(0,2,3)`

- Path: 
    - Yitong: `dl_fuzzer/doc_analysis/extract_constraint/constraint_eval2/(mxnet/pytorch/tf)/yitong/*.csv`
    - Mijung: `dl_fuzzer/doc_analysis/extract_constraint/constraint_eval2/(mxnet/pytorch/tf)/mijung/*.csv`

- Constraints extracted from *varname*, *descp1*, *descp2*, and *default value*.


- If the constraint for some category is not correct (incomplete/incorrect)
    - 0 precision + 0 recall
    - add a new line (only need to fill the last 4 columns: category, constraint, in_doc, extracted)
        - the *category* column need to be exactly one from "prim_dtype, nonprim_dtype, shape, validvalue"
        - the *constraint* column don't need to be well-format, as long as we can understand, just in case we have disagreement.
        - in_doc and extracted column would be 0 or 1
    - Old line: 0(in_doc), 1(extracted) 
    - New line: 1(in_doc), 0(extracted) 


- If correct: 1 (in_doc), 1(extracted)
- If missing: add new line 1(in_doc), 0(extracted) 





- tips:
  
    - Only need to check the first and the last one.
        - must be one of the fsollowing dtypes <dtype1\> <dtype2\> ...
        - (enum) only <enum1\> <enum2\> ... are supported
    - "An integer, " -> 0d 
    - "An int tensor" -> No dimension information
    - boolean/string is by default 0d (so with/without 0D is both correct), unless you are not sure
    - `list(int)` is equal to `list` in fuzzer

    


## Assumptions

- number/length/size of ... 
    - int
    - [0,inf)
    - 0 dimensional (not necessary)

- width/length of.. 
    - numeric

- learning/drop/decay... **rate** 
    - float
    - [0,1]

- probability..
    - float
    - [0,1]

- dimension 
    - int


- the axis .. 
    - int
    - 0 dimensional

- the axes ..
    - int
    - 1 dimensional
    
    
    
- matrix/matrices

    - numeric

...


## Assumptions on variable name

- name
    - string

- .._id
    - int
    - [0,inf)

- num_..
    - int
    - [0,inf)

- .._shape
    - tuple(int)

- .._prob
    - float
    - [0,1]

- .._width/length/size:
    - numeric


- .._axis 
    - int
    - 0 dimensional

- .._axes
    - int
    - 1 dimensional


- stride
    - int
    - [0,inf)


- dim/dimension
    - int
    

...
