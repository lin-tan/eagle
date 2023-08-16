

## Heuristics

#### Tensors/Type:

- [x] `Tensor` or `tensor`

- [x] Must be one of the following types: `type1, type2, type3` OR `type1`, `type2`...

- [x] **Must be one of the following types: not end with period, and all quoted**

- [x] **A type1, type2, ... or typen** 
  
  - e.g. A `bytes`, `str`, or `unicode` object.
  
- [x] **must be `type1`, `type2`, ... (or `typen`).**     
  - Must be is too general
  - Must be ...: not end with period, and all quoted 
    - e.g. Must be `float16`, `float32`, `float64`, `complex64`, `complex128` with shape `[..., M, M]`.'
  
- [x] Allowed dtype(s): ...

- [ ] ~~(One of ) type1 or type2~~

- [ ] ~~(One of) type1, type2, .. or type3~~

- [ ] ~~It could be `type1, type2, type3` OR `type1`, `type2`..~~

- [x] with/of  [\`'"]type/dtype[\`'"] {type....(list)}

- [x] **try with/of type {type} without   [\`'"] but only one word included** 

- [x]  `{type...or typen}` tensor
  
- match type with exsiting data types
  
- [x] **N-D type (tensor)**
  - e.g. 2-D float tensor
  - e.g. 1-D int

- [x] (A %-D(%D) {type1}) tensor of/with type(s) {type2, type3, type4 ...}

- [x] (A/an/non-type word) % {type} tensor
  
  - % could be positive/negative/non-zero/non-negative 
  
- [x] A/an {type}/`type`

- [x] {type}. OR `type`.

- [x] (Optional) type [,.]

- [x] (Optional) a/an {type}

- [x] An optional int

- [x] The {type} that/which/...

- [x] type (check the first word)

- [x] {the/maximum/minimum/..} number of ... -> int

- [ ] should be (a/an) {type}
  - should be a positive float
  - should be a list of n tensors
  - should be a tuple of strings
  - should be a `Tensor` or (possibly nested) tuple of tensors
  
- [ ] ~~an/a object of {type}~~

- [x] {type} type

- [x] (of/with) type {type}

- [x] {type} tensor

- [x] name -> string? (map)  (works pretty good)

- [x] avg_pool3d.yaml: and type ....

- [x] enum: must be {} or {}

  - [x] [pool.yaml](https://github.com/DNXie/DeepFlaw-Code/compare/17567eca2f9fdf9c42276e0c68a28cf473e1d3d7...master#diff-7d553f9fcd68f8187a92b31db81d3f5b)

  -  [arg_max.yaml](https://github.com/DNXie/DeepFlaw-Code/compare/17567eca2f9fdf9c42276e0c68a28cf473e1d3d7...master#diff-280e982f29285fc60493135c7c3147bd): An optional `tf.DType` from: `tf.int32, tf.int64`. Defaults to `tf.int64`.'
  - An optional `tf.DType` from: `tf.int32, tf.int64`.  （lu.yaml）

- [ ] (the/with the) same type/dtype/tf.dtype as/with `var` 

- [ ] special type

  - [ ] callable -> no shape information
  - [ ] tensorshape -> 1d tensor/tuple

- [x] [categorical_crossentropy.yaml](https://github.com/DNXie/DeepFlaw-Code/compare/17567eca2f9fdf9c42276e0c68a28cf473e1d3d7...master#diff-3ee0b65c2b96d4ea011f3747250875e0): float in [0,1]

- [x] Either an int/float （[enable_mixed_precision_graph_rewrite.yaml](https://github.com/DNXie/DeepFlaw-Code/compare/17567eca2f9fdf9c42276e0c68a28cf473e1d3d7...master#diff-947fb98ab7b7094c69566315029c1d4c)）

- [ ] ~~list of {} or {}~~

- [x] height or width of ....-> range [0,inf),  int/float

- [x] [mean_per_class_accuracy.yaml](https://github.com/DNXie/DeepFlaw-Code/compare/17567eca2f9fdf9c42276e0c68a28cf473e1d3d7...master#diff-84ec1638a0171519ae297b710fc458a5) whose shape is []]

- [x] whose rank is .. 

  - [x] either 1 or n-1
  - [x] either 1 or as the same rank as `some_var` 

- [x] defualt: float(-inf) -> float?



### Numeric

- [x] have numeric type.

- [x] numeric tensor 
- [x] Numeric threshold
- [x] of numeric type.



#### Rank:

- [x] %-D/dimension/dimensional or higher ( first)
- [x] %D or %-D or %d or %-d tensor  (dimension/dimensional)
- [x] one-dimensional -> 1D
- [x] two-dimensional -> 2D 
- [x] **of/with/and rank [><=] \d** 
- [x] of/with/and rank `{}`
- [x] scalar {} tensor -> 0D
- [ ] (the/with the) same rank/dimention as/with `var` 
- [ ] Keras tensor or variable **with `ndim >= 2`.'**
- [ ] that has length `>= 5`.
- [x] with `rank k >= 2`.
- [x] A `Tensor` with rank `k + 1`, where `k >= 1`.'
- [ ] A rank `R > 0` `Tensor` 
- [ ] N-D `SparseTensor`, where `N >= 2`.
- [x] A rank `n + 1` `Tensor`, `n >= 0` 
- [x] A list of `floats` that has length >= 4.  (length `*[><=]+ \d`*)
- [x] An int or list of `ints` that has length `1`, `N` or `N+2`.
- [ ] a single ..
- [ ] dict : don't have ndim=0



#### Shape

**Design**:

- Good example : nce_loss.yaml

- [?, 4] -> ? means unknown
- [num_classes, dim] -> `num_classes` and `dim ` are both unknown variables in the descriptions, may have correlationship among other inputs -> extract later
- [&num_classes, dim] -> with `&` (`&num_classes`) means another variable 
- [..., num_classes] -> N-D tensor, `ndim`= **UD**, stands for "unkown dimension", as using `N` may be confusing since description of other shape may contain `N`

- **shape_var**: a list of variables need to generate first, e.g. num_classes, dim... -> improve speed

  

- [x] (with/of)+ shape `[..]` or [..] or (..) or `(..)`

  - for most API, can only get dimension information, 

    - eg. A `Tensor` of shape `[batch_size, dim]`.  The forward activations of the input network.'

  - correlation: 

    - e.g. non_max_suppression_padded.yaml
      - boxes: A 2-D float `Tensor` of shape `[num_boxes, 4]`. 
      - scores: A 1-D float `Tensor` of shape `[num_boxes]` representing a single score corresponding to each box (each row of boxes).'

  - Error:

    - [x] I.e., `shape[0]` of the value returned by `op` must match `shape[0]` of the `RaggedTensor`s' `flat_values` tensors. OR  tf.shape(a)[:-2]
      - Solved: shape\s+ -> filter out shape[0]
      - must have with/of

    - [x] `int64` `Tensor` or `SparseTensor` with shape [D1, ... DN, num_labels] or [D1, ... DN], where the latter implies num_labels=1. N &gt;= 1 and num_labels is the number of target classes for the associated prediction. Commonly, N=1 **and `labels` has shape [batch_size, num_labels].** [D1, ... DN] must match `predictions`. Values should be in range [0, num_classes), where num_classes is the last dimension of `predictions`. Values outside this range are ignored.

      - Float `Tensor` with shape [D1, ... DN, num_classes] where N &gt;= 1. Commonly, N=1 and **predictions has shape [batch size, num_classes].** The final dimension contains the logit values for each class. [D1, ... DN] must match `labels`.

      - when 'has shape ..', check the word before it, if it is not this argument -> pass

    - [ ] [batch\*block_size*block_size, height_pad/block_size, width_pad/block_size, depth]

- [x] **Improve ndim information** 

- [ ] (the/with the) same shape as/with `var` 

- [ ] a scalar .. tensor







#### Booleans:

- [x] If/when true, ... (True, `true`, `True`)
- [x] If/when `Arg` is true, ..
- [x] True if ... /False if...
- [x] True iff..
- [x] boolean occurs
- [ ] `arg=True`
- [ ] ~~True enables ...~~
- [x] If this is set, 
- [x] boolean/bool that ..
- [x] Whether (to)..
- [x] whether or not ..
- [x] if any
- [x] Determines whether.. 



#### Range:

- [x] in/in the range `[/(  )/]`
- [x] non-negative
- [x] non-zero
- [x] positive
- [x] negative
- [x] **between \d to \d**
  - **Float between 0 and 1.**
- [x] **int/float >/>=  \d**
- [ ] An `int` that is `>= 2`.'
- [ ] An int > 1.
- [ ] A 0-D (scalar) `Tensor` > 0. 
- [ ] An int scalar >= 0,
- [ ]  must be > 0.



#### enum: (detect only quoted word)

- [x] A `string` from: ....

  - A `string` from: `"SAME", "VALID"`.

- [x] one of .. (default) ,...

  - **`mode`**: One of "CONSTANT", "REFLECT", or "SYMMETRIC" (case-insensitive)
  - one of `channels_last` (default) or `channels_first`

- [x] a/an optional tf.dtype/string/... from: ...

  - An optional `string` from: `"MIN_COMBINED", "MIN_FIRST", "SCALED"`.
  - An optional `tf.DType` from: `tf.int32, tf.int64`. Defaults to `tf.int32`.'

- [x] the type of the output: ..

  - The type of the output: `float16`, `float32`, `float64`, `int32`, or  `int64`.'

- [x] (and)... are supported. 

  - A string. ''NHWC'' and ''NCHW'' are supported.'

  - A string. ''N...C'' and ''NC...'' are supported. If `None` (the default) is specified then ''N..C'' is assumed.'

  - only `''euclidean''`, ''`fro''`, `1`, `2`, `np.inf` are supported.

    

- [x] a string, either () or ()

  - a string, either `''VALID''` or `''SAME''`

- [x] Only .. and .. are supported

  - only for : "Only string and integer types are supported. "





#### Others

- [x] Arg `name`/`%_name`: string
  - Ignore all the `name` argument. (with its default values)
- [x] (name) name of ... -> string
- [x] Args with name `fn`, `%_fn`, `func`, `%_func` -> executable/function
  - `f`/`_method`,`method` with "function"/"method" in the sentence -> callable
- [x] The type of ... -> dtype
- [x] Deprecated, does nothing. / Deprecated -> x
- [x] treat ` and ' equally 
- [x] `dtype` -> dtype
- [x] `dtypes` and `names` -> usually a list of dtype/string
- [x] `shape`/`_shape` : default 1D tensor/None
- [x] **Python integer. -> Int**







#### Non-type word

- scalar
- vector
- non-negative
- non-positive
- positive
- negative
- non-zero



## TODO:

- [x] **Get optional argument and default values from document**
- [x] revisit dtype with default values
  - None-> no datatype
- [x] **`simple_pat.yml` zero patterns -> need to check**
- [ ] **Need to deal with (a|an) (.\*) or (.\*)**
- [ ] **read papers**
- [x] **Keep count of patterns**
- [ ] dtype/shape -> of whose?
- [ ] **multiple variables (list/tuples/sequence/pairs/ list of pairs)**
  - How to express????
- [x] In the script parsing html
  -  if multiple `Args` found -> exception: https://www.tensorflow.org/api_docs/python/tf/Graph
  - Add html in the json files
  - delete <href>
- [x] Do I set deault values to some arguments? 
  - Example: **`shape`**: Gets the [`tf.TensorShape`](https://www.tensorflow.org/api_docs/python/tf/TensorShape) representing the shape of the dense tensor. (Usually shape should be 1D tensor)
  - The number of ... -> int?
- the API under tf.config?https://www.tensorflow.org/api_docs/python/tf/config
- some device-related API https://www.tensorflow.org/api_docs/python/tf/distribute/OneDeviceStrategy
  - We should focus on tensor-related OP
- [x] **For frequent itemset mining, print out the original sentences**
- [x] **For frequent itemset mining, replace datatype with placeholders**
- [x]  **fix web parsing issue**
  - [x] **arg -> argument**
- [ ] **try sequential pattern mining**
- [x] **ND constraints**
  - [x] [max_time, batch_size,  ...]  or  [..., N, N] 
  - [x] [d_0, d_1, ..., d_n]
  - [x] [D1, ... DN]
  - [x] [D1, ... DN, num_labels]
  - [x] dim1, dim2, ... dim(n-1)
  - [x] d_0, d_1, ..., d_{r-1}
- [x] **shape: len(thresholds)**  -> len:&threshold
- [ ] ndim: Indices in the range `[0, num_partitions)`.' -> **ndim<num_partitions**
- [x] implement `shape_var`
- [x] range: no list
- [x] write a readme
- [x] **enum datatypes**
- [ ] New Patterns:
  - [x] An int32/int64,, A `complex64`/`complex128` 
  - [x] ^A/An {}  (only one word)
  - [x] ... instances  (for complex object, not useful for regular dtype )
  - [x] path - > string
  - [x] Optional non-negative integer or `int32` scalar `tensor` giving the number
    - optional (non-type word) ? 
    - optional (non-type word) ? or ?
    - [ ] Optional 2d int32 lists with shape [...]
- [x] **findall, instance(str)** bug!
- [ ] axes -> int
- [ ] special type:
  - [ ] scalar
  - [ ] callable (no dtype, shape, ndim..)
  - [ ] "A dictionary..." -> no other dtype
  - [ ] iterable of which dtype
- [x] A list of `Tensor` objects, each with same shape and type.
- [x] An int or list of `ints` that has length `1` or `3`.  
  - avg_pool1d.yaml
- [x] An int or list of `ints` that has length `1`, `N` or `N+2`.
  - conv_transpose.yaml
- [x] A list of `ints` that has length `>= 4`
  - fractional_avg_pool.yaml  ( no `)
  - extract_image_patches.yaml
- [x] tuple/list of 2 integers
  - Conv2DTranspose.yaml
- [x] or tuple/list of a single integer (DepthwiseConv2D.yaml) 
- [x] Tuple or list of integers  
- [x] a single integer  (LocallyConnected1D.yaml ,   LocallyConnected1D.yaml)
- [x] a non-empty list of strings
- [ ] A list with the same length as `values` of `Tensor` objects with type `float32`.  (quantized_concat.yaml)
- [x] **dictionary**
  - [x] dict of {} to {}
  - [x] a dictionary ..
- [x] iterable 
- [x] **readme**
- [x] **have all maps in one file**  map all type in dtype (merge tensor_t and dtype code )
- [ ] have structure constraints in `pat_varname`
- [ ] Last dimension must be size 3.'
- [ ] **1-D tensor of length {}**
- [ ] **enum-> case sensitive**
- [ ] Optional `Tensor` whose rank is either 0, or the same rank as `labels`, and must be broadcastable to `labels` (i.e., all dimensions must be either `1`, or the same as the corresponding `losses` dimension).'
  - very common sentence (31)
- [x] **change enum to findall**
- [x] check https://www.tensorflow.org/versions/r2.1/api_docs/python/tf/keras/preprocessing/image/apply_affine_transform on enum
- [ ] A 1D tensor  -> shoudn't be ndim=0
- [ ] either a `SparseTensor` of float / double weights -> type1/type2
- [x] descp: '''SAME'' or ''VALID'''  and  descp: '''left'' or ''right'';    -> enum
- [x] all values must be >= 0
- [x] An integer specifying dimension of the embedding, must be > 0.
- [x] extract more Tensorshape : shape of ...
- [ ] be either `1`, or the same as the
- [ ] of/with/have/has the same (type and shape/ shape and type) with/as `<var>`



##Read

- [x] https://www.cs.purdue.edu/homes/lintan/projects.html
- [x] **（frequest itemsets mining） chapter6 https://uwspace.uwaterloo.ca/handle/10012/8934**
- [ ] https://www.cs.purdue.edu/homes/lintan/publications/webapi-msr18.pdf
- [ ] https://uwspace.uwaterloo.ca/handle/10012/15506
- [ ] https://link.springer.com/article/10.1007/s10664-018-9600-2





### Errors:

- [ ] **Indices -> unique?**

- [x] **depracated function**

- multiple variables (list, tuple)

- or

- pattern: tensor -> too loose 
  
- FP: a list of `tensor`
  
- [x] default: with ()  
  - e.g. https://www.tensorflow.org/api_docs/python/tf/keras/layers/AveragePooling3D
  - default: (2, 
  
- check the word 'float' 
  - A small float number to avoid dividing by 0.
  - A float representing 
  
- tf.case.yaml

  - pred_fn_pairs, ndim

  

















## Collections

### Tensor

- 1-D or higher numeric Tensor   (with `)
- A Tensor. 
- N-D tensor.
- K-D boolean tensor / 0-D int Tensor 
- A rank 1 integer Tensor
- Must be one of the following types: int32, int64.
- A tf.DType from: tf.bfloat16, tf.half, tf.float32, tf.float64, tf.int64, tf.int32, tf.uint8, tf.uint16, tf.uint32, tf.uint64, tf.int8, tf.int16, tf.complex64, tf.complex128, tf.qint8, tf.quint8, tf.qint16, tf.quint16, tf.qint32.
- Must be float16, float32, float64, int8, uint8, int16, uint16, int32, int64, complex64, complex128, bool or string.
-  Tensor of types float32, float64, complex64, complex128
- A Tensor or SparseTensor or IndexedSlices of numeric type. It could be uint8, uint16, uint32, uint64, int8, int16, int32, int64, float16, float32, float64, complex64, complex128, bfloat16.
- A 0-D (scalar) Tensor > 0.
- A 0-D (scalar) Tensor of type float
- A 0-D (scalar) Tensor, or a Tensor with the same shape as t.
- 0-D int32 Tensor.
- A scalar ...
- A list of Operation or Tensor objects
- string. Optional job name.
- A list of at least 1 Tensor objects with type int32.
- 5-D Tensor with shape [batch, in_planes, in_rows, in_cols, depth].
- Non-negative int32 scalar Tensor 
- Scalar int32 Tensor.
- Shape [2] Tensor of same dtype as values. 
- should be an int in [0,num_input_pipelines).
  

### Multiple Tensors/Others (LATER)

- A tuple or list of mixed Tensors, IndexedSlices
- x is a sequence of Tensor inputs to the function.
- A list of at least 1 Tensor objects with type int32.
- A list of ints that has length >= 5.
- A list or tuple of Python integers or a 1-D int32 Tensor.
- A tensor or (possibly nested) sequence of tensors
- Optional tuple of tf.autograph.experimental.Feature values.
- A Tensor or list of tensors to be differentiated.
- A list of Tensor objects.
- One of tf.int32 or tf.int64.
- A list or tuple of tensorflow data types or a single tensorflow data type ...
- A list of integers, a tuple of integers, or a 1-D Tensor of type int32.
- values: A list of Tensor objects with the same shape and type.



### Coorelation

- Must have the same type/shape as start. 
- label_dtype: A tf.dtype identifies the type of labels. By default it is tf.int64. If user defines a label_vocabulary, this should be set as tf.string. tf.float32 labels are only supported for binary classification.
- dtypes: A list of DType objects. The length of dtypes must equal the number of tensors in each queue element.
- A 0-D Tensor or Python value of type dtype.  https://www.tensorflow.org/api_docs/python/tf/random/uniform
  

### Boolean

- Boolean: If True,... If you require a stable order, pass stable=True for forwards compatibility.
- A boolean that 
- True iff.. 
- A list of Tensor objects or a single Tensor.
- When True, ...
- An integer or a scalar 'Tensor'. 
- If this is set, ..



### Shape/Rank

- Tensor of shape [..., N, N].
- whose shapes should be consistent with equation.
- A 0-D (scalar) Tensor, or a Tensor with the same shape as t.
- Must be: [1, stride_planes, stride_rows, stride_cols, 1].
- Must have rank 1 or higher.
- Tensors with rank 1.
- A tensor with rank 2 or higher and with shape [b, x1, ..., x_m].
- Must be at least rank axis + 1.
- Must be less than rank(indices). (rank is one of the args)
- len(repeats) must equal input.shape[axis] if axis is not None.



### Values

- a value which can either hold 'none' or 'zero' 
- Non-negative int32 scalar Tensor 
- Non-zero
- positive
- All elements must be >= 0. 



### Default

-  (optional, default: 'greedy').
- default: True
- Defaults to "EnsureShape"/some args/some values.
- If func is None,...
- and it defaults to 'none'.
- (default: 1)
- If not specified, 
  



### Range

- axis must be in range [-(D+1), D]
- A list of ints that has length >= 5.
- Non-negative int32 scalar Tensor 
- Must be in range [0, params.shape[axis]).
- should be an int in [0,num_input_pipelines).



### Enum

- A string from: "SAME", "VALID".
- mode: One of "CONSTANT", "REFLECT", or "SYMMETRIC" (case-insensitive)
- A value which can either hold 'none' or 'zero' 
- The type of the output: float16, float32, float64, int32, or int64.



### Others

- A Python scalar, list or tuple of values, or a N-dimensional numpy array. 
- A list of Operation or Tensor objects
- Default: True.
- Deprecated, does nothing.
- aggregation_method: Specifies the method used... -> callable
- f: function f(*x)
- \*inputs: Zero or more tensors to group.
- Path to..  (file path)
- verify_shape: Boolean that enables verification of a shape of values.