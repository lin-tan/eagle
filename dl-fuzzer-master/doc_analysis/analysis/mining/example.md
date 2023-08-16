

| sequence                 | example sentence              | pattern           | match cnt |
| ------------------------ | ----------------------------- | ----------------- | --------- |
| [`tensor`, `SOME_DTYPE`] | A `Tensor` of type `float32`. | `of type <dtype>` | 216       |
| [`SOME_DTYPE`, `tensor`] | An integer tensor             | `<dtype> tensor`  | 292       |





| sequence               | example sentence                                             | pattern                                                    | match cnt |
| ---------------------- | ------------------------------------------------------------ | ---------------------------------------------------------- | --------- |
| [`must`, `SOME_DTYPE`] | Must be one of the following types: `int32`, `int64`.        | `must be one of the following types: <type1>, <type2>, ..` | 235       |
| [`SOME_DTYPE`, `must`] | int32 or int64, must be in the range `[-rank(input), rank(input))`. | `must be in the range <range>`                             | 38        |





| sequence           | example sentence                           | pattern                                | match cnt |
| ------------------ | ------------------------------------------ | -------------------------------------- | --------- |
| [`tensor`, `type`] | A `Tensor` of type `float32` or `float64`. | `tensor of type <type1>, <type2>, ...` | 208       |
| [`type`, `tensor`] | A type for the returned `Tensor`.          | `a/an <dtype>`                         | 768       |





| sequence               | example sentence                                  | pattern                     | match cnt |
| ---------------------- | ------------------------------------------------- | --------------------------- | --------- |
| [`tensor`, `elements`] | A 1-D tensor of 2 elements                        | `tensor of <shape> element` | 7         |
| [`elements`, `tensor`] | The type of the elements of the resulting tensor. | `^the <dtype>`              | 105       |





| sequence                    | example sentence                                             | pattern                  | match cnt |
| --------------------------- | ------------------------------------------------------------ | ------------------------ | --------- |
| [`input`, `tensor`, `size`] | the input tensor of size (*, m, m) .                         | `tensor of size <shape>` | 21        |
| [`size`, `input`, `tensor`] | the size of `input` will determine size of the output tensor. | not useful               | /         |







