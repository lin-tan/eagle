import csv
import yaml
import re

with open('./exception_record') as file:
    ecp_msg = file.readlines()


with open('./inconsistency.csv', 'w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(["API", "Cause", "Message"])
    
    for l in ecp_msg:
        p = re.match(r'(.*?):\s\[(.*?)\](.*)', l)
        if p!=None:
            writer.writerow([p.group(1), p.group(2), p.group(3)])
        else:
            print('fail to match line %s' % l)
            exit