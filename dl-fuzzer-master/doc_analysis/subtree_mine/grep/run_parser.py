import sys
sys.path.insert(0,'../')
from util import *
import traceback
import os
import re



def check_changed(data):
    target=['dtype', 'ndim', 'shape', 'enum', 'range', 'structure', 'tensor_t']
    for arg in data['constraints']:
        for cat in target:
            constr = data['constraints'][arg].get(cat, [])
            if isinstance(constr, list):
                if len(constr)>0:
                    return True
            else:
                if constr:
                    return True
    return False
            

def list_rm_duplicate(l1, l2=None, sort = False):
    # append several list together without duplicate
    if l2:
        tmp = l1+l2
    else:
        tmp = l1
    ret = list(set(tmp))
    if sort:
        return sorted(ret)
    else:
        return ret


class Parser:
    def __init__(self, info, map_word, dt_map):
        self.info = info
        self.map_word = map_word
        self.dt_map = dt_map
        self.changed = False

    def set_c(self, arg, label, val):

        
        if label not in ['tensor_t', 'dtype', 'structure', 'ndim', 'shape', 'range']:
            print('unknown label %s'%label)
            return

        # val = str(val)

        # if not isinstance(val, list): # make it a list
        #     val = [val]
        # overwrite or not, append the val to the label
        final = list_rm_duplicate([val], self.info['constraints'][arg].get(label, []), sort=True) 
        assert final
        if final:
            self.changed=True   
            self.info['constraints'][arg][label] = final 

    # def check_dtype(self, dt_l, map = ['dtype_map']):
    #     # dt_l is a list of dtype
    #     # check if they are in the list and map them to the standard name
    #     # e.g. string -> tf.string,  positive -> x (not a type)
    #     ret = []
    #     for dt in dt_l:
    #         if dt[-1] == '.':
    #             tmp = dt[:-1]
    #         else:
    #             tmp = dt
    #         for m in map:
    #             if tmp.lower() in self.dt_map[m]:
    #                 ret.append(self.dt_map[m][tmp])
    #     return ret

    # def check_dtype_all_map(self, dt_l, return1list=False):
    #     # return1list=True: return in one list, False: return in dict
    #     ret_dict = {}
    #     ret_list = []
    #     for map in self.dt_map:
    #         tmp  = self.check_dtype(dt_l, [map])
    #         ret_dict[map] = tmp
    #         ret_list+= tmp

    #     if return1list:
    #         return ret_list
    #     return ret_dict

    def map(self, word):
        tmp = self.check_dtype_all_map([word], return1list=False)
        ret = {}
        ret['dtype'] = tmp['dtype_map']
        ret['tensor_t'] = tmp['tensor_t_map']
        ret['structure'] = tmp['structure']
        return ret

    # def update_constr(self, arg, label, value):
    #     self.set_c(arg, label,value)
    #     # for k in constr_dict:
    #     #     if constr_dict[k]:
    #     #         self.set_c(arg, k, constr_dict[k])

    def extract(self, label, keyword):
        ret = []
        for arg in self.info['constraints']:

            src = [self.info['constraints'][arg]['descp']] + self.info['constraints'][arg].get('doc_dtype', [])
            for s in src:
                for word in keyword:
                    
                    if re.search(r'\b{}\b'.format(word.lower()), s.lower()):
                        # constr_map = self.map(word.lower())
                        assert word in self.dt_map[label]
                        self.set_c(arg, label, self.dt_map[label][word])
                        # self.update_constr(arg, label, self.dt_map[label][word])

                

    def run(self):
        # self.extract_default()
        self.extract('dtype', self.map_word['dtype'])
        self.extract('structure', self.map_word['structure'])
        self.extract('tensor_t', self.map_word['tensor_t'])
        # self.post_process()
        

def run(source_dir, yml_files, save_to, map_word, dt_map):


    save_cnt = 0
    for i, f in enumerate(yml_files):
        info = read_yaml(source_dir+f) 
        parser = Parser(info, map_word, dt_map)
        
        try:
            parser.run()

        except:
            print(f)
            traceback.print_exc()
            break

        
        #save info here
        # if check_changed(parser.info):
        if parser.changed:
            save_addr = save_to+'success/'
            save_cnt+=1
        else:
            save_addr = save_to+'fail/'

        # if not test: 
        save_yaml(os.path.join(save_addr, f), parser.info)

    return save_cnt



def main():


    all_lib = {
                'tf': {
                    'src': '../../collect_doc/tf/tf21_all_src/',
                    'dt_map':'../config/tf_dtype_map.yaml'},
                'pt': {
                    'src': '../../collect_doc/pytorch/pt15_all_src/',
                    'dt_map': '../config/pt_dtype_map.yaml'
                },
                'mx': {
                    'src': '../../collect_doc/mxnet/mx16_all_src/',
                    'dt_map': '../config/mx_dtype_map.yaml'
                }
            }
    lib_name_map = {'tf':'tensorflow', 'pt':'torch', 'mx': 'mxnet'}
    
    all_map_word = read_yaml('../config/dtype_ls.yaml')
    for lib in all_lib:
    # for lib in ['tf']:
        map_word = all_map_word[lib_name_map[lib]]
        dt_map = read_yaml(all_lib[lib]['dt_map'])
        source_dir = all_lib[lib]['src']

        save_to = './'+lib+'/'

        del_file(save_to)  # delete recursively all files existing in the save source_dir

        yml_files = get_file_list(source_dir)
        # if lib=='tf':
        #     yml_files = _remove_v1(yml_files)
        
        save_cnt = run(source_dir, yml_files, save_to, map_word, dt_map)

        print('{}: {}/{} Changed!'.format(lib, save_cnt, len(yml_files)))



if __name__ == "__main__":

    main()
        

# tf: 928/1008 Changed!
# pt: 468/529 Changed!
# mx: 1009/1021 Changed!


   