import sys
sys.path.insert(0,'../..')
from extract_utils import *
import traceback
import re


def map_default(data, arg):
    
    if 'default' not in data['constraints'][arg]:
        return {'dtype': None, 'ndim': None}

    default_val = data['constraints'][arg]['default']
    # check bool
    bool_val = ['false', 'true']
    if str(default_val).lower() in bool_val:
        return {'dtype':'bool', 'ndim': 0}
        
    
    if str(default_val) in  ['None', '_Null']:
        return {'dtype':None, 'ndim': None}
    else:
        try:
            tmp = int(default_val)
            return {'dtype':'int', 'ndim': 0}
        except:
            pass
        
        try:
            tmp = float(default_val)
            return {'dtype':'float', 'ndim': 0}
        except:
            pass

        if len(str(default_val))>0 and str(default_val)[0] in ['(', '[']:
            ndim = len(re.findall(r'[\[\(]', str(default_val).split(',')[0]))
            return {'dtype':None, 'ndim': ndim}

        elif re.match(r'.*\..*', str(default_val))!=None or str(default_val).startswith('<'):
            return {'dtype':None, 'ndim': None}
        else:
            return {'dtype':'string', 'ndim': None}
            

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

        if not isinstance(val, list): # make it a list
            val = [val]
        # overwrite or not, append the val to the label
        final = list_rm_duplicate(val, self.info['constraints'][arg].get(label, []), sort=True) 
        if final:
            self.changed=True   
        self.info['constraints'][arg][label] = final 

    def check_dtype(self, dt_l, map = ['dtype_map']):
        # dt_l is a list of dtype
        # check if they are in the list and map them to the standard name
        # e.g. string -> tf.string,  positive -> x (not a type)
        ret = []
        for dt in dt_l:
            if dt[-1] == '.':
                tmp = dt[:-1]
            else:
                tmp = dt
            for m in map:
                if tmp.lower() in self.dt_map[m]:
                    ret.append(self.dt_map[m][tmp])
        return ret

    def check_dtype_all_map(self, dt_l, return1list=False):
        # return1list=True: return in one list, False: return in dict
        ret_dict = {}
        ret_list = []
        for map in self.dt_map:
            tmp  = self.check_dtype(dt_l, [map])
            ret_dict[map] = tmp
            ret_list+= tmp

        if return1list:
            return ret_list
        return ret_dict

    def map(self, word):
        tmp = self.check_dtype_all_map([word], return1list=False)
        ret = {}
        ret['dtype'] = tmp['dtype_map'] + tmp['plural_map']
        ret['tensor_t'] = tmp['tensor_t_map']
        ret['structure'] = tmp['structure']
        return ret

    def update_constr(self, arg, constr_dict):
        for k in constr_dict:
            if constr_dict[k]:
                self.set_c(arg, k, constr_dict[k])

    def extract(self, label, keyword):
        ret = []
        for arg in self.info['constraints']:

            src = [self.info['constraints'][arg]['descp']] + self.info['constraints'][arg].get('doc_dtype', [])
            for s in src:
                for word in keyword:
                    
                    if re.search(r'\b{}\b'.format(word.lower()), s.lower()):
                        constr_map = self.map(word.lower())
                        self.update_constr(arg, constr_map)

    def extract_default(self):
        for arg in self.info['constraints']:
            constr = map_default(self.info, arg)
            if constr['dtype']:
                constr_map = self.map(constr['dtype'])
                self.update_constr(arg, constr_map)
            if constr['ndim']!=None:
                self.set_c(arg, 'ndim', str(constr['ndim']))


    def post_process(self):

        # remove deprecated variables from input list
        # for da in self.info['inputs'].get('deprecated', []):
        #     _remove_deprecated(da)

        for arg in self.info['constraints']:
            # if 'deprecated' in self.info['constraints'][arg].get('dtype', []):
            #     _remove_deprecated(arg)
            
            if 'scalar' in self.info['constraints'][arg].get('dtype', []):
                if 'scalar' not in str(self.info['constraints'][arg].get('structure', [])):
                    self.info['constraints'][arg]['dtype'].remove('scalar')
                    # self.set_c(arg, 'ndim', str(0))       # don't use assumptions
                    self.set_c(arg, 'dtype', 'numeric')     # convert to numeric for comparison
                

    def run(self):
        # self.extract_default()
        self.extract('dtype', self.map_word['dtype'])
        self.extract('structure', self.map_word['structure'])
        self.extract('tensor_t', self.map_word['tensor_t'])
        self.post_process()
        

def run(source_dir, yml_files, save_to, map_word, dt_map):


    save_cnt = 0
    for i, f in enumerate(yml_files):
        #print(f)
        # print('{}/{}    {}'.format(i+1, len(yml_files), f))
        info = read_yaml(source_dir+f) 
        parser = Parser(info, map_word, dt_map)
        
        try:
            parser.run()

        except:
            print(f)
            traceback.print_exc()
            break

        
        #save info here
        if check_changed(parser.info):
            save_addr = save_to+'changed/'
            save_cnt+=1
        else:
            save_addr = save_to+'unchanged/'

        # if not test: 
        save_yaml(save_addr+f, parser.info)

    return save_cnt



def main():
    def _remove_v1(file_list):
        # this is only for tf, to remove all apis from tf.compat.v1
        ret = []
        for f in file_list:
            if 'tf.compat.v1' in f:
                continue
            ret.append(f)

        return ret
            

    all_lib = {
                'tf': {
                    'src': '../../../collect_doc/tf/tf21_all_src/',
                    'dt_map':'../../tf/patterns/dtype_map.yml'},
                'pytorch': {
                    'src': '../../../collect_doc/pytorch/pt15_all_src/',
                    'dt_map': '../../pytorch/patterns/dtype_map.yml'
                },
                'mxnet': {
                    'src': '../../../collect_doc/mxnet/mx16_all_src/',
                    'dt_map': '../../mxnet/patterns/dtype_map.yml'
                }
            }
    
    
    for lib in all_lib:
        map_word = read_yaml('./dtype_ls.yaml')[lib]
        dt_map = read_yaml(all_lib[lib]['dt_map'])
        source_dir = all_lib[lib]['src']
        files = get_file_list(source_dir)
        
        save_to = './'+lib+'/'


    # if not test:
        del_file(save_to)  # delete recursively all files existing in the save source_dir

        yml_files = get_file_list(source_dir)
        # if lib=='tf':
        #     yml_files = _remove_v1(yml_files)
        
        save_cnt = run(source_dir, yml_files, save_to, map_word, dt_map)

        print('{}: {}/{} Changed!'.format(lib, save_cnt, len(yml_files)))



if __name__ == "__main__":

    main()
        

# tf: 930/1008 Changed!
# pytorch: 476/529 Changed!
# mxnet: 1009/1021 Changed!

   