from shutil import copyfile
import sys
sys.path.insert(0,'..')
from extract_utils import *
import random

path = {
    'tf': {
        'src': '../tf/constraint_4/changed/',
        'dst': './tf21/'
    },
    'pt': {
        'src': '../pytorch/constraint_1/changed/',
        'dst': './pt15/'
    },
    'mx': {
        'src': '..//mxnet/constraint_2/changed/',
        'dst': './mx16/'
    }
        
}

ratio = 0.1     # only copy 10% randomly from each src to dst

for lib in path:
    file_list = get_file_list(path[lib]['src'])
    file_sample = random.choices(file_list, k=int(ratio*len(file_list)))
    print('sampled %s file from %s' % (len(file_sample), lib))
    del_file(path[lib]['dst'])
    for f in file_sample:
        copyfile(path[lib]['src']+f, path[lib]['dst']+f)

# sampled 91 file from tf
# sampled 40 file from pt
# sampled 95 file from mx
    
