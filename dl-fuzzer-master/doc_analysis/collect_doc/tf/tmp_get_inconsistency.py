import csv
import yaml
import re

with open('./stat/other_exception') as file:
    ecp_msg = file.readlines()


with open('./stat/inconsistency.csv', 'w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(["url", "arg"])
    
    for l in ecp_msg:
        p = re.search(r'arg (.*?) doesn\'t exist: (.*)', l)
        if p!=None:
            writer.writerow([p.group(2), p.group(1)])