
import sys
import pickle
import re
    
def read_file(path):
    with open(path) as file:
        ret = file.readlines()
    return ret
        

def read_list(path):
    ret = read_file(path)
    return [x.replace('\n', '') for x in ret]


def main(bash_path, arg):
    content = read_list(bash_path)
    content  = [x.split('/')[-1][:-2] for x in content]
    prefix = re.sub(r'(.*\/)[\w]+', r'\1', bash_path)
    #path_prefix = '/home/workdir/expect_ok_prev_ok/mxnet.ndarray.op.split.yaml_workdir/'
    for c in content:  
            data = pickle.load(open(prefix+c+'p', 'rb'))
            print(prefix+c+'p')
            if arg:
                argname = arg.replace('.shape', '')
                if argname not in data:
                    continue
                if arg.endswith('.shape'):
                    print(data[argname].shape)
                else:
                    print(data[argname])
            else:
                print(data)

            print()




if __name__ == "__main__":

    # USAGE:

    # If print all the arguments:
    # python print.py LINK_TO_BASH_SCRIPT
    # e.g.  python print.py /home/workdir/expect_ok_prev_ok/torch.cholesky_solve.yaml_workdir/Segmentation_Fault_script_record
    
    # If print only one argument:
    # python print.py  LINK_TO_BASH_SCRIPT  ARG_NAME
    # e.g.  python print.py /home/workdir/expect_ok_prev_ok/torch.cholesky_solve.yaml_workdir/Segmentation_Fault_script_record upper

    # if print the argument's shape
    # python print.py  LINK_TO_BASH_SCRIPT  ARG_NAME.shape
    # e.g.  python print.py /home/workdir/expect_ok_prev_ok/torch.cholesky_solve.yaml_workdir/Segmentation_Fault_script_record upper.shape

    bash_path = sys.argv[1]  # path to the bash script
    try: 
        arg = sys.argv[2]  # print only the arg
    except:
        arg = None

    
        
    main(bash_path, arg)