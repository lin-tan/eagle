import yaml
from extract_utils import *

class Pat:
    def __init__(self, filepath, savedir=None):

        self.filepath = filepath
        self.savedir = savedir
        self.filename = self.filepath.split('/')[-1]
        self.pat_dict = read_yaml(filepath)
        
        if self.pat_dict == None:
            self.pat_dict = {}

        if 'pat' in  self.pat_dict:
            for p in self.pat_dict['pat']:
                self.pat_dict['pat'][p]['cnt'] = 0

    def upcnt(self, p):
        
        try:
            if isinstance(p, list):
                for pp in p:
                    self.pat_dict['pat'][pp]['cnt']+=1
            else:
                self.pat_dict['pat'][p]['cnt']+=1
        except:
            pass
    
    def print_cnt(self, p=None):
        if p:
            print('{}\t{}', self.pat_dict['pat'][p]['cnt'], p)
        else:
            for pp in self.pat_dict['pat']:
                print('{}\t{}', self.pat_dict['pat'][pp]['cnt'], pp)

    def save_cnt(self):
        if self.savedir:
            with open(self.savedir+self.filename, 'w') as yaml_file:
                yaml.dump(self.pat_dict, yaml_file)