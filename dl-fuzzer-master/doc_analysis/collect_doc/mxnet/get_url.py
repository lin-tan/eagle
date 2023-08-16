from bs4 import BeautifulSoup
import requests
import re
import yaml

# get urls and titles of APIs from https://www.tensorflow.org/versions/r2.1/api_docs/python
# tf python 2.1


def parse_html(url, class_=None, text=None):
    req = requests.get(url)
    soup = BeautifulSoup(req.text, 'lxml')
    if class_!=None:
        return soup.find_all(class_=class_)
    elif text != None:
        return soup.find_all(text)


url = 'https://mxnet.apache.org/versions/1.7/api/python/docs/api/'
init_offset = 'index.html'
content = parse_html(url+init_offset, class_ = 'toctree-l1 current')
offsets = re.findall(r'href=\"(.*?)\"', str(content[0].find_all('li')))

save = {}
save['deprecated'] = {}

func_list_pat = r'<p><strong>Functions</strong></p><table class="longtable docutils align-default">(.*?)</table>'
func_element_pat = r'<tr class="row-(odd|even)">(.*?)</tr>'
func_name_pat = r'<td>(.*?)</td>'
func_title_pat = r'title=\"(.*?)\"'
func_href_pat = r'href=\"(.*?)\"'

api_cnt = 0

for of in offsets:
    tmp_url = url+of
    save[tmp_url] = {}
    func_sect = parse_html(tmp_url, class_ = 'section')
    
    func_list = re.findall(func_list_pat,str(func_sect[0]).replace('\n', ''))
    if func_list==[]:
        print("{}: {} found".format(tmp_url, 0))
        continue
    func_elements = re.findall(func_element_pat, func_list[0])
    print("{}: {} found".format(tmp_url, len(func_elements)))
    # api_cnt += len(func_elements)

    for fe in func_elements:
        func_name, func_descp = re.findall(func_name_pat, fe[1])
        func_title = re.search(func_title_pat, func_name).group(1)
        func_href = re.search(func_href_pat, func_name).group(1)
        if 'deprecated' in func_descp.lower():
            save['deprecated'][func_title] = tmp_url+func_href
        else:
            save[tmp_url][func_title] = tmp_url+func_href
            api_cnt+=1

        


# 1.7: 3766 function API found
with open("./stat1.7/mxnet_1.7_fromweb.yaml", 'w') as yaml_file:
    yaml.dump(save, yaml_file)

print(str(api_cnt) + ' function API found ')