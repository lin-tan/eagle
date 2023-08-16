import sys
sys.path.insert(0,'..')

from bs4 import BeautifulSoup
import yaml
import re
from parse_utils import *
from yaml_file_cls import yaml_file
import pprint
import traceback
import time


def main():
    web_file_folder = '/Users/danning/Desktop/deepflaw/web_source/doc2.1source/'
    save_folder = './doc2.1_parsed/' 

    uniqueurl_filename = read_yaml('./stat/tf2.1_py_uniqueurl_filename.yaml')
    candidate = list(uniqueurl_filename.keys())
    print(len(candidate))

    word_cnt = 0  # number of word in all tensorflow documents (2588)
    doc_cnt = 0
    api_cnt = 0


    for url in candidate:

        filename = uniqueurl_filename[url]['filename']
        if filename.startswith('Module:'):
            continue

        doc_cnt+=1
        api_cnt+=len(uniqueurl_filename[url]['aliases'])
        
        # soup = read_soup(web_file_folder+filename)
        
        # title = str(soup.find_all(class_ = 'devsite-page-title')[0].contents[0])
        # body = soup.find_all(class_='devsite-article-body')[0]
        
        # word_cnt += cnt_num_word(body.get_text())+cnt_num_word(title)

    # 4584 API, 2334 documents and 854900 words 
    print('{} API, {} documents and {} words'.format(api_cnt,doc_cnt, word_cnt))

main()