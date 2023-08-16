### Text that we consider:
- Description
- doc_dtype (only for mxnet and pytorch). It is the string within the parantheses in the document (e.g., https://pytorch.org/docs/stable/generated/torch.nn.Conv1d.html#torch.nn.Conv1d)
- default value 

### "Descp" col:
- Description: the whole description for the parameter
- Doc_dtype: `DD: <doc_dtype text>`
- Default value: `DF: <the default value>`

### Normalization (Col "Normalized_descp"):

#### Normalization for the doc_dtype and description
- `D_TYPE` for data types. 
- `D_STRUCTURE`: for data structures including tensors (e.g., list, tuple, tensor, dict)
- `BSTR`: strings in brackets which is normally shape, e.g., "shape `[1,1]`" will be normalized to shape BSTR
- `QSTR`: strings in quotation marks (`, ', "). Normally enumerated type or range
- `PARAM`: the parameter's name of the same API. Note that we only normalize the parameter's name with more than one character. For example, we won't normalize the parameter `x` ot `a` to `PARAM` since it only has one character. 
- `CONSTANT_NUM`: contant number (integer)
- `CONSTANT_FLOAT`: constant float
- `CONSTANT_BOOL`: constant boolean (true or false)
- `REXPR`: relational expression, e.g., "a<=1" would be normalized to "a REXPR"

#### Normalization for default value:

There are four cases for the default value's normalization:
- `DEFAULT CONSTANT_NUM`: when the default value is an integer
- `DEFAULT CONSTANT_FLOAT`: when the default value is a float
- `DEFAULT CONSTANT_BOOL`: when the default value is a boolean constant (true/false)
- `DEFAULT DF_STR`: when the default valus is a string. 
- `DEFAULT <the default value >`: for some other cases 

#### `ONE_WORD`
To build the tree structure, we add `ONE_WORD` before the normalized text when there is only one word. 

For example, since the doc_dtype is usually one word, the normalized version of "NDArray" would be `ONE_WORD D_STRUCTURE`.



### Annotation

The are 6 cols to fill and their common values:
- dtype (`D_TYPE`, int, float, bool, string)
- structure: including data structure and tensor type  (e.g., `D_STRUCTURE`, list, dict)
- shape (e.g., `BSTR`, [2])
- ndim (e.g., `CONSTANT_NUM`, 0, 1)
- range: ( e.g., [0,inf))
- enum (e.g., QSTR)


Things to notice: 
- For all columns, fill in the IR(e.g., `D_TYPE`) if the corresponding value is normalized in the "normalized_descp" col. For example, the descp "input array" is normalized to "input D_STRUCTURE". So the IR (col "structure") would be `D_STRUCTURE` instead of `array`. 
- If the value is not normalized, fill in the actual value. For example, when there is "the number of....", according to our assumption, it should be an non-negative 0-D integer. The IR for dtype (col "dtype") is `int` instead of `D_TYPE`.
- When there is multiple values for one column, use `;` to separate. For example, if you think the parameter can be either 0-D or 1-D, in the column "ndim", input `0;1`.
- When there is dependency, for example "Must have the same type as PARAM", the "dtype" column should be `&PARAM`
- We usually assume `string` and `bool` are 0D, unless you think the context is really not clear. 


### Assumptions
The most common ones are "number of",  "name of", and "shape of".

Since it is hard to remember all assumptions, one easy way is after annotation, search for keyword and update all the IRs related to assumptions together (that's what I did, otherwise there might be some inconsistencies.)

Note: we usually assume `string` and `bool` are 0D, unless you think the context is really not clear. 




- `number of ..`: dtype:int, range:[0,inf), ndim: 0

- `name of`:
   dtype: string, ndim: 0


- `shape of `:
    dtype: int, ndim:1, range:[0,inf)

- `size/length/stride of`:  dtype:int, range:[0,inf)

- `width/height of`: 
    dtype: numeric, range: [0,inf)


- `axis of`: 
    dtype: int 0D

- `axes of`:
    dtype: int

- `index/indices`: 
    dtype: int, ndim: 0 unless pretty sure, e.g., the second index, otherwise leave ndim empty

- `ID`: 
    dtype: int, range: [0,inf)

- `dimension(s)`: 
    dtype:int

    
- `probability/ learning rate`:
    range: [0,1]  dtype: numeric

- other rate:
    dtype: numeric

- `max/min value / mean/variance / deviation / weight decay/ weight / matrix/ mat`:
    numeric

