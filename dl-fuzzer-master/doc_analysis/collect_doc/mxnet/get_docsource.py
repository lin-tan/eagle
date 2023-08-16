import sys
sys.path.insert(0,'..')

import os
import yaml
import re
import os.path
from os import path
from parse_utils import *



save_src_folder = '/Users/danning/Desktop/deepflaw/web_source/mx1.6_source/'
save_src = {}

del_file(save_src_folder, etd='*.html')

url_info = read_yaml('./stat1.6/mxnet_1.6_fromweb_class.yaml')

for url in url_info:
    if url == 'deprecated':
        continue
    if url_info[url]:
        # not empty
        title = parse_html(url, class_='section')[0].get('id')
        web_content = requests.get(url)
        save_path = save_src_folder+title+'.html'

        while os.path.exists(save_path) :
            save_path += '2'
            title+='2'

        save_file(save_path, web_content.content)

        save_src[url] = title+'.html'

save_yaml('./stat1.6/save_src_class.yaml', save_src)