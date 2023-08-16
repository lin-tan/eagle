import yaml
from mining_utils import *

dtype_map_file = {
    'tf': '/Users/danning/Desktop/deepflaw/DeepFlaw-Code/doc_analysis/extract_constraint/tf/patterns/dtype_map.yml',
    'pytorch': '/Users/danning/Desktop/deepflaw/DeepFlaw-Code/doc_analysis/extract_constraint/pytorch/patterns/dtype_map.yml',
    'mxnet': '/Users/danning/Desktop/deepflaw/DeepFlaw-Code/doc_analysis/extract_constraint/mxnet/patterns/dtype_map.yml'
}

result = {}

stop_type = [   # don't replace with "SOME_DTYPE"
    'tensor',
    'tf.tensor',
    'tensors',
    'shape',
    'method',
    'function', 
    'dtype',
    'types',
    'tf.dtype',
    'number',
    'size',
    'path',
    'name',
    'names',
    'images',
    'image',
    'floating',
    'dimension',
    'dimensions',
    'deprecated',
    'long',
    'context',
]
for framework in dtype_map_file:
    dtypes = []
    structures = []
    content = read_yaml(dtype_map_file[framework])
    for cat in content:
        if cat=='structure':
            structures+=content[cat]
        else:
            dtypes+=content[cat]
    
    result[framework] = {}
    result[framework]['dtype'] = [x for x in dtypes if x not in stop_type]
    result[framework]['structure'] = [x for x in structures if x not in stop_type]

save_yaml('/Users/danning/Desktop/deepflaw/DeepFlaw-Code/doc_analysis/analysis/mining/dtype_ls.yaml', result)
    
