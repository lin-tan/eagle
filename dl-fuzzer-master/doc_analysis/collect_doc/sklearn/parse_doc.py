import re
import os
import sys
sys.path.insert(0,'..')
from parse_utils import *
from yaml_file_cls import yaml_file

class parser:
    def __init__(self, fname, content):
        self.data = yaml_file(title=fname, api_name=fname.split('.')[-1], url='', package='sklearn', version='0.24.2')
        self.content = content
        self.fname = fname
    
    def parse_sig(self):
        def process_sig(parsed_sig):
            ret = {}
            for key in parsed_sig:
                if key=='' or key.isspace() or key=='...':
                    continue
                else:
                    ret[key] = parsed_sig[key]
            return ret
        m = re.match('(.*?)\s=\s([\w_.]+)\((.*?)\)$', self.content[0])
        if m:
            assert(fname == m.group(1))
            assert(fname.split('.')[-1] == m.group(2))
            sig = m.group(3)
            parsed_sig = parse_input(sig)
            parsed_sig = process_sig(parsed_sig)
            if self.data.init_input(parsed_sig):
                return True
        
        raise GoToTheNextOne('' , self.fname, '[Sig] Fail to parse signature', save=True)
    
    def get_sect(self, sect):
        rule = r'\n\s*{}\n\s*---+\n(.*?)(\n\s*(\w+|See [aA]lso)\n\s*---+\n|$)'.format(sect)
        m = re.search(rule, ''.join(self.content), flags=re.DOTALL)
        if m:
            return m.group(1)
        raise GoToTheNextOne('' , self.fname, '[{}] Fail to parse {} section'.format(sect, sect), save=True)
        
    def descp_pre_process(self,descp):
        return re.sub(r'\.\.\s+(versionchanged|versionadded|deprecated)::.*?(\n\s+\n|$)', '\n \n', descp, flags=re.DOTALL)

    def descp_post_process(self,descp):
        return re.sub(r'\s*\n\s*', ' ', descp.lstrip())
    
    def update_descp(self, descp_dict):
        if not descp_dict:
            raise GoToTheNextOne('' , self.fname, '[Descp] Fail to parse descp section (empty return)', save=True)
        
        for arg in descp_dict:
            self.data.update_constraint(arg, descp_dict[arg], allow_inconsistent_when_kwargs=False, ignore_star=False)
        
        
    def parse_descp(self, raw_descp):
        ret = {}
        raw_descp = self.descp_pre_process(raw_descp)
#         print(raw_descp)
        for a in re.split(r'\n\s+\n', raw_descp):
            if not a:
                continue
            m = re.match(r'^\s*([\w_\*]+)\s*:(.*?)$', a, flags=re.DOTALL)
            if not m:
                return self.parse_descp2(raw_descp)
                
                
            varname = m.group(1)
            descp = self.descp_post_process(m.group(2))
            ret[varname] = descp
            
        return ret
        
    def parse_descp2(self, raw_descp):
        # match the descp by the args
        # cannot detect inconsistencies, but can solve the itmes inside param descp
        ret = {}
        # raw_descp = descp_pre_process(raw_descp)
        arg_list = list(self.data.data['constraints'].keys())
        non_space_seg = []
        for seg in re.split(r'(^|\n\s+\n)\s+({})\s+:(.*?)'.format(get_bigrex(arg_list, boundary=False, escape=True)), raw_descp, flags=re.DOTALL):
            if seg and not seg.isspace():
                non_space_seg.append(seg)
        try:
            assert(len(non_space_seg) == 2*len(arg_list))
        except:
            raise GoToTheNextOne('' , self.fname, '[SPEC_Descp] Fail to parse descp section', save=True)
            
#         print(non_space_seg)
        for i in range(0, len(non_space_seg), 2):
            varname = non_space_seg[i]
            descp = self.descp_post_process(non_space_seg[i+1])
            ret[varname] = descp
            
        return ret
        
    
        
    def parse(self, folder):
        self.parse_sig()
        param_str = self.get_sect('Parameters')
        descp_dict = self.parse_descp(param_str)
        self.update_descp(descp_dict)
        self.data.save_file(folder, filename = self.fname)
        

if __name__ == "__main__":
    src_path = './raw/'
    dst_path = './parsed/'

    del_file(dst_path)
    for fname in get_file_list(src_path):
        try:
            p = parser(fname, content = read_file(os.path.join(src_path, fname)))
            p.parse(dst_path)
        except GoToTheNextOne as gttno:
            if gttno.save:
                print(fname+': '+gttno.msg)