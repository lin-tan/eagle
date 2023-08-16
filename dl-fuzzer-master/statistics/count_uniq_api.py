import argparse

def read_file(path):
    with open(path) as file:
        ret = file.readlines()
    return ret


def main(fpath):
    api_list = read_file(fpath)
    api_list = [x.replace('\n', '') for x in api_list]
    unique_api = list(set(api_list))
    print('Total: {}, Unique: {}'.format(len(api_list), len(unique_api)))



if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument('fpath')
    args = parser.parse_args()

    main(args.fpath)