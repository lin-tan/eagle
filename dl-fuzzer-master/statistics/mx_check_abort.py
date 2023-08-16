import os
import argparse

def get_file_list(dir_addr):

    files = []
    for _,_, filenames in os.walk(dir_addr):
        files.extend(filenames)
        break

    if '.DS_Store' in files:
        files.remove('.DS_Store')

    return files

def read_file(path):
    with open(path) as file:
        ret = file.readlines()
    return ret

def pprint_list(l):
    for i in l:
        print(i)

def main(out_dir):
    crash_API = []
    FP_API = []
    file_list = get_file_list(out_dir)
    for f in file_list:
        content = read_file(os.path.join(out_dir, f))
        content_str = ' '.join([s.replace('\n', '') for s in content])
        if 'Segmentation fault: 11' in content_str:
            crash_API.append(f)
        elif 'bad_alloc' in content_str or 'deadlock' in content_str or 'double free' in content_str \
            or 'realloc' in content_str or 'double free' in content_str:
            crash_API.append(f)
        elif '==Test Start== ==Test Start==' in content_str or content_str.endswith('==Test Start=='):
            FP_API.append(f)

    
    print('Crash API')
    pprint_list(crash_API)
    print('False Positive (Potential Crash):')
    pprint_list(FP_API)



    
if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument('out_dir')
    args = parser.parse_args()


    
        
    main(args.out_dir)