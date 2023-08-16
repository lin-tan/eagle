import os
import sys
sys.path.insert(0,'../')
from util import *

frameworks = ['tf', 'pt', 'mx']
folder = ['./val_mining_data/', './val_result/', './val_rule/']
for f in folder:
    for fm in frameworks:
        path = os.path.join(f, fm)
        create_dir(path)