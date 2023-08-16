from util import *

import sys
# sys.path.insert(0,'/Users/danning/Desktop/deepflaw/exp2/code/dl-fuzzer/doc_analysis/subtree_mine/preprocess')
sys.path.insert(0,'./preprocess')
from normalize_sent import *
from nltk.parse.corenlp import CoreNLPDependencyParser
from mining_util import *
import nltk


MAX_TREE_LEN = 60
# MAX_ITER = 3
class Doc_Extractor():
    def __init__(self, doc_data, dtype_map, rule, all_category, all_anno, max_iter=-1):
        self.doc_data = doc_data
        self.dtype_map = dtype_map
        self.rule = rule
        self.all_category = all_category
        self.all_anno = all_anno
        self.max_iter = max_iter
        self.arg_list = self.init_arg_list()
        self.framework  = doc_data['package']
        self.dependency_parser = CoreNLPDependencyParser(url='http://localhost:9000')
        self.success = False

    def init_arg_list(self):
        return list(self.doc_data['constraints'].keys())

    def extract_constr(self, ):
        for argname in self.arg_list:
            arg_data = self.doc_data['constraints'][argname]
            arg_extractor = Arg_Extractor(arg_data, argname, self.dtype_map, self.framework, self.arg_list, self.rule, self.all_category, self.all_anno, self.max_iter)
            arg_extractor.extract_from_descp(self.dependency_parser)
            self.doc_data['constraints'][argname].update(arg_extractor.constraint)
            if arg_extractor.success: 
                self.success=True
        return self.doc_data
    

class Arg_Extractor():
    def __init__(self, arg_data, argname, dtype_map, framework, arg_list, rule, all_category, all_anno, max_iter):
        self.arg_data = arg_data
        self.argname = argname
        self.framework = framework
        self.dtype_map = dtype_map
        self.arg_list = arg_list
        self.rule = rule
        self.all_category = all_category
        self.all_anno = all_anno
        self.max_iter = max_iter
        self.constraint = {}            # dict {cat1: [constr1, constr2,..], cat2: ...}
        self.dependency_var = set()
        self.success = False        # =True if at least one constr extracted


    # def detect_rule(self, src_tree):
    #     matched_rule = []
    #     for subtree in self.rule:
    #         if is_subseq(subtree.split(), src_tree):
    #             matched_rule.append(subtree)
    #     return matched_rule


    
    def check_param(self, param):
        param = re.sub(r'[^a-zA-Z0-9_]', '', param)
        for arg in self.arg_list:
            if param.lower() == arg.lower():
                return arg
        return None
        # return param.lower() in [x.lower() for x in self.arg_list]

    def check_dtype(self, s, cat='dtype'):
        s = re.sub(r'[^a-zA-Z0-9_\.]', '', s)
        return self.dtype_map[cat].get(s, None)
        
    def check_ds(self, s, cat=['structure', 'tensor_t']):
        s = re.sub(r'[^a-zA-Z0-9_\.]', '', s)
        for c in cat:
            if s in self.dtype_map[c]:
                return c, self.dtype_map[c][s]
        return None, None

    def known_range(self, range_str):
        p = r'^[\[\(][\+-]?(\d+|inf),[\+-]?(\d+|inf)[\]\)]$'
        if re.match(p, range_str):
            return True
        else:
            return False

    def valid_range_shape(self, range_str):
        # it is mapped to a BSTR, however, some of them can be "(at least 2)" or some other illustration, which is not a valid range or shape
        # cannot do anything about "(optional)" "(default)"
        if 'optional' in range_str or 'default' in range_str:
            # hardcoded
            return False
        elif re.search(r'[0-9a-zA-Z]+(\s+[0-9a-zA-Z]+)+', range_str):
            return False
        return True


    def normalize_arg(self, s):
        for arg in self.arg_list:
            # with \b..\b dont match substring
            if arg[0]=='*':
                continue
            s = re.sub(r'\b{}\b'.format(arg), '&'+arg, s, flags=re.IGNORECASE)
            # src_str = re.sub(r'\b{}\b(?!\.)'.format(arg), '&'+arg, src_str)

        return s

    def set_dependency_var(self, var_list):
        self.dependency_var.update(var_list)

    def get_dependency_var(self, s, sep=[',', '[', ']', '(', ')', '+', '-', '/', '*', '...']):
        dependency_var = []
        if sep:
            splited= split_str(s, sep, boundary=False, not_empty=True, escape=True)
        else:
            splited = [s]

        for ss in splited:
            if is_empty_str(ss) or ss.isnumeric() or ss.startswith('&'):
                continue
            dependency_var.append(ss)

        return dependency_var

    def get_dim_cnt(self, shape_str, ndim_prefix='>='):
        # print(shape_str)
        dim_cnt = 0
        shape_str = shape_str.strip('[]()')
        shape_token = re.split(',',shape_str)
        shape_ret = []       # shape string to return
        unkown_dimension = False
        for token in shape_token:
            dim_cnt+=1
            # if not token:
            #     break
            # token = token.replace(' ', '')
            assert token.strip()==token # the shape_str should be pre-processed to remove all spaces
            if token == '...' or token == 'd1...dn' or token == '*':
                token = '...'
                unkown_dimension= True
                dim_cnt-=1  # doesn't count as dimension 

            shape_ret.append(str(token))
        
        # print(shape_ret)
        

        if unkown_dimension:
            if dim_cnt == 0:
                dim_cnt = -1        # don't update constaints since it is not a useful information
                shape_ret = []
            else:
                dim_cnt = ndim_prefix+str(dim_cnt)
        
        shape_ret='['+','.join(shape_ret)+']'
        return shape_ret, dim_cnt



    def parse_ir(self, subtree, constr_ir, constr_cat, anno_map):
        def _update_dict(d, key, val):
            if key in d:
                d[key].append(val)
            else:
                d[key] = [val]
            return d

        # assert len(str_constains_anno(s, anno_list))<=1
        assert constr_cat in self.all_category
        constr_result = {}     # the parsed constraint value to return
        # the original text of the annotaion, a list of options
        # the original IR should contain at most one annotation as the assertion
        deanno_ir = deannotaion(constr_ir, anno_map, self.all_anno)  
        for ir in deanno_ir: 
            if ir.startswith('&'):
                matched_param = self.check_param(ir[1:])
                if matched_param:
                    constr_result = _update_dict(constr_result, constr_cat, '&'+matched_param)
                else:
                    # todo: report doc bug
                    print('Warning: Documentation bug, cannot find parameter %s' % ir[1:])
                    
            # elif constr_cat == 'dtype':
            #     ir_parsed = parse_str(ir)
            #     assert len(ir_parsed)==1
            #     ir_mapped = self.check_dtype(ir_parsed[0].lower(), constr_cat)
            #     if ir_mapped:
            #         constr_result = _update_dict(constr_result, constr_cat, ir_mapped)
            #     else:
            #         print('Unable to find map from %s to data type for arg %s with subtree %s' % (ir_mapped, self.argname, subtree))
            # elif constr_cat == 'structure': 
            #     # merged from structure and tensor_t, need to separate them
            #     ir_parsed = parse_str(ir)
            #     assert len(ir_parsed)==1
            #     ds_cat, ir_mapped = self.check_ds(ir_parsed[0].lower())
            #     if ds_cat:
            #         constr_result = _update_dict(constr_result, ds_cat, ir_mapped)
            #     else:
            #         print('Unable to find map from %s to data structure for arg %s with subtree %s ' % (ir_mapped, self.argname, subtree))

            elif constr_cat == 'dtype':
                ir_parsed = parse_str(ir)
                # assert len(ir_parsed)==1
                for irp in ir_parsed:
                    ir_mapped = self.check_dtype(irp.lower(), constr_cat)
                    if ir_mapped:
                        constr_result = _update_dict(constr_result, constr_cat, ir_mapped)
                    else:
                        print('Unable to find map from %s to data type for arg %s with subtree %s' % (ir_mapped, self.argname, subtree))
            elif constr_cat == 'structure': 
                # merged from structure and tensor_t, need to separate them
                ir_parsed = parse_str(ir)
                # assert len(ir_parsed)==1
                for irp in ir_parsed:
                    ds_cat, ir_mapped = self.check_ds(irp.lower())
                    if ds_cat:
                        constr_result = _update_dict(constr_result, ds_cat, ir_mapped)
                    else:
                        print('Unable to find map from %s to data structure for arg %s with subtree %s ' % (ir_mapped, self.argname, subtree))


            elif constr_cat == 'shape':
                if not self.valid_range_shape(ir):
                    continue
                ir_parsed = rm_quo_space(ir)  
                if not is_shape_range_valid(ir_parsed):
                    continue
                ir_parsed = ir_parsed.lower()
                ir_parsed = self.normalize_arg(ir_parsed)
                self.set_dependency_var(self.get_dependency_var(ir_parsed))
                shape_ir, dim_cnt = self.get_dim_cnt(ir_parsed)
                if dim_cnt!=-1:
                    constr_result = _update_dict(constr_result, constr_cat, shape_ir)
                    constr_result = _update_dict(constr_result, 'ndim', dim_cnt)
                # else  don't update constaints since it is not a useful information, e.g., shape=[...]
            elif constr_cat == 'ndim':
                if not ir.isalnum():
                    ir = rm_quo_space(ir, merge_word=True)  
                ir_parsed = self.normalize_arg(ir) 
                ir_parsed = ir_parsed.lower()
                self.set_dependency_var(self.get_dependency_var(ir_parsed))
                constr_result = _update_dict(constr_result, constr_cat, ir_parsed)
            elif constr_cat == 'range': 
                if self.known_range(ir):
                    constr_result = _update_dict(constr_result, constr_cat, ir)
                else:
                    ir_parsed = rm_quo_space(ir, merge_word=True)  
                    if not is_shape_range_valid(ir_parsed):
                        continue 
                    ir_parsed = ir_parsed.lower() 
                    ir_parsed = self.normalize_arg(ir_parsed)
                    if ir_parsed[0] in '([' and  ir_parsed[-1]  in'])':
                        self.set_dependency_var(self.get_dependency_var(ir_parsed))
                        _update_dict(constr_result, constr_cat, ir_parsed)

            elif constr_cat == 'enum':
                ir_parsed = parse_str(ir)
                for irp in ir_parsed:
                    constr_result = _update_dict(constr_result, constr_cat, irp)
            else:
                assert(1==2)

        return constr_result
            
            
    def apply_rule(self, matched_rule, anno_map):
        for subtree in matched_rule:
            # print(subtree)
            # print(self.rule[subtree])
            for constr_cat in self.rule[subtree]:   # for each constraint category
                for constr_ir in self.rule[subtree][constr_cat]:
                    constr_val = self.parse_ir(subtree, constr_ir, constr_cat, anno_map)
                    # constr_val is a dict {cat1: [constr1, constr2,..], cat2: ...}
                    self.update_constr(constr_val)

            # print(self.argname)
            # print(subtree)
            # print(self.rule[subtree])
            # print()
                
                
    
    def update_constr(self, constr_val):
        # constr_val is a dict {cat1: [constr1, constr2,..], cat2: ...}
        # print(self.argname)
        # print(constr_val)
        # print()
        for cat in constr_val:
            if constr_val[cat]:
                self.success = True
                new_contr = [str(c) for c in constr_val[cat]]
                self.constraint[cat] = list_rm_duplicate(self.constraint.get(cat, []), new_contr, sort=True)

    def apply_default(self,):
        if 'default' in self.arg_data:
            default_val = self.arg_data['default']
            dtype, ndim = extract_default(default_val)
            constr_val = {}
            if not dtype is None:
                dtype_mapped = self.check_dtype(dtype.lower(), 'dtype')
                if dtype_mapped:
                    constr_val['dtype'] = [dtype_mapped]
                else:
                    print('Error')
            if not ndim is None:
                constr_val['ndim'] = [ndim]

            self.update_constr(constr_val)
        else:
            return

    def extract_from_descp(self, dependency_parser):
        # extract constraints from the description 
        def _process(normalized_content, anno_map):
            if not normalized_content or normalized_content.isspace() or normalized_content == '':
                return 
            normalized_content = normalized_content.lower()

            anno_map = normalize_annomap(anno_map, self.all_anno)
            # 2. get parsing tree from text
            _, horizontal_format = generate_parsing_tree(dependency_parser, normalized_content)
            if len(horizontal_format)>MAX_TREE_LEN:
                return
            # here horizontal_format is a list of str.
            # 3. detect subtree
            # print(normalized_content)
            matched_rule = detect_match_rule(self.rule, normalized_content, horizontal_format, self.max_iter, threadsafe=True) # in util.py
            # if matched_rule:
            #     print(matched_rule)
            # print('matched subtree for sent %s' % normalized_content)
            # print(matched_rule)
            # 4. process constr & update constr
            self.apply_rule(matched_rule, anno_map)
     


        for sent in nltk.sent_tokenize(self.arg_data['descp']):
            # 1. parse text
            normalized_descp, anno_map = normalize_sent(sent, self.framework, self.arg_list, self.argname)
            # print(normalized_descp)
            _process(normalized_descp, anno_map)

        if 'doc_dtype' in self.arg_data:
            normalized_docdtype, anno_map = normalize_docdtype(self.arg_data['doc_dtype'], self.framework, self.arg_list, self.argname)
            _process(normalized_docdtype, anno_map)
        
        if 'default' in self.arg_data:
            normalized_default, anno_map = normalize_default(self.arg_data['default'], self.all_anno, self.framework, self.arg_list, self.argname)
            _process(normalized_default, anno_map)

        # self.apply_default()
        

    
        

def str_constains_anno(s, anno_list):
    # returns the annotation a string (`s`) contains. 
    # anno_list: all possible annotation
    contain_anno = []
    for anno in anno_list:
        if re.search(r'\b{}\b'.format(anno), s, flags=re.IGNORECASE):
            contain_anno.append(anno)
    return contain_anno

def normalize_annomap(anno_map, anno_list):
    # in case of nested anno_map
#     ret = {}
    for anno in anno_map:
        new_mapping = []
        for mapping in anno_map[anno]:
            if str_constains_anno(mapping, anno_list):
                m = deannotaion(mapping, anno_map, anno_list)
                new_mapping+= m
            else:
                new_mapping.append(mapping)
        anno_map[anno] = new_mapping
    return anno_map


def deannotaion(s, anno_map, anno_list):
    # print('111'+s)
    # s = ''
    s2process=[s]
    ret = []
    while s2process:
        ss = s2process.pop(0)
        anno2map = str_constains_anno(ss, anno_list)
        if not anno2map:
            ret.append(ss)
            continue
        for anno in anno2map:
            if not anno_map[anno]:
                print(s)
                print(anno)
                print(anno_map)
            assert anno_map[anno]
            for original_token in anno_map[anno]:
                tmp = re.sub(r'\b{}\b'.format(anno), original_token, ss)
                    
                # 
                s2process.append(tmp)
    ret = list(set(ret))
    for ss in ret:
        assert not str_constains_anno(ss, anno_list)
#     if str_constains_anno(tmp, anno_list):
#         print('Failed to deannotate %s with anno_map %s' % (s, str(anno_map)))
    return ret

    
def extract_default( default_val):

    # check bool
    bool_const = ['false', 'true']
    if str(default_val).lower() in bool_const:
        return 'bool', 0
        
    
    if str(default_val) in  ['None', '_Null']:
        return None, None
    else:
        try:
            int(default_val)
            return 'int', 0
        except:
            pass
        
        try:
            float(default_val)
            return 'float', 0
        except:
            pass

        if len(str(default_val))>0 and str(default_val)[0] in ['(', '[']:
            ndim = len(re.findall(r'[\[\(]', str(default_val).split(',')[0]))
            return None, ndim

        elif re.match(r'.*\..*', str(default_val))!=None or str(default_val).startswith('<'):
            return None, None
        else:
            return 'string', None