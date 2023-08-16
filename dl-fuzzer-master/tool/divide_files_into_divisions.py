"""
this script divides the files from the input folder into N folders
this is needed because using bash to divide lots of files is very slow
want to leverage multiprocessing to make it more efficient
"""
import argparse
import os
import shutil
from multiprocessing import Pool


def map_files_to_index(input_dir, out_prefix, num_folders):
    files = [os.path.join(input_dir, f) for f in os.listdir(input_dir) if os.path.isfile(os.path.join(input_dir, f))]
    mapping = []
    for i, f in enumerate(files):
        division_index = i % num_folders + 1
        output_folder = out_prefix + '_%d' % division_index
        output_path = os.path.join(input_dir, output_folder)
        mapping.append((f, output_path))
    return mapping


def copy_file_to_dir(fpath, dpath):
    shutil.copy(fpath, dpath)


def copy_files_to_div(mapping, ncpu):
    with Pool(processes=ncpu) as pool:
        pool.starmap(copy_file_to_dir, mapping)


def create_folders(input_dir, out_prefix, num_folders):
    for i in range(num_folders):
        idx = i + 1
        folder_name = '%s_%d' % (out_prefix, idx)
        folder_path = os.path.join(input_dir, folder_name)
        os.makedirs(folder_path)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('input_dir', type=str,
                        help='directory containing the files')
    parser.add_argument('--out_prefix', type=str, default='division',
                        help='prefix to the output directories')
    parser.add_argument('--num_folders', type=int, default=10,
                        help='number of output directories')
    parser.add_argument('--ncpu', type=int, default=4,
                        help='number of cpus to do the conversion')
    args = parser.parse_args()

    assert 0 < args.num_folders < 100
    assert 0 < args.ncpu <= os.cpu_count()

    if not os.path.exists(args.input_dir):
        raise Exception('Directory does not exist ({0}).'.format(args.input_dir))

    create_folders(os.path.abspath(args.input_dir), args.out_prefix, args.num_folders)

    files_to_divid_mapping = map_files_to_index(os.path.abspath(args.input_dir), args.out_prefix, args.num_folders)

    copy_files_to_div(files_to_divid_mapping, args.ncpu)


if __name__ == '__main__':
    main()
