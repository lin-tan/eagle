import sys
sys.path.insert(0,'..')

import os
import yaml
import re
import os.path
from os import path
from parse_utils import *

# version = '1.7'
save_src_folder = '/Users/danning/Desktop/deepflaw/web_source/pt_1.4_source/'
url = 'https://pytorch.org/docs/1.4.0/'
save_src_path = './stat1.4/save_src.yaml'
offset_list = []
save_src = {}

del_file(save_src_folder, etd='*.html')

soup = parse_html(url, class_='toctree-wrapper compound')
for c in soup[2].find_all(class_='toctree-l1'):
    offset_list.append(c('a')[0].get('href'))

for offset in offset_list:
    web_content = requests.get(url+offset)
    filename = offset.replace('/','_')
    save_path = save_src_folder+filename
    save_file(save_path, web_content.content)
    
    save_src[url+offset] = {}
    save_src[url+offset]['filename'] = filename

save_yaml(save_src_path, save_src)