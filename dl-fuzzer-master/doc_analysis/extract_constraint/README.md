

### yaml files

|                | Total (API) | Collected | Changed | Unchanged |
| -------        | ----------- | --------- | ------- | --------- |
| TF(remove v1)  | 2588        | 949       | 915     |    34     |
| Pytorch        |             | 415       | 404     |    11     |
| MXNet          |  1866       | 959       | 954     |    5      |
| Total          |  1866       | 2323       | 2273    |           |

With layer APIs

|                | Total (API) | Collected | Changed | Unchanged |
| -------        | ----------- | --------- | ------- | --------- |
| TF(remove v1)  |             | 1008      | 959 (95.1%)|         |
| Pytorch        |             | 529       | 507 (95.8%) |         |
| MXNet          |             | 1021      | 1010 (98.9%) |          |
| Total          |             | 2558      | 2476 (96.8%)    |           |

### Mining:

7070 sentences

### APIs related to Class

478 listed in `./class_api`





## Yaml file format:



An example:

~~~yaml
link: https://www.tensorflow.org/api_docs/python/tf/nn/avg_pool
package: tensorflow
target: avg_pool
title: tf.nn.avg_pool
version: 2.1.0
inputs:
  optional:
  - data_format
  - name
  required:
  - input
  - ksize
  - strides
  - padding
outputs: A `Tensor` of format specified by `data_format`. The average pooled output tensor.
constraints:
  data_format:
    default: None
    descp: ' A string. Specifies the channel dimension. For N=1 it can be either "NWC"
      (default) or "NCW", for N=2 it can be either "NHWC" (default) or "NCHW" and
      for N=3 either "NDHWC" (default) or "NCDHW".'
    dtype:
    - tf.string
    enum: 
    - NWC
    - NCW
    - NHWC
    - NCHW
    - NDHWC
    - NCDHW
  input:
    descp: '  Tensor of rank N+2, of shape `[batch_size] + input_spatial_shape + [num_channels]`
      if `data_format` does not start with "NC" (default), or `[batch_size, num_channels]
      + input_spatial_shape` if data_format starts with "NC". Pooling happens over
      the spatial dimensions only.'
    dtype:
    - tf.tensor
    ndim:
    - 1        (INCORRECT)
    shape:
    - '[batch_size]'  (INCORRECT)
  ksize:
    descp: ' An int or list of `ints` that has length `1`, `N` or `N+2`. The size
      of the window for each dimension of the input tensor.'
    dtype:
    - int
    tensor_t:
    - tf.tensor
    ndim: 
    - 1
    shape:
    - [1]
    - [n]
    - [n+1]
  name:
    default: None
    descp: ' Optional name for the operation.'
    dtype:
    - tf.string
  padding:
    descp: ' A string, either `''VALID''` or `''SAME''`. The padding algorithm. See
      the "returns" section of `tf.nn.convolution` for details.'
    enum: 
    - VALID
    - SAME
  strides:
    descp: ' An int or list of `ints` that has length `1`, `N` or `N+2`. The stride
      of the sliding window for each dimension of the input tensor.'
    dtype:
    - int
    tensor_t:
    - tf.tensor
    ndim: 
    - 1
    shape:
    - [1]
    - [n]
    - [n+1]
dependency:
	- batch_size
    - n
~~~



#### How did I get the default value (How do I know a input variable is optional):

In the webpage for each API, for example [clip_by_value](https://www.tensorflow.org/api_docs/python/tf/clip_by_value), there is a code snippet as a signature of the API:

~~~python
tf.clip_by_value(
    t, clip_value_min, clip_value_max, name=None
)
~~~

From the code, we know there is four input variables, and one of them (`name`) is optional (with `=`), which has the defualt value `None`.



### Constraints

#### dtype

A list of all possible datatypes. All stored as **string**

The acceptable dtype list:

Tensorflow: https://bitbucket.org/lintan/dl-fuzzer/src/master/tensorflow/tensorflow_dtypes.yml

pytorch: https://bitbucket.org/lintan/dl-fuzzer/src/master/pytorch/pytorch_dtypes.yml

mxnet: https://bitbucket.org/lintan/dl-fuzzer/src/master/mxnet/mxnet_dtypes.yml


Possible format:


- type `scalar` represents **0-D numeric tensor**
- `dtype:&var`: the same dtype with input parameter `var`
- `dtype:var`: the save dtype with `var`, where `var` is not an input parameter



#### tensor_t

a list of acceptable types of tensor.

For Tensorflow: 

- tf.tensor
- SparseTensor


For Pytorch: 

- torch.tensor
- SparseTensor

For MXNet:

- tensor

#### structure

a list of acceptable python data structures, including list, tuple and dictionary

possible format and values:

- `list(int)`
- `list`  : unkown datatype
- `tuple(float)`
- `tuple` : unknown datatype
- (deprecated)`dict(a:b)`
- (deprecated) `dict(int:?)` `?` represents unknown type
- `dict` : unknown datatype
- `iterable(string)`: iterable of some datatype
- `iterable`: iterable of unknown datatype
- `tuple:(dw,dh)`: `(dw,dh)` is the value of the tuple, which can be found in `dependency`.


MXNet-specific:

- `ndarray`
- `sparse_ndarray`


#### ndim

A list of all possible number of dimension. Stored **All AS String**  . Extracted both from pattern and shape.

All possible values:

- some integer, stored as **string** 
- `>2`: higher than 2. 2 can be any integer, stored as **string** Usually extracted from following cases:
  - 2-D or higher
  - shape [..., m, m] -> at least 2D
-  (deprecated) `?` represents unknown number of dimension, stored as **string**. Usually extracted from following sentences:
  - N-D tensor
- `ndim:labels`: as the same ndim as the `labels`
- `ndim:&labels`: as the same ndim as the input parameter `labels`



##### How are ndim constraints extracted:

- patterns (mentions ndim information in the description)

- shape 

- dtype patterns:

  - **a/an** right before dtype word
  - a/an dtype1, dtype2, ... or dtypen
  - the {dtype} ...
  - {dtype} ... (dtype word at the begining of the sentence)
  - scalar tensor
  - python integer/float

  If the dtype is one of the following, then ignore:

  - plural (e.g. integers/ints/floats/strings/dtypes/**image(s)**/...)
  - tensor
  - sparsetensor

  



#### shape

A list of all possible shape with brackets `[..]`. All stored as **string**,  where there could be `+-*/` operation symbols.

All possible format:

- `[2,2]` , all element are integers. 

- `[2]` a 0d tensor with length 2

- `[>=5]`: length larger than 5

- `[batch_size,num_labels]`: some word extracted directly from the document, stored in `depedency` . 

- `[&num_classes,dim]`: the word with `&` in front of it means this is some input variable, which means this dimension should be the same as the value of this input variable, in this case, `num_classes`. 

- `[...,num_labels]`: `...` means unknown number of dimension. 

- `[len:&dim]`: length of the variable `dim`. In the original document, it is usually stated as `len(dim)`. Note that it can be both of the following cases:
  
  - `[len:dim]`  (in this case, add `dim` into `depedency`)
  - `[len:&dim]`
  
  The same with `ndim:` and `max_value:`
  
- `[ndim:&m]` : number of dimension of other variable `m`. In the original document, it is usually stated as `rank(dim)`. 

- `[max_value:&m]`: the max value in the variable `m`.

- `shape:&var`: the same shape with variable `var`

- `shape:var`: the save shape with `var`, where `var` is not an input variable



**To use the shape information:**

1. parse the string in the brackets (`[]` ) by comma (`,`)
2. it can be:

   - integer
   - some variable (placeholder) that you can find at `depedency` 
   - word starts with `&`, which refers to another variable
   - `...` : an unknown number of dimension 
   - `len:sth` : length of some variable
   - `ndim:sth`: number of dimension of some variable.



#### range

A **value (not list)** of the range this input variable, or each element in the input list/tensor/tuple/... . The value is stored as **string** in a open(`()`) or closed (`[]`) interval, where there could be `+-*/` operation symbols.

All possible format:

- `(0,inf)` :  positive

- `[0,inf)`: non-negative (0 included)

- `(-inf,0]`: negative

- `[0,1]` 

- `[a,b)` : some word that is also in `dependency`  (rare case)

- `[0,&num_reserved_ids)` : where `num_reserved_ids` is another input variable

- `[-ndim:&input,ndim:&input)` : extracted from `[-rank(input), rank(input))` .  Note that it can be both of the following cases:

    
    - `[ndim:input]`  (in this case, add `input` into `dependency`)
    - `[ndim:&input]`


- `[len:&vocabulary_list,len:&vocabulary_list+&num_oov_buckets)`: extracted from `[len(vocabulary_list), len(vocabulary_list)+num_oov_buckets)`. And there could be `+-*/` operation symbols.

- (deprecated)`[max_value:&m]`: the max value in the variable `m`. 



#### enum

A list of all supported input values stored as **string**.

