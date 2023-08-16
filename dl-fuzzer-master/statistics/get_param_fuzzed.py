# get the parameters being fuzzed/generated
# test fuzz optional with probability 

from utils import *
import glob
import pickle

def main(workdir, limit):
    input_files = glob.glob('*.p')
    result = {}
    num_input = min(len(input_files), limit)
    for i in range(0, num_input):
        data = pickle.load(open(input_files[i], 'rb'))
        print(data.keys())
        for param in data.keys():
            if param in result:
                result[param]+=1
            else:
                result[param] = 1
    print(str(num_input)+' input files')
    print(result)


if __name__== '__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--workdir', type=check_dir_exist, required=True, help='Work directory that stores fuzzing output. E.g., ../workdir/expect_ok_no_constr_no_adapt/....yaml_workdir')
    parser.add_argument('--limit', required=False, default=1000, help='Optional: how many to print, default all (1000)')
    args = parser.parse_args()
    workdir = args.workdir
    limit = int(args.limit)

    os.chdir(workdir)
    main(workdir, limit)