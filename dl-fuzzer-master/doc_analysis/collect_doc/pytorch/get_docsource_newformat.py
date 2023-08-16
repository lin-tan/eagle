import sys
sys.path.insert(0,'..')

import os
import yaml
import re
import os.path
from os import path
from parse_utils import *


save_src_folder = '/Users/danning/Desktop/deepflaw/web_source/pt_1.4_source/'

new_format_html = read_yaml('./stat1.4/new_format.yaml')    # ['torch.html', 'nn.html']
save_src = read_yaml('./stat1.4/save_src.yaml')
save_src_path = './stat1.4/save_src_new_format.yaml'

prefix = 'https://pytorch.org/docs/1.4.0/'

for html_file in new_format_html:
    file_path = save_src_folder+html_file
    soup = read_soup(file_path)
    api_element = soup.find_all('tr')
    for ae in api_element:
        offset = ae('a')[0].get('href')
        link = prefix + offset

        web_content = requests.get(link)
        filename = offset.split('#')[-1]
        save_path = save_src_folder + filename
        save_path = filename_wo_duplicate(save_path, '', msg = True)
        save_file(save_path, web_content.content)

        save_src[link] = {}
        save_src[link]['filename'] = save_path.split('/')[-1]

save_yaml(save_src_path, save_src)



