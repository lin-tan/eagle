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


def main(workdir):
    def get_time(fuzz_time_file):
        return float(fuzz_time_file[0].replace(' sec\n', ''))

    sub_dir = [f.path for f in os.scandir(workdir) if f.is_dir()]
    total_time = 0
    total_script = 0
    for d in sub_dir:
        if not os.path.exists(os.path.join(d, 'fuzz_time')):
            print('Cannot find file '+ str(os.path.join(d, 'fuzz_time')))
            continue

        if not os.path.exists(os.path.join(d, 'script_record')):
            print('Cannot find file '+str(os.path.join(d, 'script_record')))
            continue
        
        fuzz_time_file = read_file(os.path.join(d, 'fuzz_time'))
        time_used = get_time(fuzz_time_file)
        script_record = read_file(os.path.join(d, 'script_record'))
        total_script+=len(script_record)
        total_time += time_used

    print('Total script generated: '+ str(total_script))
    print('Total time(sec) used: '+ str(total_time))
    print('Average time(sec) to generate one script: '+str(total_time/total_script))


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument('workdir')
    args = parser.parse_args()
    
        
    main(args.workdir)

# 83.20 sec