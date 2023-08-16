**Example sentences**:

- Must be one of the following types: `int32`, `int64`.

- Must be one of the following types: `bfloat16`, `half`, `float32`, `float64`, `int64`, `int32`, `uint8`, `uint16`, `uint32`, `uint64`, `int8`, `int16`, `complex64`, `complex128`, `qint8`, `quint8`, `qint16`, `quint16`, `qint32`.

-  Must be one of the following types: `int8`, `int16`, `int32`, `int64`, `uint8`, `uint16`, `uint32`, `uint64`.

- Must be one of the following types: `half`, `bfloat16`, `float32`, `float64`.


Before the mining, we replace the dtype word to **SOME_DTYPE**. So the **sub-sequence** would be 

> must be one of the following types: SOME_DTYPE, SOME_DTYPE, ...


**Rules**:

`must be one of the following types: <dtype1>, <dtype2> ...<dtypen>`




