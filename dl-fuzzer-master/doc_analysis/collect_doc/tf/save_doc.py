import sys
sys.path.insert(0,'..')

import os
import yaml
import re
import os.path
from os import path
from parse_utils import *






uniqueurl = read_yaml('./stat2.2/tf2.2_py_uniqueurl.yaml')

title_list = []
lower_title_list = []
url_list = []

uniqueurl_filename = uniqueurl   # file with  path of file saved 

save_folder = "/Users/danning/Desktop/deepflaw/web_source/tf_2.2_source/"
del_file(save_folder, etd='*.html')

for url in uniqueurl:
    
    
    
    try: 
       # url = pu.replace('https://www.tensorflow.org/', 'https://www.tensorflow.org/versions/r2.1/')
    
        title = str(parse_html(url, class_='devsite-page-title')[0].contents[0])


        web_content = requests.get(url)

        save_path = save_folder+title
        # handle duplicate name
        while os.path.exists(save_path+'.html') :
            save_path += '2'
            title+='2'

        save_file(save_path+'.html', web_content.content)

        title = title+'.html'
        uniqueurl_filename[url]['filename'] = title

        url_list.append(str(url))
        title_list.append(str(title))
        lower_title_list.append(str(title.lower()))
            
    except:
        
        print(url)

        


# save title/url list
save_yaml("./stat2.2/title.yaml", title_list)

save_yaml("./stat2.2/url.yaml", url_list)

save_yaml("./stat2.2/tf2.2_py_uniqueurl_filename.yaml", uniqueurl_filename)

#     # read it back in
#     with open("./temp.html") as f:
#         soup = BeautifulSoup(f.read())
