import csv
import yaml
import re
import sys
sys.path.insert(0,'..')
from parse_utils import *


ecp_msg = read_file('./stat/other_exception')


with open('./stat/inconsistency.csv', 'w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(["arg", "API", "url"])
    
    for l in ecp_msg:
        p = re.search(r'\[(.*?)\] Inconsistency detected, arg (.*?) doesn\'t exist (.*)', l)
        if p!=None:
            writer.writerow([p.group(2), p.group(1), p.group(3)])


