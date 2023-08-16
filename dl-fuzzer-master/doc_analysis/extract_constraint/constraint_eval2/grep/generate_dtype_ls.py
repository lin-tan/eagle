import yaml
import sys
sys.path.insert(0,'../../')

from extract_utils import *

dtype_map_file = {
    'tf': '/Users/danning/Desktop/deepflaw/exp2/code/dl-fuzzer/doc_analysis/extract_constraint/tf/patterns/dtype_map.yml',
    'pytorch': '/Users/danning/Desktop/deepflaw/exp2/code/dl-fuzzer/doc_analysis/extract_constraint/pytorch/patterns/dtype_map.yml',
    'mxnet': '/Users/danning/Desktop/deepflaw/exp2/code/dl-fuzzer/doc_analysis/extract_constraint/mxnet/patterns/dtype_map.yml'
}

result = {}

stop_type = [   # don't replace with "SOME_DTYPE"
    # 'tensor',
    # 'tf.tensor',
    # 'tensors',
    'shape',
    'method',
    'function', 
    # 'dtype',
    'types',
    'type',
    'number',
    'operation',
    'callable',
    'size',
    'path',
    'name',
    'names',
    'images',
    'image',
    # 'floating',
    'dimension',
    'dimensions',
    'deprecated',
    'long',
    'context',
    'ctx',
    'timedelta',
    'tf.tensorshape', 
    'tensorshape',
    'torch.size',
    'python:int',
    'python:ints',
    'python:integer',
    'python:integers',
    'tensorproto'
]

shared_structure = [
  "list",
  "lists",
  "array",
  "arrays",
  "tuple",
  "dict",
  "dictionary",
  "iterable",
  "sequence",
  "ndarray",
  "array_like"
]


for framework in dtype_map_file:
    dtypes = []
    structures = []
    tensors = []
    content = read_yaml(dtype_map_file[framework])
    for cat in content:
        if cat=='structure':
            structures+=content[cat]
        elif cat == 'tensor_t_map':
            tensors+=content[cat]
        else:
            dtypes+=content[cat]
    
    result[framework] = {}
    result[framework]['dtype'] = [x for x in dtypes if x not in stop_type]
    result[framework]['tensor_t'] = [x for x in tensors if x not in stop_type]
    result[framework]['structure'] = shared_structure
    #result[framework]['structure'] = [x for x in structures if x not in stop_type]

    result[framework]['dtype'] = list(set(result[framework]['dtype']))
    result[framework]['tensor_t'] = list(set(result[framework]['tensor_t']))
    #result[framework]['structure'] = list(set(result[framework]['structure']))

save_yaml('./dtype_ls.yaml', result)
    
