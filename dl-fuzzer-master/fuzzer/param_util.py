import random
import numpy as np
import re
import string
import util
from util import MutationError
from constant import MAX_NUM_DIM, MAX_DIM, Param_Category, MAX_INT, MIN_INT

class Range:
    """
    a simple structure to record several attributes of a specified range
    """
    def __init__(self, raw, compat_dtype, lower_bound, upper_bound, lower_ound_dep,
                 upper_bound_dep, lower_bound_inclusive, upper_bound_inclusive, 
                 default_low=None, default_high=None):
        self.raw_rep = raw
        self.compat_dtype = compat_dtype  # rare case: when a range is only for a specific dtype
        self.lower_bound = lower_bound
        self.upper_bound = upper_bound
        self.lower_bound_dep = lower_ound_dep
        self.upper_bound_dep = upper_bound_dep
        self.lower_bound_inclusive = lower_bound_inclusive
        self.upper_bound_inclusive = upper_bound_inclusive

        self.default_low = default_low
        self.default_high = default_high
        
        self.dtype = None
        self.boundary = []

    def __repr__(self):
        return '{} {}'.format(self.__class__.__name__, self.raw_rep)

    def __str__(self):
        return self.raw_rep

    def is_default(self, side):
        if side=='low':
            return self.default_low == self.lower_bound
        elif side == 'high':
            return self.default_high == self.upper_bound
        else:
            util.error('invalid side %s' % side)
    
    def set_boundary(self, dtype):
        self.dtype = dtype
        self.boundary = []
        if not util.is_type_numeric(dtype):
            # if not numeric type
            return 
        
        low, high = self.lower_bound, self.upper_bound
        if 'int' in dtype:
            self.boundary = [int(low), int(high)]
        
        if 'float' in dtype:
            self.boundary = [float(low), float(high)]

        if 'complex' in dtype:
            self.boundary = [complex(low, low), complex(low, high), complex(high, high), complex(high, low)]

        self.boundary =  list(set(self.boundary))




class Mutator:
    def __init__(self, guided_mutate, special_value):
        self.guided_mutate = guided_mutate
        self.special_value = special_value

        self.funcdict = {
                'none': self._to_none,
                'zero': self._to_zero,
                'nan': self._to_nan,
                'inf': self._to_inf,
                'extreme': self._to_extreme,
                'empty_str': self._to_empty_str,
                # 'negative': self._to_negative,
                'zero_ndim': self._zero_ndim,
                'empty_list': self._empty_list,
                'element_zero': self._element_zero
            }

        self.boundary_op_map = {         
            Param_Category.NUM: ['zero', 'extreme'],
            Param_Category.STR: ['none', 'empty_str'],
            Param_Category.BOOL: ['none'],
            Param_Category.COMPLEX: ['none']
        }
        self.boundary_op_nd ={
            Param_Category.NUM: ['zero', 'extreme', 'zero_ndim', 'empty_list', 'element_zero'],
            Param_Category.STR: ['none', 'empty_str'],
            Param_Category.BOOL: ['none', 'zero_ndim', 'empty_list'],
            Param_Category.COMPLEX: ['none', 'zero_ndim', 'empty_list']
        }
        # self.additional_map_nd = ['zero_ndim', 'empty_list']
        self.coverage_record = self.init_coverage_record()  # record of mutation operation used
        self.mutator_choices = None
        self.mutation_op_covered = False
        self.zero_ndim_record = self.init_zero_ndim_coverage()  # record of ndim set to 0
        self.zero_ndim_covered = False

        self.obey = True
        self.dtype = None
        self.shape = None
        self.range = None
        self.data = None
        self.name = None
        self.category = None
        self.can_disobey_dtype = False
        self.can_disobey_ndim = False
        self.can_disobey_shape = False
        self.can_disobey_range = False
        self.can_disoeby_enum = False


    def init_coverage_record(self):
        coverage_record = {}
        for op in self.funcdict:
            coverage_record[op] = False
        # for param_cat in self.boundary_op_map:
        #     for op in self.boundary_op_map[param_cat]:
        #         coverage_record[op] = False
            
        # for op in self.additional_map_nd:
        #     coverage_record[op] = False
        return coverage_record
    

    def init_zero_ndim_coverage(self):
        ret = {}
        for n in range(MAX_NUM_DIM):
            ret[n] = False
        # ret['empty_list'] = False
        return ret

    def update_coverage(self, op, target_dim=None):
        if not self.zero_ndim_covered and op == 'zero_ndim':
            if target_dim not in self.zero_ndim_record:
                util.error('target dim %s is not valid' % target_dim)
            self.zero_ndim_record[target_dim] = True

            if not [x for x in self.zero_ndim_record if self.zero_ndim_record[x]==False]:
                util.DEBUG('Param %s has covered all dimension for zero_ndim op' % self.name)
                self.zero_ndim_covered = True
            

        if not self.mutation_op_covered:
            if op not in self.coverage_record:
                util.error('mutation op is not defined')
            self.coverage_record[op] = True

            if not self.zero_ndim_covered:
                self.coverage_record['zero_ndim'] = False   # zero_ndim is not completely covered

            if not [x for x in self.coverage_record if self.coverage_record[x]==False]:
                util.DEBUG('Param %s has covered all the mutation op' % self.name)
                self.mutation_op_covered = True

        

    def pick_mutation_op(self, max_coverage=True):
        def _init_mutator_choices():
            if len(self.shape) == 0:
                op_list = self.boundary_op_map[self.category]
            else:
                op_list = self.boundary_op_nd[self.category]


            if self.mutator_choices is not None:
                return
                
            self.mutator_choices = {}
            for op in op_list:
                self.mutator_choices[op] = True # true means not been tried    

        def _aval_mutator():
            # ret mutator that haven't been tried
            ret = []
            for op in self.mutator_choices:
                if self.mutator_choices[op]:
                    ret.append(op)
            return ret

        
        
        _init_mutator_choices()
        candidate_op = _aval_mutator()
        if not candidate_op:
            return None     # all available mutator have been tried and failed


        # all available op are covered
        if not max_coverage or self.mutation_op_covered or not [x for x in candidate_op if self.coverage_record[x]==False]:
            ret_op = random.choice(candidate_op)


        for op in candidate_op:
            if self.coverage_record[op]==False:
                ret_op=op
        
        self.mutator_choices[ret_op] = False
        return ret_op
        
    def _to_none(self, val):
        return None


   
    def _element_zero(self, val): 
        if self.can_disobey_range and self.obey:
            if self.range and 0<self.range.lower_bound or 0>self.range.upper_bound:
                raise MutationError('Need to follow constraint') 

        if re.search(r'^complex([0-9]*)', self.dtype):
            return complex(0,0)
        return 0

    def _to_zero(self, val):

        if len(self.shape)!=0 and self.can_disobey_ndim and self.obey:
            # if it is a multi-dimensional array AND with shape constraints AND need to obey constraints
            raise MutationError('Need to follow constraint') 
    
        return self._element_zero(val)



    def _to_nan(self, val):
        # special value
        if self.special_value:
            return np.nan
        else:
            raise MutationError('MutationError: No special value')
    
    def _to_inf(self, val):
        # special value
        if self.special_value:
            return random.choice([np.inf, -np.inf])
        else:
            raise MutationError('MutationError: No special value')
        
    def _to_extreme(self, val):
        if self.range:
            if self.range.boundary:
                return random.choice(self.range.boundary)
            else:
                raise MutationError('MutationError: [ATTENTION!] boundary for %s is empty ' % self.name)    
        else:
            raise MutationError('No range given, cannot mutate %s to extreme.' % self.name)    
        
    def _to_empty_str(self, val):
        return ''

    # def _to_negative(self, val):
    #     if self.range and self.range.lower_bound>=0:
    #         raise MutationError('MutationError: The parameter %s cannot be negative. ' % self.name)    # violate constraint
    #     if val<0:
    #         return val      # already a boundary case, don't mutate
    #     else:
    #         return 0-val


    def _zero_ndim(self, target_dim):
        # mutate one element in shape into 0
        # e.g. shape (1,2,3) -> shape (1,0,3)

        # if self.can_disobey_shape and self.obey:
        #     raise MutationError('Need to follow constraint')    
        
        s = list(self.shape)
        s[target_dim] = 0
        return np.ndarray(shape=s, dtype=self.dtype)

    def _empty_list(self, val):
        if self.can_disobey_ndim and self.obey:
            raise MutationError('Need to follow constraint')    
            
        return []



    def pick_target_dim(self):
        if len(self.shape)<2:
            raise MutationError('MutationError: to conduct zero_ndim, the parameter has to be at least 2D.') 
        
        if self.zero_ndim_covered:   # already covered all
            return  random.randint(0, len(self.shape)-1)
        
        for dim in [x for x in self.zero_ndim_record if self.zero_ndim_record[x]==False]:
            if dim <= len(self.shape)-1 :
                return dim

        # randint: both inclusive
        target_dim = random.randint(0, len(self.shape)-1)
        # print("Target dim is %s/%s" % (target_dim, self.shape))
        return target_dim 


    def pick_element_index(self, shape):
        # pick a index from multi-dimensional array
        index = []
        for dim in shape:
            if dim==0:          # 0 in shape, contain no elements
                return None     # already a boundary case, don't mutate
            index.append(random.randint(0, dim-1))      # [0, dim-1] inclusive
        return tuple(index)

    def assign_element(self, data, index, func):
        # assign element of "data" at "index" to be "func(val)"
        # index is a list
        if not index:       # index = []
            return data 
        # print('Debugging: '+str(data))
        # print(self.shape)
        if isinstance(data, str):   # the shape of string is random
            raise MutationError('String has invalid shape')    

        try:
            if len(index)==1:
                data[index[0]] = func(data[index[0]])
            else:
                data[tuple(index)] = func(data[tuple(index)])
        except:
            raise MutationError('Mutating failed.')    
        return data

    

    def gen_boundary_shape(self, shape, dtype):
        if len(self.shape)==0:
            return None
        
        if len(self.shape)==1:
            if not self.zero_ndim_record['empty_list']:
                return []
            else:
                return None

        # len(self.shape) >=2
        while True:
            candidate_dim = [d for d in self.zero_ndim_record if self.zero_ndim_record[d]==False]
            if not candidate_dim:
                return None
        
        target_dim = random.choice(candidate_dim)
        if target_dim=='empty_list':
            return self._empty_list
        else:
            self.shape = shape
            self.dtype = dtype
            return self._zero_ndim(target_dim = target_dim)


        

    def mutate(self, name, category, data, obey, dtype, shape, curr_range, can_disobey_ndim, can_disobey_dtype, \
            can_disobey_shape, can_disobey_range, can_disoeby_enum):
        self.name = name
        self.data = data
        self.obey = obey
        self.dtype = dtype
        self.shape = shape
        self.range = curr_range
        self.category = category
        self.can_disobey_dtype = can_disobey_dtype
        self.can_disobey_ndim = can_disobey_ndim
        self.can_disobey_shape = can_disobey_shape
        self.can_disobey_range = can_disobey_range
        self.can_disoeby_enum = can_disoeby_enum
        


        new_val=data
        stop=True # stop trying
        self.mutator_choices = None

        # try to max coverage only the first time to avoid inf loop
        boundary_op = self.pick_mutation_op(max_coverage=self.guided_mutate)
        assert (boundary_op is not None)

        
        while True:
            try: 
                if self.can_disoeby_enum and self.obey:
                    # don't do mutation
                    util.DEBUG('Need to follow constraint. Will not mutate enum value.')
                    return new_val

                if self.can_disobey_dtype and self.obey and self.category==Param_Category.BOOL:
                    util.DEBUG('Need to follow constraint. Will not mutate bool type')  
                    return new_val  


                target_dim = -1
                op_func = self.funcdict[boundary_op]
                # 0d case
                if len(shape) == 0 or self.category==Param_Category.STR:
                    new_val = op_func(data)
                    
                else:
            
                    if boundary_op == 'empty_list' or boundary_op=='zero':
                        new_val = op_func(data)
                    elif boundary_op == 'zero_ndim':
                        target_dim = self.pick_target_dim()
                        new_val = op_func(target_dim)
                    else:
                        target_element_index = self.pick_element_index(shape)
                        print('mutate element at index '+str(target_element_index))
                        new_val = self.assign_element(data, target_element_index, op_func)

                # success
                # update coverage info
                self.update_coverage(boundary_op, target_dim)
                break

            except (TypeError, ValueError, OverflowError, MutationError) as e:
                # TypeError: np.array cannot contain None .
                # ValueError: cannot convert nan to int/uint
                # OverflowError: cannot convert inf to int/uint
                # MutationError: (defined in util.py) cannot conduct mutation 
                #   - boundary case out of the range constraint
                #   - cannot conduct zero_ndim on 0D/1D tensor
                util.DEBUG('Failed to mutate parameter {}.\nError Message: {}\nDtype: {}; Shape: {}; Category: {}; Operation: {}.'\
                    .format(name, e, dtype, shape, self.category, boundary_op))

                # if fail, random pick op
                boundary_op = self.pick_mutation_op(max_coverage=False)
                if not boundary_op:
                    util.DEBUG('No mutator avaliable.')
                    return new_val
                else:
                    util.DEBUG('Try mutate again.')
            
                
            
        if len(shape)==0:
            util.DEBUG('Mutate parameter {} from {} to {}.\nDtype: {}; Type: {}; Shape: {}; Category: {}; Operation: {}.'\
                        .format(name, data, new_val, dtype, type(data), shape, self.category, boundary_op))
        else:
            util.DEBUG('Mutate parameter {}. Dtype: {}; Type: {}; Shape: {}; Category: {}; Operation: {}.'\
                        .format(name, dtype, type(data), shape, self.category, boundary_op))

        return new_val