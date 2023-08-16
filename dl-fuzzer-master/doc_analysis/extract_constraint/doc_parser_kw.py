
import re
from extract_utils import *


class Parser:
    def __init__(self, info, dt_map, all_target, stop_name=None):
        self.info = info
        self.dt_map = dt_map
        self.stop_name = stop_name
        self.all_target = all_target
        self.cnt = 0  # increase only in self.print_update

    def match_sent(self, arg, descp, pat, target):
        if pat.pat_dict['direct_map']:
            return self.direct_map(arg, descp, pat, target)
        else:
            return self.group_map(arg, descp, pat, target)

    
    def match_ret_init(self, target, ow=False):
        # init match_ret
        return {target:{'nval':[], 'p_matched':[], 'ow': ow}}

    def match_ret_check(self, match_ret, other_target, ow=True):
        # check whether other_target exist in match_ret, if not create new one
        if not match_ret.get(other_target, None):
            match_ret[other_target] = {'nval':[], 'p_matched':[], 'ow': ow}
        return match_ret


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
                if tmp.lower() in self.dt_map.pat_dict[m]:
                    ret.append(self.dt_map.pat_dict[m][tmp])
        return ret

    def check_dtype_all_map(self, dt_l, return1list=False):
        # return1list=True: return in one list, False: return in dict
        ret_dict = {}
        ret_list = []
        for map in self.dt_map.pat_dict:
            tmp  = self.check_dtype(dt_l, [map])
            ret_dict[map] = tmp
            ret_list+= tmp

        if return1list:
            return ret_list
        return ret_dict

    def parse_range_shape_brackets(self, range_str, pat, p):
        # only deal with the range/shape inside brackets () [] ..

        range_str = re.sub(',\s', ',', range_str)
        range_str = re.sub(r'([a-zA-Z])\s([a-zA-Z])', r'\1_\2', range_str)

        # replace all argument name -> &arg_name
        range_str = self.replace_arg(range_str)
        
        # all replace pattern from the yaml file 
        range_str = replace_symbol_with_dict(range_str, pat.pat_dict['pat'][p].get('replace', {})) 

        # after replace all possible paranthesis in the str, try to find only one pair of parenthesis.
        # if this doesn't work later, try stack
        '''
        Failed example:
        in the range `(-rank(values), rank(values))`. 
        As in Python, indexing for axisis 0-based. 
        Positive axis in the rage of `[0, rank(values))` 
        refers to `axis`-th dimension. And negative axis 
        refers to `axis + rank(values)`-th dimension.
        '''
        # try:
        #     range_str = re.search(r'[\[\(][^()]*[\]\)]',range_str).group(0)
        # except:
        #     pass 

        # add to shape_var
        return range_str

    def replace_arg(self, src_str):
        # replace all argument name -> &arg_name
        for arg in set(arg.lower() for arg in self.info['constraints']):
            # with \b..\b dont match substring
            if arg[0]=='*':
                continue
            # print('\b{}\b'.format(arg))
            src_str = re.sub(r'\b{}\b(?!\.)'.format(arg), '&'+arg, src_str)

        return src_str


    def match_other_target(self, match_ret, target, pat, p, ow):
        for pk in pat.pat_dict['pat'][p]:
            if pk!=target and pk in self.all_target.pat_dict:
                if match_ret.get(pk, []) == []:
                    match_ret[pk] = {'nval':[], 'p_matched':[], 'ow': ow}
                # don't add p_matched (otherwise duplicate)
                nv = str(pat.pat_dict['pat'][p][pk])


                if pk in ['dtype', 'tensor_t', 'structure']:
                    tmp = self.check_dtype_all_map([nv], return1list=False)
                    if pk == 'dtype':
                        nv = tmp['dtype_map'] + tmp['plural_map']
                    elif pk == 'tensor_t':
                        nv = tmp['tensor_t_map']
                    elif pk == 'structure':
                        nv = tmp['structure']

                    nv = nv[0]

                if pk == 'shape':
                    sv = self.parse_shapevar(nv, ['[', ']', ','])
                    self.set_shape_var(sv)

                match_ret[pk]['nval'].append(nv)

        return match_ret
                        
    def set_shape_var(self, shape_var, cat = 'dependency'):
        # input: a list
        # set self.info['shape_var']
        old = self.info.get(cat, [])
        final = list_rm_duplicate(old, shape_var, sort=True)
        if len(final)>0:
            self.info[cat] = final


    def parse_shapevar(self, s, split_word=[]):
        shape_var_ret = []

        if split_word:
            splited= split_str(s, split_word, boundary=False, not_empty=True, escape=True)
        else:
            splited = [s]

        for ss in splited:
            if is_empty_str(ss) or ss.isnumeric() or '&' in ss:
                continue
            shape_var_ret.append(ss)

        return shape_var_ret


    def set_c(self, arg, label, val, ow, append=False, pat=None, p=None):
        # set constraints label = val for argument arg
        # label: constraint category 
        # val: new constraint value
        # ow: can be overwrite or not
        # append: can append or not
        # pat: the pat obj
        # p: the list of pattern that successfully matched

        

        def _conflict_range(range_ls):
            # deal with conflict range
            default_val = self.info['constraints'][arg].get('default', None)
            # hard code, so far only one case of conflict
            if range_ls[0] == '(-inf,0)' and range_ls[1] == '(0,inf)' and int(default_val) == 0:
                return '(-inf,inf)'
            else:
                print('***************************range conflict************************')
                return range_ls[0]
        if val == None:
            return 

        if not isinstance(val, list): # make it a list
            val = [val]

        if len(val)==0:
            return
        
        val = list_rm_duplicate(val, sort=True)  # remove duplicate first

        # whether the label is empty
        if not self.info['constraints'][arg].get(label, []) :
            empty = True
        else: 
            empty = False



        # if label=='range':  # hardcode
        #     # save as key-value, not list
        #     if not empty and not ow:
        #         return
                
        #     if not empty or len(val)>1:
        #         old = self.info['constraints'][arg].get(label, None)
        #         if old:
        #             final = _conflict_range(val.append(old))
        #         else:
        #             final = _conflict_range(val)

        #         if not final:
        #             final = val[0]
        #     else:
        #         final = val[0]  
        #     self.info['constraints'][arg][label] = final
        #     self.print_update(arg, label, pat=pat, p=p)
        #     return 


        if empty:  # if label doesn't exist, assign directly
            self.info['constraints'][arg][label] = val
            self.print_update(arg, label, pat=pat, p=p)
            return


        # label exist
        if append:
            # overwrite or not, append the val to the label
            final = list_rm_duplicate(val, self.info['constraints'][arg][label], sort=True)     
            self.info['constraints'][arg][label] = final
            self.print_update(arg, label, pat=pat, p=p)
            return

        # don't append
        if ow:  # assign directly
            self.info['constraints'][arg][label] = val
            self.print_update(arg, label, pat=pat, p=p)
            return 
        else:
            # label exists, don't append, don't overwrite, do nothing
            return



    def print_update(self, arg, cls, pat=None, p=None):
        #print(p)
        self.cnt+=1
        if cls=='dtype':
            #print('API:{}\tArg:{}\nDescp:{}\npattern:{}\ndtype:{}\n'.format(self.info['title'],arg, self.info['constraints'][arg]['descp'], p, self.info['constraints'][arg]['dtype']))
            pass
        if p :
            pat.upcnt(p)
        
    def keyword_match(self, pat, stop=True, update_ndim=True):
        def helper(arg, keyword_ls):
            ret = []
            single  = False
            if stop and arg in self.stop_name :
                return ret, single
            src = [self.info['constraints'][arg].get('descp', [])] +  self.info['constraints'][arg].get('doc_dtype', [])
            if 'sub' in pat.pat_dict:
                src = replace_symbol_with_dict(src, pat.pat_dict['sub'])

            for s in src:
                if s:
                    for word in keyword_ls:
                        if re.search(r'\b{}\b'.format(word.lower()), s.lower()):
                            ret.append(word.lower())
                            if re.search(r'(a|an|the|one|single|^)\s*[`\"]*\b{}\b[`\"]*'.format(word.lower()), s.lower()):
                                single = True

                            #self.set_c(arg, constr_map)
                
            return ret, single
        for arg in self.info['constraints']:
            matched = []
            single = False
            for k in pat.pat_dict['map']:
                m, s = helper(arg, pat.pat_dict['map'][k])
                matched += m
                if k == 'dtype':
                    single = s
            
            constr_map = self.check_dtype_all_map(matched, return1list=False)
            match_constr = {}
            match_constr['dtype'] = list(set(constr_map['dtype_map'] + constr_map['plural_map']))
            match_constr['tensor_t'] = list(set(constr_map['tensor_t_map']))
            match_constr['structure'] = list(set(constr_map['structure'] + constr_map['1dstructure']))
            for label in match_constr:
                for constr in match_constr[label]:
                    self.set_c(arg, label, constr, ow=False, append=True)
            
            if constr_map['1dstructure']:
                self.set_c(arg, 'ndim', '1', ow=False, append=True)
            if not constr_map['tensor_t_map']:
                if single  and constr_map['dtype_map'] and not constr_map['plural_map']:
                    self.set_c(arg, 'ndim', '0', ow=False, append=True)
        



    def match_name(self, pat): 
        def _handle_dtype(pk, nv):
            tmp = self.check_dtype_all_map([nv], return1list=False)
            if pk == 'dtype':
                ret = tmp['dtype_map'] + tmp['plural_map']
            elif pk == 'tensor_t':
                ret = tmp['tensor_t_map']
            elif pk == 'structure':
                ret = tmp['structure']+tmp['1dstructure']
            return ret

        # no target
        # try with variable name
        for arg in self.info['constraints']:
            ndt = None
            for p in pat.pat_dict['pat']:
                if re.match(r'{}'.format(p), arg.lower()):
                    # matched
                    for pk in pat.pat_dict['pat'][p]:
                        if  pk in self.all_target.pat_dict:
                            nv = str(pat.pat_dict['pat'][p][pk])
                            if pk in ['dtype', 'tensor_t', 'structure']:
                                nv =  _handle_dtype(pk, nv)
                            # overwrite anything existing directly
                            self.set_c(arg, pk, nv, ow=pat.pat_dict['pat'][p]['ow'], append=pat.pat_dict['pat'][p]['append'], pat=pat, p=p) 
                    break
                
                
            
            
    def match_default(self, default_map=None, stop=True):

        # try with default values, priority: lowest
        for arg in self.info['constraints']:
            if arg in self.stop_name and stop:
                continue
            if 'default' in self.info['constraints'][arg]:
                default_val = self.info['constraints'][arg]['default']
                if default_map and default_val in default_map.pat_dict:
                    dt = default_map.pat_dict[default_val]
                    def_constr = {'val':None, 'dtype': dt, 'ndim': None}
                else:
                    def_constr = convert_default(str(default_val))  # default_value already updated when collecting from web
                
                if def_constr['dtype']:
                    new_dt = self.check_dtype_all_map([def_constr['dtype']], return1list=True)
                    if new_dt[0] in ['tf.string', 'string', 'np.string']:
                        self.set_c(arg, 'dtype', new_dt, ow=False, append=False) 
                    else:
                        self.set_c(arg, 'dtype', new_dt, ow=False, append=True) 
                if def_constr['ndim']!=None: # could be none
                    self.set_c(arg, 'ndim', str(def_constr['ndim']) , ow=False, append=True) 



    def detect_deprecated(self, pat_obj):
        deprecated_list = []
        for arg in self.info['constraints']:
            if arg in self.info['inputs'].get('deprecated', []):  # already in the list
                continue

            descp = self.info['constraints'][arg]['descp']
            if descp:
                descp2 = pre_descp(descp)
                for p in pat_obj.pat_dict['pat']:
                    if re.findall(p, descp2):
                        deprecated_list.append(arg)
                        break
        if deprecated_list:
            self.info['inputs']['deprecated'] = list_rm_duplicate(deprecated_list, self.info['inputs'].get('deprecated', []), sort=True)

    def check_arg(self, rslt, varname, findall, pat, p):
        if 'check_arg' in pat.pat_dict['pat'][p]:
            arg_ls = get_group(rslt, pat, p, group='check_arg', findall=findall)
            if arg_ls:
                for arg in arg_ls:
                    if arg!=varname:
                        return False
                return True
            else:
                return False # empty
        else:
            return True # no check_arg, pass

    def count_len(self, s):
        # count the length of an 1-d array e.g. [a,b,c] or (a,b,c). don't deal with multiple dimension
        return s.count(',')+1
        
    def group_map(self, arg, descp, pat, target):
        
        def _shape_process(nval_group_it, p, findall = True, ndim=False, ndim_prefix='>'):
            # extracted part from _group_map when target is shape
            # check if the word equals to the varname

            if 'replace' in pat.pat_dict['pat'][p]:
                nval_group_it = replace_symbol_with_dict(nval_group_it, pat.pat_dict['pat'][p]['replace'])

            
            nval_final= self.parse_range_shape_brackets(nval_group_it, pat, p)
            shape_var = self.parse_shapevar(nval_final, split_word = pat.pat_dict.get('split_word', []))

            dim_cnt = 0
            sp_item = re.split(',',nval_final)
            ret = '['
            unkown_dimension = False
            for sp in sp_item:
                if not sp:
                    break
                sp = sp.replace(' ', '')
                if sp == '...':
                    unkown_dimension= True
                    dim_cnt-=1  # doesn't count as dimension 


                ret+=str(sp)
                ret+=','
                dim_cnt+=1

            if ret[-1] == ',':
                ret = ret[:-1]  # delete the last comma
            ret+=']'
            if unkown_dimension:
                if dim_cnt == 0:
                    dim_cnt = '?'
                else:
                    dim_cnt = ndim_prefix+str(dim_cnt)

            if ndim and pat.pat_dict['pat'][p].get('ret_count', True):
                return ret, dim_cnt, shape_var
            else:
                return ret, nval_final, shape_var
            

        def _dtype_from_group(dt, nv, p, sep=[]):

            # dt: \1 or \2 .. or "int" that is specified in the pattern file. 
            # nv: element in rslt when findall=True (a list/str)

            # the function: find the element corresponding to dt(group) \
            # and map it to the standard dtype name. 
            # return 

            if str(dt)[0] == '\\':
                # map group
                nv_dt = get_group_findall(nv, pat, p, group=int(str(dt)[1:]))
            else:
                nv_dt = dt
            
            if not isinstance(nv_dt, list):
                nv_dt = [nv_dt]

            dt_final = {}
            dt_list = []

            for nv_it in nv_dt:
                nv_parsed = parse_str(nv_it, sep = sep)
                tmp = self.check_dtype_all_map(nv_parsed, return1list=False)
                if not dt_final:
                    dt_final = tmp
                else:
                    dt_final['dtype_map'] += tmp['dtype_map']
                    dt_final['plural_map'] += tmp['plural_map']
                    dt_final['tensor_t_map'] += tmp['tensor_t_map']
                    dt_final['structure'] += tmp['structure']
                    dt_final['1dstructure'] += tmp['1dstructure']

                tmp2 = self.check_dtype_all_map(nv_parsed, return1list=True)
                dt_list+=tmp2

            return dt_final, dt_list

        def _check_dependent(p, parsed_val):
            shape_var = []
            for pv in parsed_val:
                if pv.isnumeric():
                    return False, None
                pv = self.replace_arg(pv)
                sv = self.parse_shapevar(pv, split_word=[])
                if sv:
                    shape_var+=sv
            if shape_var:
                #self.set_shape_var(shape_var)
                print('{} unclear dependent for input {}'.format(self.info['title'], arg))
                return False, None
            else:
                return True, pv


        def _check_prereq(p, match_ret, target):
            # check prereq
            for pre in pat.pat_dict['pat'][p].get('prereq', []):
                if pre in match_ret[target]['p_matched']:
                    return False
            return True

        # def _parse_dict(rslt, match_ret, p, target, ds, ds_dtype):
        #     # deprecated
        #     # parse dict information. 
        #     # no length information to parse


        #     if not ds_dtype:
        #         match_ret[target]['nval'].append(ds)
        #         return match_ret, True

        #     for nv in rslt:
        #         dt_dict1, dt_list1 = _dtype_from_group(ds_dtype[0], nv, p, pat.pat_dict.get('split_word', []))
        #         dt_dict2, dt_list2 = _dtype_from_group(ds_dtype[1], nv, p, pat.pat_dict.get('split_word', []))
                
        #         dtype = (dt_dict1['dtype_map']+dt_dict1['plural_map']+dt_dict2['dtype_map']+dt_dict2['plural_map'])
        #         tensor_t = (dt_dict1['tensor_t_map']+dt_dict2['tensor_t_map'])
                
        #         # all types
        #         nv_final = dtype+tensor_t

        #         if not dt_list1:
        #             dt1 = '?'
        #         else:
        #             dt1 = dt_list1[0]

        #         if not dt_list2:
        #             dt2 = '?'
        #         else:
        #             dt2 = dt_list2[0]


        #         if dt1=='?' and dt2=='?':
        #             match_ret[target]['nval'].append(ds)
        #         else:
        #             match_ret[target]['nval'].append('{}({}:{})'.format(ds,dt1,dt2))
                

        #         match_ret = self.match_ret_check(match_ret, 'dtype', ow=True)
        #         #match_ret = self.match_ret_check(match_ret, 'tensor_t', ow=True)

        #         match_ret['dtype']['nval'] += dtype
        #         #match_ret['tensor_t']['nval'] += tensor_t

        #     if match_ret[target]['nval']:
        #         success = True
        #     else:
        #         success = False
        #     return match_ret, success

        descp2 = pre_descp(descp, pat)
        update_ndim=True
        # target = pat.pat_dict['target']

        # if target == 'tensor_t':   # hard code
        #     target = 'dtype'

        ow = True
        match_ret = self.match_ret_init(target, ow=ow)

        for p in pat.pat_dict['pat']:
            success = False
            findall = pat.pat_dict.get('findall', False)
            rslt = match_pat(descp2, p, findall=findall)


            if not rslt:
                continue

            
            if not _check_prereq(p, match_ret, target):
                continue
            
            # if "check_arg" label exist, check
            if not self.check_arg(rslt, arg, findall, pat, p):
                continue

            nval_group = get_group(rslt, pat, p, group='group', findall=findall)
            shape_var = []
            if nval_group and pat.pat_dict['pat'][p].get('dependent', False):
                success, nv = _check_dependent(p, nval_group)

                if success:
                    match_ret[target]['nval'].append('{}:{}'.format(target, nv))


            elif target == 'range':
                # find all
                if 'range' in pat.pat_dict['pat'][p]:
                    match_ret[target]['nval'].append(pat.pat_dict['pat'][p]['range'])
                    success = True
                else:
                    for nv_it in get_group(rslt, pat, p, group='full_range_group', findall=findall):
                    # for nv_it in nval:
                    #     if isinstance(nv_it, str):
                    #         nv = nv_it
                    #     else:
                        nv= self.parse_range_shape_brackets(nv_it, pat, p)

                        sv = self.parse_shapevar(nv, split_word = pat.pat_dict['split_word'])

                        match_ret[target]['nval'].append(nv)
                        success = True
                        self.set_shape_var(sv)
                # if len(match_ret[target]['nval'])>0:
                #     match_ret[target]['p_matched'].append(p)

            elif target == 'dtype' :

                #FINDALL
                update_ndim = True
                if pat.pat_dict['pat'][p].get('dtype', None):
                    nval_group = [pat.pat_dict['pat'][p]['dtype']]

                for nv in nval_group:

                    # parse datatype from a string
                    kwargs = dict(dt_str=nv, stop_word=pat.pat_dict.get('stop_word', None), sep= pat.pat_dict.get('sep', None))
                    ntype = parse_str(**{k: v for k, v in kwargs.items() if v!=None})


                    # if pat.pat_dict['check_dt']:  # dead code
                    # check dtype
                    ntype = self.check_dtype_all_map(ntype, return1list=False)


                    
                    #if there is plural/tensor_t map, don't update ndim
                    if ntype['plural_map'] or ntype['tensor_t_map'] or ntype['structure'] or ntype['1dstructure']:
                        update_ndim = False
                    else:
                        update_ndim = True

                    ntype_final = ntype['dtype_map'] + ntype['plural_map']



                    if len(ntype_final)>0:
                        #match_ret[target]['p_matched'].append(p)
                    
                        match_ret[target]['nval']+=ntype_final
                        success = True

                    if ntype['tensor_t_map']:
                        match_ret = self.match_ret_check(match_ret, 'tensor_t', ow=True)
                        match_ret['tensor_t']['nval'] += ntype['tensor_t_map']
                        match_ret['tensor_t']['p_matched'].append(p)
                        success = True

                    if ntype['structure'] and pat.pat_dict['pat'][p].get('update_structure', False):
                        match_ret = self.match_ret_check(match_ret, 'structure', ow=True)
                        match_ret['structure']['nval'] += ntype['structure']
                        match_ret['structure']['p_matched'].append(p)
                        success = True

            # elif target == 'structure':
            # deprecated
            # need to update 1dstructure map
            #     # findall

            #     update_ndim = True

            #     ds_original = pat.pat_dict['pat'][p][target]
            #     ds_dtype = pat.pat_dict['pat'][p].get('ds_dtype', [])
            #     ds_len = pat.pat_dict['pat'][p].get('len', None)
            #     ds_value = pat.pat_dict['pat'][p].get('value', None)

            #     if ds_original=='dict':
            #         match_ret, success = _parse_dict(rslt, match_ret, p, target, ds_original, ds_dtype)

            #     else:
            #         for nv in rslt:
            #             if ds_original[0] == '\\':
            #                 ds = _dtype_from_group(ds_original, nv, p,  pat.pat_dict.get('split_word', []))[0]['structure']
            #             else:
            #                 ds = [ds_original]
            #             if not ds:
            #                 continue

            #             candidate_value = []

            #             if ds_dtype:
            #                 dtype = []
            #                 tensor_t = []
            #                 for dt in ds_dtype:
            #                     dt_all, dt_all_list = _dtype_from_group(dt, nv, p,  pat.pat_dict.get('split_word', []))
            #                     dtype += (dt_all['dtype_map']+dt_all['plural_map'])
            #                     tensor_t+= dt_all['tensor_t_map']
            #                 nv_final = dt_all_list

                            
            #                 if len(nv_final)>0:
            #                     # also add dtype
            #                     match_ret = self.match_ret_check(match_ret, 'dtype', ow=True)
            #                     #match_ret = self.match_ret_check(match_ret, 'tensor_t', ow=True)


            #                     for nf in nv_final:
            #                         for dds in ds:
            #                             candidate_value.append('{}({})'.format(dds,nf))
            #                         if nf in tensor_t:
            #                             update_ndim = False
            #                             #match_ret['tensor_t']['nval'].append(nf)
            #                         elif nf in dtype:
            #                             match_ret['dtype']['nval'].append(nf)
            #                         else:
            #                             update_ndim = False

            #                     success = True

            #                 else:   # no dtype information
            #                     candidate_value += ds
            #                     success = True
            #                     update_ndim = False
                                

            #             if not ds_value:
            #                 for ca in candidate_value:
            #                     match_ret[target]['nval'].append(ca)

            #             else :
            #                 if ds_value[0]=='\\':
            #                     # ds_value_val = ['(dh, dw)']
            #                     ds_value_val = get_group(rslt, pat, p, group=int(ds_value[1:]), findall=True)
            #                 else:
            #                     ds_value_val = [ds_value]

            #                 for dv in ds_value_val:
            #                     # (dh, dw)->(dh,dw)
            #                     parsed = self.parse_range_shape_brackets(dv, pat, p)
            #                     parsed = replace_symbol_with_dict(parsed, {r',\)': ')', r'\b(or|and)\b': ''})
            #                     val_len = self.count_len(parsed)
            #                     if parsed:
            #                         sv = self.parse_shapevar(parsed, split_word=pat.pat_dict.get('split_word', []))
            #                         if sv:
            #                             self.set_shape_var(sv)

            #                         if not candidate_value:
            #                             candidate_value = ds
            #                         for cv in candidate_value:
            #                             match_ret[target]['nval'].append('{}:{}'.format(cv, parsed))
                                    
            #                         # update length to shape
            #                         match_ret = self.match_ret_check(match_ret, 'shape', ow=True)
            #                         match_ret['shape']['nval'].append('[{}]'.format(val_len))
                                    
            #                         success=True

            #             # length information
                        
            #             if ds_len!=None:

            #                 match_ret = self.match_ret_check(match_ret, 'shape', ow=True)

            #                 if str(ds_len)[0] == '\\':
            #                     # map group
            #                     if isinstance(nv, str):
            #                         nv_len = nv
            #                     else:
            #                         nv_len = nv[int(str(pat.pat_dict['pat'][p]['len'])[1:])-1]
            #                     if nv_len:
            #                         nv_final = parse_str(nv_len, min_len =1)

            #                     else:
            #                         nv_final = []
            #                     if nv_final:
            #                         shape_var = []
            #                         for nvf in nv_final:
            #                             kwargs = dict(s=nvf, split_word=pat.pat_dict.get('split_word', None))
            #                             sv = self.parse_shapevar(**{k: v for k, v in kwargs.items() if v!=None})
            #                             if sv:
            #                                 shape_var+=sv
            #                         self.set_shape_var(shape_var)
            #                 else:
            #                     # direct value
            #                     nv_final = [ds_len]



            #                 for nvf in nv_final:
            #                     len_val = pat.pat_dict['pat'][p].get('len_prefix', '')+str(nvf)
            #                     match_ret['shape']['nval'].append('[{}]'.format(len_val))
                        
                        


            #         if not success:
            #             match_ret[target]['nval']+=ds
            #             success = True

   

            elif target == 'enum' and nval_group:
                
                # no findall
                for nv_it in nval_group:
                    if 'replace' in pat.pat_dict['pat'][p]:
                        nv_it = replace_symbol_with_dict(nv_it, pat.pat_dict['pat'][p]['replace'])

                    # if isinstance(nv_it, str):
                    #     nv = nv_it
                    # else:
                    #     nv = nv_it[int(pat.pat_dict['pat'][p]['group'])-1]
                    kwargs = dict(dt_str=nv_it, stop_word=pat.pat_dict.get('stop_word', None), min_len=1)
                    ntype_ls = parse_str(**{k: v for k, v in kwargs.items() if v!=None})

                    ntype_original_case = [get_original_case(descp, x) for x in ntype_ls]
                    if len(ntype_ls)>0:
                        #match_ret[target]['p_matched'].append(p)
                        match_ret[target]['nval']+=[x for x in ntype_original_case if x!=None]
                        success = True
                
            elif target=='shape':
                # FINDALL     
                if findall:
                    
                    for nv in nval_group:
                        # original str: `[height, width, channels]`
                        # nv: ('with', 'height, width, channels')
                        # nval_final : [height,width,channels]

                        nval_final, dim_cnt , shape_var = _shape_process(nv, p, findall = findall, ndim=True, ndim_prefix=pat.pat_dict['pat'][p].get('ndim_prefix', '>'))
                        if nval_final:
                            # check balance 
                            if is_balanced(nval_final):
                                if shape_var:
                                    self.set_shape_var(shape_var)
                                match_ret[target]['nval'].append(nval_final)
                                #match_ret[target]['p_matched'].append(p)
                                success = True
                                if match_ret.get('ndim', []) == []:
                                    match_ret['ndim'] = {'nval':[], 'p_matched':[], 'ow': True}
                                
                                # don't add p_matched (otherwise duplicate)
                                match_ret['ndim']['nval'].append(str(dim_cnt))
                                
                            else:
                                print('unbalanced shape: '+str(nval_final))
                                              
            

            elif target=='ndim':
                # findall
                
                nval_final = []
                if 'ndim' in pat.pat_dict['pat'][p]:
                    match_ret[target]['nval'].append(pat.pat_dict['pat'][p].get('prefix', '')+str(pat.pat_dict['pat'][p]['ndim']))
                    success=True

                else:
                    from_shape = pat.pat_dict['pat'][p].get('from_shape', False)

                    for nv_it in nval_group:

                        # info extract from shape, need to cnt dim
                        if from_shape:
                            
                            _, nval_fix, shape_var = _shape_process(nv_it, p, findall = findall, ndim=True, ndim_prefix=pat.pat_dict['pat'][p].get('ndim_prefix', '>'))
                            
                        # extract from parsed str
                        else: 
                            nval_fix = nv_it

                            nval_fix = self.replace_arg(nval_fix)
                            nval_fix = replace_symbol_with_dict(nval_fix, pat.pat_dict['pat'][p].get('replace', {}))
                            nval_fix = str(pat.pat_dict['pat'][p].get('prefix', ''))+str(nval_fix)
                            shape_var = self.parse_shapevar(nval_fix, pat.pat_dict.get('split_word', []))
                        


                        if nval_fix!=None:  # bug fixed: nval_fix can be 0, so cannot use `if nval_fix:`
                            match_ret[target]['nval'].append(str(nval_fix))
                            success = True

                        if shape_var and pat.pat_dict['pat'][p].get('keep_shapevar', False):
                            self.set_shape_var(shape_var)
                            #match_ret[target]['p_matched'].append(p)
                        # don't break
                

            if success:
                #  add pattern as matched
                match_ret[target]['p_matched'].append(p)
                # check other target
                if not update_ndim:
                    continue
                match_ret = self.match_other_target(match_ret, target, pat, p, ow)
                
    
            if pat.pat_dict['break']:
                break
        
        # test
        # if arg =='axes':
        #     print(match_ret)
        return match_ret    

    
    def direct_map(self, arg, descp, pat, target):
        prev = None
        prev_p = None
        ow = False 
        map_target = True
        
        descp2 = pre_descp(descp)
        # target = pat.pat_dict['target']
        match_ret = self.match_ret_init(target, ow)
        
        for p in pat.pat_dict['pat']:
            
            ntype = pat.pat_dict['pat'][p][target]
            ntype = self.check_dtype_all_map([ntype], return1list=True)[0]

            rslt = re.search(p, descp2)
            if rslt:  # if result is not None

                if pat.pat_dict['pat'][p].get('group', None): # need to parse a group
                    if pat.pat_dict['pat'][p]['group_type'] == 'arg':  # the group is argument name
                        if arg == rslt.group(pat.pat_dict['pat'][p]['group']):  # arg name matches
                            ow = pat.pat_dict['pat'][p].get('overwrite', True)
                            if ow:  # if allow to overwrite
                                match_ret[target] = {'nval':ntype, 'p_matched':p, 'ow': ow}
                                break
                            else:   # weak pattern, save and keep going
                                prev = ntype
                                prev_p = p
                        else: 
                            continue
                ow = pat.pat_dict['pat'][p].get('overwrite', True)

                if ow:
                    match_ret[target] = {'nval':ntype, 'p_matched':p, 'ow': ow}
                    break
                else:
                    prev = ntype
                    prev_p = p


        if not match_ret[target]['nval'] and prev!=None:
            match_ret[target] = {'nval':prev, 'p_matched':prev_p, 'ow': ow}
        
        
        if match_ret[target]['nval'] : #and map_target ) or (not map_target):
            p = match_ret[target]['p_matched']
            match_ret = self.match_other_target(match_ret, target, pat, p, ow)

        return match_ret
    



    def parse_descp(self, pat, stop=True, cat = 'descp'):
        append = pat.pat_dict['append']  # whether to append
        target = pat.pat_dict['target']
        if target == 'tensor_t':
            target = 'dtype'

        for arg in self.info['constraints']:    # for each argument
            if stop and arg in self.stop_name:
                continue

            if arg in self.info['inputs'].get('deprecated', []):
                continue
                
            if pat.pat_dict['parse_sent']:      # whether need to parse by sentence
                # dead code
                pass
            else:
                target_str = self.info['constraints'][arg].get(cat, '')
                if not target_str:
                    continue
                if isinstance(target_str, str):
                    target_str = [target_str]
                
                for ts in target_str:
                    if pat.pat_dict['direct_map']:
                        match_ret = self.direct_map(arg, ts, pat, target)

                    match_ret = self.match_sent(arg, ts, pat, target)
                    if not match_ret:
                        continue
                    
                    nval = match_ret[target]['nval']

                    for t in match_ret:
                        if len(match_ret[t]['nval'])>0:
                            self.set_c(arg, t, match_ret[t]['nval'], match_ret[t]['ow'], append, pat, match_ret[t]['p_matched'])

    
    def map_doc_dtype(self, pat, stop=True):
        self.parse_descp(pat, stop, cat='doc_dtype')

    
    def post_process(self):
        def _remove_deprecated(arg):
            if arg in self.info['inputs']['required']:
                self.info['inputs']['required'].remove(arg)
            elif arg in self.info['inputs']['optional']:
                self.info['inputs']['optional'].remove(arg)
            else:
                print('Warning: deprecated arg %s not found. '% arg)

            # add into deprecated list
            if not self.info['inputs'].get('deprecated', []):
                self.info['inputs']['deprecated'] = []
            if arg not in self.info['inputs']['deprecated']:
                self.info['inputs']['deprecated'].append(arg)

        # remove deprecated variables from input list
        for da in self.info['inputs'].get('deprecated', []):
            _remove_deprecated(da)

        for arg in self.info['constraints']:
            if 'deprecated' in self.info['constraints'][arg].get('dtype', []):
                _remove_deprecated(arg)
            
            if 'scalar' in self.info['constraints'][arg].get('dtype', []):
                if 'scalar' not in str(self.info['constraints'][arg].get('structure', [])):
                    self.info['constraints'][arg]['dtype'].remove('scalar')
                    self.set_c(arg, 'ndim', str(0), True, True, None, None)
                    self.set_c(arg, 'dtype', 'numeric', False, False, None, None)

            if len(self.info['constraints'][arg].get('dtype', [])) == 1 and \
                    'enum' not in self.info['constraints'][arg]:

                if 'string' in str(self.info['constraints'][arg]['dtype']) or \
                    'bool' in str(self.info['constraints'][arg]['dtype']):
                    self.info['constraints'][arg].pop('shape', None)
                    # self.info['constraints'][arg].pop('ndim', None)
                    self.info['constraints'][arg].pop('range', None)
                    #if not self.info['constraints'][arg].get('structure', []):
                    # self.info['constraints'][arg]['ndim'] = ['0']
                    self.info['constraints'][arg].pop('structure', None)
                    self.info['constraints'][arg]['ndim'] = ['0']
                

            if 'shape' in self.info['constraints'][arg].get('dtype', []):
                self.info['constraints'][arg]['dtype'].remove('shape')
                self.set_c(arg, 'ndim', str(1), True, True, None, None)
                self.set_c(arg, 'dtype', 'int', True, True, None, None)
                self.set_c(arg, 'range', '[0,inf)', False, False, None, None)
                #self.set_c(arg, 'structure', 'tuple(int)', False, False, None, None)

            if 'image' in self.info['constraints'][arg].get('dtype', []):
                self.info['constraints'][arg]['dtype'].remove('image')
                self.set_c(arg, 'dtype', 'numeric', True, True, None, None)


            if 'callable' in self.info['constraints'][arg].get('dtype', []):
                self.info['constraints'][arg].pop('shape', None)
                self.info['constraints'][arg].pop('range', None)
                self.info['constraints'][arg].pop('dtype', None)
                
                if 'callable' in str(self.info['constraints'][arg].get('structure', [])):
                    new_struc = []

                    for struc in self.info['constraints'][arg].get('structure', []):
                        if 'callable' not in str(struc):
                            new_struc.append(struc)
                        else:
                            new_struc.append(struc.replace('(callable)', ''))
                    self.info['constraints'][arg]['structure'] = list(set(new_struc))
                    #         self.info['constraints'][arg]['structure'].remove(struc)

                else:
                    self.info['constraints'][arg].pop('structure', None)
                    self.info['constraints'][arg].pop('ndim', None)
                    self.info['constraints'][arg].pop('tensor_t', None)
            if 'enum' in self.info['constraints'][arg]:
                self.info['constraints'][arg].pop('shape', None)
                self.info['constraints'][arg].pop('ndim', None)
                self.info['constraints'][arg].pop('range', None)
                self.info['constraints'][arg].pop('dtype', None)
                self.info['constraints'][arg].pop('tensor_t', None)
                self.info['constraints'][arg].pop('structure', None)


            if not self.info['constraints'][arg].get('dtype', []):
                self.info['constraints'][arg].pop('dtype', None)
                # self.info['constraints'][arg]['dtype'].remove('callable')
                
                    
                        



                

            




    def refine_required_optional(self, refine_inputs):
        def _update(arg, dest, remove_from):
            if arg in self.info['inputs'].get('deprecated', []):
                return
            if arg in self.info['inputs'][dest]:
                return
            else:
                # in the wrong list
                self.info['inputs'][remove_from].remove(arg)
                self.info['inputs'][dest].append(arg)


        for arg in self.info['constraints']:
            for dd in self.info['constraints'][arg].get('doc_dtype', []):
                for p in refine_inputs.pat_dict['pat']:
                    if re.search(p, dd.lower()):
                        _update(arg, refine_inputs.pat_dict['pat'][p]['dest'], refine_inputs.pat_dict['pat'][p]['remove_from'])
            