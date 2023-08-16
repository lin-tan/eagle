import os
import argparse
import csv
def write_csv(path, lines):
    with open(path, 'w', newline='') as file:
        writer = csv.writer(file)
        for l in lines:
            writer.writerow(l)
            
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

def to_csv(api_data):
    content = []
    content.append(['API', 'BugType', 'FirstTrigger'])
    for api in api_data:
        for bt in api_data[api]:
            content.append([api, bt, api_data[api][bt]])
    return content
def main(workdir, save_path):

    bug_type = ['Floating_Point_Exception', 'Segmentation_Fault', 'Abort', 'Bus_Error']
    api_data = {}
    sub_dir = [f.path for f in os.scandir(workdir) if f.is_dir()]

    for d in sub_dir:
        api = d.split('/')[-1].replace('.yaml_workdir', '')
        if os.path.exists(os.path.join(d, 'script_record')):
            script_record = [x.split(',')[0] for x in read_file(os.path.join(d, 'script_record'))]
        # print(script_record)
        
            for bt in bug_type:
                record_path = os.path.join(d, bt+'_record')
                script_record_path = os.path.join(d, bt+'_script_record')
                if os.path.exists(record_path):
                    if api not in api_data:
                        api_data[api] = {}
                    # if bt not in api_data[api]:
                    #     api_data[api][bt] = num_bugs
                    trigger_py_file =  [x.replace('\n', '').replace('python ', '') for x in read_file(script_record_path)]
                    first_py_file = trigger_py_file[0]
                    # print(first_py_file)
                    idx = script_record.index(first_py_file)
                    api_data[api][bt] =  idx # _update_num_bugs(api_data[api][bt], idx)
        else:
            print('Cannot find script_record for API %s'%api)
    write_csv(save_path, to_csv(api_data))

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument('workdir')
    parser.add_argument('save_path')
    args = parser.parse_args()

        
    main(args.workdir,  args.save_path)


