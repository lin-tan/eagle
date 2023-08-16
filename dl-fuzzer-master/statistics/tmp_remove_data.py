import os
import argparse

# this script removes all the input(.p)/python script(.py)/exception message(.e) files that doesn't trigger crash
# and record the file names in corresponding files so that later can calculate exception rate

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

def save_file(path, content):
    with open(path, 'w') as f:
        if isinstance(content, str):
            f.write(content)
        elif isinstance(content, list):
            for c in content:
                f.write(c+'\n')
        else:
            f.write(content)

def main(workdir):
    bug_type = ['Kill', 'Abort', 'Floating_Point_Exception', 'Segmentation_Fault', 'timeout', 'Nan']

    sub_dir = [f.path for f in os.scandir(workdir) if f.is_dir()]
    for d in sub_dir:
        p_file_to_keep = []
        py_file_to_keep = []
        for bt in bug_type:
            record_path = os.path.join(d, bt+'_record')
            script_record_path = os.path.join(d, bt+'_script_record')
            if os.path.exists(record_path):
                p_file_to_keep += [x.split('/')[-1].replace('\n', '') for x in read_file(record_path)]
                py_file_to_keep += [x.split('/')[-1].replace('\n', '') for x in read_file(script_record_path)]

        for py in py_file_to_keep:
            if '_' in py:
                p_file_to_keep.append(py.replace('.py', '').split('_')[1]+'.p')
        
        target_file_list = get_file_list(d)
        py_file = [f for f in target_file_list if f.endswith('.py')]
        p_file = [f for f in target_file_list if f.endswith('.p')]
        e_file = [f for f in target_file_list if f.endswith('.e')]
        emt_file = [f for f in target_file_list if f.endswith('.emt')]

        save_file(os.path.join(d, 'script_record'), py_file)
        save_file(os.path.join(d, 'p_file_record'), p_file)
        save_file(os.path.join(d, 'exception_record'), e_file)
        save_file(os.path.join(d, 'emt_record'), emt_file)
        

        for f in target_file_list:
            if f.endswith('.py') and f not in py_file_to_keep:
                os.remove(os.path.join(d, f))
            elif f.endswith('.p') and f not in p_file_to_keep:
                os.remove(os.path.join(d, f))
            elif f.endswith('.e') or f.endswith('emt'):
                os.remove(os.path.join(d, f))

            
        
        




if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument('workdir')
    args = parser.parse_args()


    
        
    main(args.workdir)
