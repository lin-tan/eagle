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


def main(workdir, exclude_abort):

    def _update_num_bugs(num_bugs, idx):
        added = False
        for itr in num_bugs:
            if idx<=int(itr)-1:
                num_bugs[itr] +=1
                added=True
                # return num_bugs
        if not added:
            print('Error occured')

        return num_bugs

    bug_type = ['Floating_Point_Exception', 'Segmentation_Fault']
    
    
    num_bugs = {
        '500': 0,
        '1000': 0,
        '1500': 0,
        '2000': 0
    }
    if not exclude_abort:
        # for tf and pytorch
        bug_type.append('Abort')
    sub_dir = [f.path for f in os.scandir(workdir) if f.is_dir()]
    for d in sub_dir:
        script_record = [x.split(',')[0] for x in read_file(os.path.join(d, 'script_record'))]
        # print(script_record)
        
        for bt in bug_type:
            record_path = os.path.join(d, bt+'_record')
            script_record_path = os.path.join(d, bt+'_script_record')
            if os.path.exists(record_path):
                trigger_py_file =  [x.replace('\n', '').replace('python ', '') for x in read_file(script_record_path)]
                first_py_file = trigger_py_file[0]
                # print(first_py_file)
                idx = script_record.index(first_py_file)
                num_bugs = _update_num_bugs(num_bugs, idx)
            
    print(num_bugs)
if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument('workdir')
    parser.add_argument('--exclude_abort', default=False, action='store_true')
    args = parser.parse_args()


# exp 19
# {'500': 71, '1000': 6, '1500': 6, '2000': 3}
# ➜  docter python check_saturate.py expr/pytorch/PT19_8758cca_baseline/workdir/expect_ok_no_constr
# {'500': 8, '1000': 1, '1500': 2, '2000': 0}
# ➜  docter python check_saturate.py expr/mxnet/MX19_8758cca_baseline/workdir/expect_ok_no_constr --exclude_abort
# {'500': 5, '1000': 2, '1500': 4, '2000': 0}

# MX19.2 found 0 bugs 

    
        
    main(args.workdir, args.exclude_abort)
