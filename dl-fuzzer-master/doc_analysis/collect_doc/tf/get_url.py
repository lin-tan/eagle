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

url = 'https://www.tensorflow.org'
offset = '/versions/r2.2/api_docs/python/tf/all_symbols'
content = parse_html(url+offset, class_ = 'devsite-article-body clearfix')


py_urls = {}
pat = r'<li><a href=\"(.*?)\"><code.*?>(.*?)<\/code><\/a><\/li>'
for i in content[0].find_all('li')[1:]:    # the first one is tf
    parsed = re.match(pat, str(i))
    title = parsed.group(2)
    href = parsed.group(1)
    py_urls[str(title)] = str(href)

    


# get unique urls

unique_url = {}


for t in py_urls: # for title t
    if unique_url.get(py_urls[t], None):
        unique_url[py_urls[t]]['aliases'].append(t)
    else:
        unique_url[py_urls[t]] = {}
        # unique_url[py_urls[t]]['aliases'] = []
        unique_url[py_urls[t]]['aliases'] = [t]



# r2.1: 4847 APIs collected, 2588 unique URL
# r2.2: 6229 APIs collected, 3923 unique URL
# r2.3: 6482 APIs collected, 4073 unique URL
# 2.3-2.1: tf.raw_ops (new module)
print('{} APIs collected, {} unique URL '.format(len(py_urls.keys()), len(unique_url.keys())))


with open("./stat2.2/tf2.2_py_fromweb.yaml", 'w') as yaml_file:
    yaml.dump(py_urls, yaml_file)

with open("./stat2.2/tf2.2_py_uniqueurl.yaml", 'w') as yaml_file:
    yaml.dump(unique_url, yaml_file)