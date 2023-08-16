import yaml
from parse_utils import *
import os.path
from os import path

class yaml_file:
    def __init__(self, title, api_name, url, aliases=[], package = 'tensorflow', version = '2.1.0'):
        self.title = str(title)
        self.api_name = str(api_name)
        self.url = str(url)
        self.package = package
        self.version = version
        self.aliases = aliases
        self.deprecated_list = []
        self.data = self.init_data()
        
        
    def init_data(self):
        
        yaml_data = {}
        yaml_data['package']= self.package
        yaml_data['version']= self.version
        yaml_data['title'] = self.title
        yaml_data['target'] = self.api_name
        yaml_data['link'] = self.url
        yaml_data['constraints'] = {}

        if len(self.aliases)>1:
            self.aliases = [i for i in self.aliases if i.lower()!=self.title.lower()]
            yaml_data['aliases'] = self.aliases

        yaml_data['inputs'] = {'required':[], 'optional':[]}

        return yaml_data
    
    def init_input(self, parsed_input, deprecated_list = [], keyword_only =[], sig_dtype={}):
        self.deprecated_list = deprecated_list
        ret = False
        for a in parsed_input:
            if not (a=='' or a.isspace()):
                if parsed_input[a]!=None:  # with default value. default value can be empty string or 0
                    self.data['inputs']['optional'].append(a)
                    self.data['constraints'][a]={'descp':'', 'default':parsed_input[a]}
                else:
                    self.data['inputs']['required'].append(a)
                    self.data['constraints'][a]={'descp':''}
                ret = True

        # print('parsed input: '+ str(parsed_input))

        for arg in sig_dtype:
            if arg not in self.data['constraints']:
                raise GoToTheNextOne(self.url , self.title, "[Inconsistent] Arg %s from sig_dtype doesn't exist" % arg, save=True)
            
            self.data['constraints'][arg]['sig_dtype'] = sig_dtype[arg] 

        if keyword_only:
            self.data['inputs']['keyword_only']=keyword_only

        if deprecated_list:
            self.data['inputs']['deprecated'] = []
            for da in deprecated_list:
                self.data['inputs']['deprecated'].append(da)


        return ret
        # save_yaml('./tmp', self.data)

    def is_input(self, varname, allow_inconsistent_when_kwargs=True, ignore_star = False):
        # check whether varname is a valid input name
        if allow_inconsistent_when_kwargs and '**kwargs' in self.data['constraints']:
            return True
        if varname in self.data['constraints']:
            return True
        elif ignore_star:
            if varname in [x.replace('*', '') for x in self.data['constraints']]:
                return True
        return False

    def set_attr(self, key, value):
        self.data[key] = value

    def update_constraint(self, arg, descp, replace= {}, doc_dtype=None, allow_inconsistent_when_kwargs=True, ignore_star = False):
        if replace:
            descp = replace_symbol(descp, replace)

        if arg not in self.data['constraints']:
            arg = self.inconsistency_handle(arg, descp, allow_inconsistent_when_kwargs, ignore_star, doc_dtype)  # if returned, continue, else throw exception
            
            if arg==None:
                return
        
        self.data['constraints'][arg]['descp'] = pre_descp(descp)
        if doc_dtype:
            self.data['constraints'][arg]['doc_dtype'] = doc_dtype
    
    def inconsistency_handle(self, varname, descp, allow_inconsistent_when_kwargs, ignore_star, doc_dtype):
        if ignore_star :
            for x in self.data['constraints']:
                if varname == x.replace('*', ''):
                    return x
        if allow_inconsistent_when_kwargs and '**kwargs' in self.data['constraints']:
            if doc_dtype and 'required' in str(doc_dtype):
                self.init_input({varname:None})
            else:
                self.init_input({varname:'None'})
            return varname #continue add descriptoin
        

        if varname in self.deprecated_list:
            return None  # skip this argument

        # else throw exception
        raise GoToTheNextOne(self.url , self.title, '[Inconsistent] arg {} doesn\'t exist'.format(varname), save=True)
        

    def update_out_excep(self, label ,item, descp, replace= {}):
        # update outputs and excepton
        # label: outputs or exceptions
        # item: if it is itemize, otherwise item=None
        
        if label not in ['outputs', 'exceptions']:
            raise GoToTheNextOne(self.url , self.title, 'Unknown label', save=True)
        
        descp = replace_symbol(descp, replace)

        if item == None:
            if label in self.data:
                print('Warning: yaml conflict when updating {} (str vs item): {}'.format(label,self.url))
                return
                #raise GoToTheNextOne(self.url , self.title, 'yaml Conflict when updating {} (str vs item)'.format(label), save=True)                
            else:
                self.data[label]=pre_descp(descp)
        
        else:
            # update in item style
            if label in self.data:
                if isinstance(self.data[label], str):
                    print('Warning: yaml conflict when updating {} (str vs item): {}'.format(label,self.url))
                    return
                    #raise GoToTheNextOne(self.url , self.title, 'yaml Conflict when updating {} (str vs item)'.format(label), save=True)
                   
            else:
                self.data[label] = []
            
            self.data[label].append({item:pre_descp(descp)})

    def get_empty_arg(self):
        # return list of arg that has no description
        ret = []
        for arg in self.data['constraints']:
            if self.data['constraints'][arg]['descp']=='':
                ret.append(arg)

        return ret
            
    def save_file(self, folder, filename):

        # don't overwrite existing file
        path = folder+filename.lower()

        path = filename_wo_duplicate(path, '.yaml')
        # while os.path.exists(path+'.yaml') :
        #     path += '2'

        save_yaml(path,  self.data)

        return path

            
                