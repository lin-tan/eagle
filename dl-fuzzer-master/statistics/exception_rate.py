import os
import argparse
import re

def get_file_list(dir_addr):

    files = []
    for _,_, filenames in os.walk(dir_addr):
        files.extend(filenames)
        break

    if '.DS_Store' in files:
        files.remove('.DS_Store')

    return files

def num_file(file_list, ext):
    # ext = .py
    target = [f for f in file_list if str(f).endswith(ext)]
    return len(target)


def read_file(path):
    with open(path) as file:
        ret = file.readlines()
    return ret

def get_first_n_input(file, n):
    pat=r'(.*?),\s(\d+)'
    ret = []
    for r in file:
        if int(re.match(pat, r.replace('\n', '')).group(2))<=n:
            ret.append(r)
    return ret


def count_e_file(workdir):
    num_py_total = 0
    num_e_total = 0
    sub_dir = [f.path for f in os.scandir(workdir) if f.is_dir()]
    for d in sub_dir:
        file_list = get_file_list(d)
        num_py_total += num_file(file_list, '.py')
        if num_file(file_list, '.py') ==0:
            print('No script file in '+str(d))
        num_e_total += num_file(file_list, '.e')

    exception_rate = num_e_total/num_py_total
    print(exception_rate)

def read_exception_record(workdir, limit=1000):
    num_py_total = 0
    num_e_total = 0
    exception_rate_sum = 0
    count=0
    sub_dir = [f.path for f in os.scandir(workdir) if f.is_dir()]
    for d in sub_dir:
        if os.path.exists(os.path.join(d, 'exception_record')):
            exception_record = read_file(os.path.join(d, 'exception_record'))
        else:
            print('Cannot find file '+str(os.path.join(d, 'exception_record')))
            exception_record = []
        if os.path.exists(os.path.join(d, 'script_record')):
            script_record = read_file(os.path.join(d, 'script_record'))
        else:
            print('Cannot find file '+str(os.path.join(d, 'script_record')))
            script_record=[]

        # only consider the first 1000 input 
        exception_record = get_first_n_input(exception_record, limit)
        script_record = get_first_n_input(script_record, limit)
        # print(script_record)
        #num_e = len([x for x in exception_record if '.emt' not in x])
        num_e = len(exception_record)
        num_py = len(script_record)
        if num_py!=0:
            exception_rate_sum += num_e/num_py
            # count+=1
        num_py_total+=num_py
        num_e_total+=num_e
        count+=1

    avg_exception_rate = exception_rate_sum/count
    accum_exception_rate = num_e_total/num_py_total
    print('average exception rate: '+str(avg_exception_rate))
    print('accumulative exception rate: '+str(accum_exception_rate))


def read_e_file_record(workdir):
    num_py_total = 0
    num_e_total = 0
    sub_dir = [f.path for f in os.scandir(workdir) if f.is_dir()]
    for d in sub_dir:
        if os.path.exists(os.path.join(d, 'e_file_record')):
            exception_record = read_file(os.path.join(d, 'e_file_record'))
        else:
            print('Cannot find file '+str(os.path.join(d, 'e_file_record')))
            exception_record = []
        if os.path.exists(os.path.join(d, 'script_record')):
            script_record = read_file(os.path.join(d, 'script_record'))
        else:
            print('Cannot find file '+str(os.path.join(d, 'script_record')))
            script_record=[]
        num_py_total+=len(script_record)
        num_e_total+=len(exception_record)
    exception_rate = num_e_total/num_py_total
    print(exception_rate)

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument('workdir')
    args = parser.parse_args()


    
        
    read_exception_record(args.workdir)