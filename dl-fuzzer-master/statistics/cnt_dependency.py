import sys
# sys.path.insert(0,'..')
# from extract_utils import *
import re
import os
import argparse
import yaml


def get_file_list(dir_addr):

    files = []
    for _,_, filenames in os.walk(dir_addr):
        files.extend(filenames)
        break

    if '.DS_Store' in files:
        files.remove('.DS_Store')

    return files

def read_yaml(path):
    with open(path) as yml_file:
        ret = yaml.load(yml_file, Loader=yaml.FullLoader)
    return ret

def read_file(path):
    with open(path) as file:
        ret = file.readlines()
    return ret


def get_bigrex(sep, boundary=True, escape=True):
    if boundary:
        s1 = r'\b%s\b'
        s2 = r'\b|\b'
    else:
        s1 = r'%s'
        s2 = r'|'


    if escape:
        bigrex = re.compile(s1 % s2.join(map(re.escape, sep)))
    else:
        bigrex = re.compile(s1 % s2.join(sep))

    return bigrex

class Constr:
    def __init__ (self, api, arg, cat, constr_value):
        # constraint
        self.api = api
        self.arg = arg
        self.cat = cat # dtype, structure, shape or validvalue
        self.constr_value = constr_value
        self.dependency = False


class dep_var:
    def __init__(self, var):
        # depenedency vairable
        self.var = var
        self.related_constr=[]
    
    def set_related_as_dependency(self):
        # set the constraint related to this variable to dependency-related constraints
        if len(self.related_constr)>1:
            for constr in self.related_constr:
                constr.dependency = True

    def set_related(self, constr):
        # set constr as related constr
        if constr in self.related_constr:
            return False
        self.related_constr.append(constr)
        return True

class API:
    def __init__(self, yaml, api_name):
        self.api_name = api_name
        self.yaml = yaml
        self.all_dep_var = []
        self.all_constr = []
        self.num_constr = 0
        self.group = {
            'prim_dtype': ['dtype'],
            'nonprim_dtype': ['tensor_t', 'structure'],
            'shape': ['shape', 'ndim'],
            'validvalue': ['enum', 'range']
        }
        self.related_cnt = 0

        self.init_depvar()
        self.init_constr()
        

    def init_depvar(self):
        for dep in self.yaml.get('dependency', []):
            self.all_dep_var.append(dep_var(dep))
        
    def init_constr(self):
        for arg in self.yaml['constraints']:
            for cat in self.group:
                tmp = []  # constr
                for subcat in self.group[cat]:
                    tmp += self.yaml['constraints'][arg].get(subcat, [])
                if tmp: # if tmp is not empty
                    self.all_constr.append(Constr(self.api_name, arg, cat, sorted(tmp)))
        self.num_constr = len(self.all_constr)

    def label_dep_related_constr(self):
        # whenever a constraint contains "&", it is a dependency-related
        # otherwise, if a variable in shape_var (self.all_dep_var) 
        # appears in two cosntraints, all related constr are considered dependency-related
        
        # label dependency related constr
        for dep in self.all_dep_var:
            if dep.var.startswith('&'):
                continue
            
            rex = get_bigrex([dep.var], boundary=True, escape=False)
        
            for constr in self.all_constr:
                if rex.search(str(constr.constr_value)):
                    dep.set_related(constr)
                    dep.set_related_as_dependency()

        # &XX
        for constr in self.all_constr:
            if '&' in str(constr.constr_value):
                constr.dependency=True
    
    def count_related(self):
        for constr in self.all_constr:
            if constr.dependency:
                print(self.api_name)
                self.related_cnt+=1
        

def count(file_list):
    # count number of dependency-related constraints in given list of APIs
    # file_list: list of absolute path

    unique_file_list = list(set(file_list))

    num_constr = 0
    num_related_contr = 0 
    num_API_dep = 0  # number of APIs with dependency constraints
    for file in unique_file_list:
        yaml_file = read_yaml(file)
        api_obj = API(yaml_file, yaml_file['title'])
        api_obj.label_dep_related_constr()
        api_obj.count_related()

        num_constr += api_obj.num_constr
        num_related_contr += api_obj.related_cnt
        if api_obj.related_cnt>0:
            num_API_dep+=1
            print(file)
        

    # print('{} files (APIs), {} unique ones, {} constraints, {} dependency-related; percentage {}'\
    #     .format(len(file_list),len(unique_file_list), num_constr, num_related_contr, num_related_contr/num_constr))

    print('{} files (APIs), {} unique ones, {} APIs has dependency constraints'\
    .format(len(file_list),len(unique_file_list), num_API_dep))

    return num_constr, num_related_contr
    

    
def main(framework, buggy_api_list): 

    constraint_src = {
        
        'tf': '../doc_analysis/subtree_mine/constr/tf/success/',
        'pytorch': '../doc_analysis/subtree_mine/constr/pt/success/',
        'mxnet': '../doc_analysis/subtree_mine/constr/mx/success/'
    }

    def _construct_filelist(framework):
        files = get_file_list(constraint_src[framework])
        return [constraint_src[framework]+f for f in files]


    if framework =='all':
        all_files = _construct_filelist(framework)
    
    else:
        all_files = []
        buggy_list = [x.replace('\n', '')+'.yaml' for x in read_file(buggy_api_list)]
        all_files = [constraint_src[framework]+f for f in buggy_list]
        for api_path in all_files:
            if not os.path.exists(api_path):
                print('cannot find file '+api_path)
                return

        # all_files = list_rm_duplicate(all_files)

    # elif framework=='all':
    #     for fw in constraint_src:
    #         all_files += _construct_filelist(fw)
        
    # print(all_files)
    
    num_constr, num_related = count(all_files)

    
if __name__ == "__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument('framework')
    parser.add_argument('buggy_api_list')


    args = parser.parse_args()
    framework = args.framework
    buggy_api_list = args.buggy_api_list
    main(framework, buggy_api_list)