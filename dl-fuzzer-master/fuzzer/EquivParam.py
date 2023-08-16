import cmath
import re
import string
import sys
import random

import numpy as np

import util
from util import MutationError
from constant import MAX_NUM_DIM, MAX_DIM, Param_Category, MAX_INT, MIN_INT
from errors import FuzzerError
from param_util import Range, Mutator

class Param:
    """ parameter class to store the information about each input parameter
    """
    shape_var = {}  # NOTE: this var needs to be rest every generation iteration

    @staticmethod
    def reset_shape_var():
        # reset shape_var (this is called by the fuzzer)
        Param.shape_var = {}
        return

    def __init__(self, name, spec, dtype_map, required=True, guided_mutate=False, special_value=False):
        # flags
        self.can_disobey_dtype = False
        self.can_disobey_ndim = False
        self.can_disobey_shape = False
        self.can_disobey_range = False
        self.can_disoeby_enum = False
        self.can_disobey = False  # will logical OR all can_disobey_*
        self.shape_dep = False
        self.range_dep = False

        self.default = None
        self.data = None
        self.valid_dtypes = None
        self.valid_ndims = None
        self.valid_ranges = None

        self.pick_ndim = None
        self.pick_dtype = None

        self.shape_spec = None
        self.tensor_t = None
        self.range_choices = []
        self.choices = []
        self.dep_param = {}
        self.var_dep = set()
        self.const_dep = set()

        self.name = name
        self.required = required
        #self.mutate_p = mutate_p  # the probability to mutate this param to one of the boundary cases
        self.guided_mutate = guided_mutate
        self.special_value = special_value
        self.category = None      # one of Param_Category
        self.curr_range = None      # current range choice, should be a Range object

        self.spec = spec  # NOTE: potentially be None
        self._process_spec(dtype_map)
        self.can_disobey = self.can_disobey_ndim or self.can_disobey_dtype or \
            self.can_disobey_shape or self.can_disobey_range or self.can_disoeby_enum

        self.mutator = Mutator(self.guided_mutate, self.special_value)
        # if self.choices:
        #     self.can_disobey = False
        return

    def __repr__(self):
        return '{} {}'.format(self.__class__.__name__, self.name)

    def _process_spec(self, dtype_map):
        if not self.spec:
            return
        # spec exists
        self._parse_ndims()
        self._parse_shape()
        self._parse_range()
        self._parse_enum()
        self._parse_dtype(dtype_map)
        self._parse_tensor_t()

        # optional param
        if not self.required:
            assert 'default' in self.spec
            self.default = str(self.spec['default'])
        return

    def _parse_tensor_t(self):
        self.tensor_t = self.spec.get('tensor_t')
        if self.tensor_t is not None and not isinstance(self.tensor_t, list):
            util.error('invalid format %s for "tensor_t"' % self.spec.get('tensor_t'))

    def _parse_dtype(self, dtype_map):
        if 'dtype' not in self.spec:
            # NOTE: when this happens, no way to dis-obey constraints
            self.valid_dtypes = None  # None here, so leave the job to the fuzzer to pass the default list to generator
            return

        self.can_disobey_dtype = True
        valid_dtypes = self._verify_dtypes(dtype_map)
        self.valid_dtypes = valid_dtypes

    def process_shape_dep(self, shape_spec):
        if not shape_spec or shape_spec[0] == '[' and shape_spec[-1] == ']':
            shape_spec = shape_spec[1:-1]  # remove '[]'
        shape_spec = shape_spec.replace(' ', '')  # remove space
        shape_toks = re.split(',|\+|-|\*|/', shape_spec)

        const_dep, var_dep = self.process_shape_toks(shape_toks)
        return var_dep, const_dep

    def process_shape_toks(self, shape_toks):
        var_dep = []
        const_dep = []

        for tok in shape_toks:
            if not tok:
                util.error('invalid shape spec %s' % tok)
            if tok.isnumeric():  # do nothing
                continue
            elif util.is_float(tok):  # maybe a non-integral numeric value
                util.error('"shape" value cannot be a float number "%s"' % tok)
            elif tok[0] == '>' or tok[0] == '<':  # implicitly 1D
                ref, is_var = util.gobble_unequal_sign(tok)
            elif tok[0] == '&':  # depends on another var and that var has to be 0D int
                ref, is_var = tok[1:], True
            elif tok[0] == '.':  # uncertain number of dimensions
                continue
            elif 'len:' in tok:
                _, ref, is_var = util.gobble_var_dep(tok, 'len:')
                if not is_var:
                    util.error('expect "%s" in "len:xx" a variable, rather than a constant' % ref)
            elif 'ndim:' in tok:
                _, ref, is_var = util.gobble_var_dep(tok, 'ndim:')
                if not is_var:
                    util.error('expect "%s" in "ndim:xx" a variable, rather than a constant' % ref)
            elif 'max_value:' in tok:
                _, ref, is_var = util.gobble_var_dep(tok, 'max_value:')
                if not is_var:
                    util.error('expect "%s" in "max_value:xx" a variable, rather than a constant' % ref)
            elif 'shape:' in tok:
                _, ref, is_var = util.gobble_var_dep(tok, 'shape:')
                if not is_var:
                    util.error('expect "%s" in "shape:xx" a variable, rather than a constant' % ref)
            else:
                # referring to another constant value e.g. [batch_size,num_labels]
                _, ref, is_var = util.gobble_var_dep(tok)

            if ref is not None:
                if is_var:
                    var_dep.append(ref)
                else:
                    const_dep.append(ref)
        return const_dep, var_dep

    def _parse_shape(self):
        """
        only to parse the shape dependency in variables
        :return: a list of constants/variables this depends on
        """
        if 'shape' not in self.spec:
            return

        self.can_disobey_shape = True
        self.shape_spec = self.spec['shape']
        # shape constraint exists
        var_dep = []
        const_dep = []
        final_shape_spec_list = []
        for spec in self.shape_spec:
            try:
                var_dep_part, const_dep_part = self.process_shape_dep(spec)
            except FuzzerError:
                util.warning('shape spec %s is not understandable, skipping' % spec)
                continue
            final_shape_spec_list.append(spec)
            var_dep += var_dep_part
            const_dep += const_dep_part

        self.shape_spec = final_shape_spec_list
        self.var_dep.update(set(var_dep))
        self.const_dep.update(set(const_dep))
        return

    def _parse_enum(self):
        if 'enum' in self.spec:
            self.can_disoeby_enum = True
            self.choices = self.spec['enum']
        return

    def _parse_range(self):
        if 'range' not in self.spec:
            return

        self.can_disobey_range = True
        range_str_list = self.spec['range']
        assert isinstance(range_str_list, list)

        range_spec_list = []
        for range_str in range_str_list:
            for_dtype = 'all'
            if ':' in range_str and 'ndim:' not in range_str and 'len:' not in range_str and \
                    'dtype:' not in range_str and 'max_value:' not in range_str:  # special form, e.g., int:[0, inf)
                for_dtype = range_str.split(':')[0]
                range_str = range_str.split(':')[1]
            range_spec_list.append(self._process_range_str(for_dtype, range_str))

        # self.mutator.

        self.range_choices = range_spec_list

    def _process_range_str(self, for_dtype, range_str):
        if range_str[0] not in '([' or range_str[-1] not in'])':
            util.error('invalid range spec "%s" for param "%s"' % (range_str, self.name))

        lower_bound_inclusive = True if range_str[0] == '[' else False
        # starting from index 1, get the lower bound string
        lower_bound_str, next_start_idx = util.gobble_until(1, range_str, ',')
        lower_bound_value, lower_bound_dep = self._process_bound_str(lower_bound_str)

        upper_bound_inclusive = True if range_str[-1] == ']' else False
        # starting from the next_start_idx, get the upper bound string
        upper_bound_str, _ = util.gobble_until(next_start_idx, range_str, ')]')
        upper_bound_value, upper_bound_dep = self._process_bound_str(upper_bound_str)

        if lower_bound_value is not None and upper_bound_value is not None and lower_bound_value > upper_bound_value:
            print('Error: upper bound should be greater than the lower bound: %s' % range_str)
            exit(1)

        # bound value can be none
        return Range(range_str, for_dtype, lower_bound_value, upper_bound_value, lower_bound_dep, upper_bound_dep,
                     lower_bound_inclusive, upper_bound_inclusive)

    def _process_bound_str(self, bound_str):
        if not util.str_is_number(bound_str):
            operands = self._find_dependency(bound_str)
            for o in operands:
                if o == '' or util.str_is_number(o):
                    continue
                elif o[0] == '&':
                    self.var_dep.add(o[1:])
                else:
                    self.const_dep.add(o)
            bound_value = None
            bound_dep = bound_str
        else:
            bound_value = util.convert_to_num(bound_str)
            bound_dep = None
        return bound_value, bound_dep

    def _find_dependency(self, s):
        """
        this function tries to figure out the dependencies and returns a list of operands
        :param s: given string expression (should only contain +-*/ and the special operations such as ndim:
        :return: a list of operands (e.g., -ndim:&a+1 will return ['', '&a', '1']
        """
        operators = {'+', '-', '*', '/'}
        sp_operators = {'ndim:', 'len:', 'max_value:', 'dtype:'}

        operands = []
        str_buff = ''
        for c in s:
            if c in operators:
                operands.append(str_buff)  # NOTE: could be ''
                str_buff = ''
            else:
                str_buff += c
                if str_buff in sp_operators:
                    str_buff = ''
        operands.append(str_buff)
        return operands

    def _parse_ndims(self):
        def get_num_after(ndim_str, idx):
            num = ndim_str[idx+1:]
            num = util.convert_to_num(num)  # TODO: will throw error when there's shape dependency like '>=ndim:&x'
            check_ndim(num)
            return num

        def check_ndim(ndim):
            if ndim > MAX_DIM:
                print('Error: given "ndim" %d is too large; may cause memory error' % ndim)
                exit(1)

        if 'ndim' not in self.spec:  # NOTE: when this happens, no way to dis-obey constraints
            self.valid_ndims = []  # leave it to the fuzzer to pass the default list to generator
            return

        self.can_disobey_ndim = True

        # NOTE: store ndim in str form to be consistent
        valid_ndims = set()
        ndim_spec = self.spec['ndim']
        if not isinstance(ndim_spec, list):
            util.error('"ndim" spec should be a list')
        for ndim_str in self.spec['ndim']:
            if not isinstance(ndim_str, str):
                ndim_str = str(ndim_str)  # possible to have int/float, convert to str for consistency

            if ndim_str == '?':
                continue

            if ndim_str.isnumeric():
                valid_ndims.add(ndim_str)
                continue

            if util.is_float(ndim_str):  # maybe a non-integral numeric value
                util.error('"ndim" cannot be a float number "%s"' % ndim_str)

            ge_idx = ndim_str.find('>=')
            if ge_idx != -1:
                min_ndim = get_num_after(ndim_str, ge_idx + 1)
                valid_ndims.update(map(str, np.arange(min_ndim, MAX_NUM_DIM+1)))
                continue

            gt_idx = ndim_str.find('>')
            if gt_idx != -1:
                min_ndim = get_num_after(ndim_str, gt_idx) + 1
                valid_ndims.update(map(str, np.arange(min_ndim, MAX_NUM_DIM+1)))
                continue

            le_idx = ndim_str.find('<=')
            if le_idx != -1:
                max_ndim = get_num_after(ndim_str, le_idx + 1)
                valid_ndims.update(map(str, np.arange(0, max_ndim+1)))
                continue

            lt_idx = ndim_str.find('<')
            if lt_idx != -1:
                max_ndim = get_num_after(ndim_str, lt_idx) - 1
                valid_ndims.update(map(str, np.arange(0, max_ndim+1)))
                continue

            if 'ndim:' in ndim_str:
                _, ref, is_var = util.gobble_var_dep(ndim_str, 'ndim:')
                if not is_var:
                    util.error('expect "%s" in "ndim:xx" a variable, rather than a constant' % ref)
                self.var_dep.add(ref)
                valid_ndims.add(ndim_str)
                continue

            # likely a constant
            _, ref, is_var = util.gobble_var_dep(ndim_str)
            if is_var:
                self.var_dep.add(ref)
            else:
                self.const_dep.add(ref)
                valid_ndims.add(ndim_str)
        self.valid_ndims = list(valid_ndims)
        return

    def _verify_dtypes(self, dtype_map):
        default_dtypes = [k for k, v in dtype_map.items() if v is not None]
        # in case the specified dtype is just `int` or `float`
        special_numeric_dtypes = ['int', 'float']

        dtype_spec = self.spec.get('dtype')
        if dtype_spec is None:
            util.warning('dtype spec is None; using the default dtype list')
            return default_dtypes
        if not isinstance(dtype_spec, list):
            util.error('expect dtype spec to be a list; got %s.' % type(dtype_spec))

        # the given dtypes should only contain recognizable dtype
        known_dtypes = [dtype for dtype in dtype_spec if dtype in dtype_map]
        rest_dtypes = set(self.spec['dtype']) - set(known_dtypes)
        special_dtypes = [dtype for dtype in rest_dtypes if dtype.lower() in special_numeric_dtypes]

        # the dtype of a variable could be `dtype`
        special_dtypes += [dtype for dtype in rest_dtypes if 'dtype' in dtype and ':' not in dtype]  # TODO: outdated parsing here

        # tensorshape
        special_dtypes += [dtype for dtype in rest_dtypes if dtype.lower() == 'tensorshape']

        # scalar
        special_dtypes += [dtype for dtype in rest_dtypes if dtype.lower() == 'scalar']

        # numeric
        special_dtypes += [dtype for dtype in rest_dtypes if dtype.lower() == 'numeric']

        # dtype dependency
        dtype_dep_list = [dtype for dtype in rest_dtypes if 'dtype:' in dtype]

        def set_dep(dtype_str):
            _, ref, is_var = util.gobble_var_dep(dtype_str, 'dtype:')
            if not is_var:
                util.error('expect "%s" in "dtype:xx" a variable, rather than a constant' % ref)
            self.var_dep.add(ref)

        for dtype_dep in dtype_dep_list:
            set_dep(dtype_dep)
            known_dtypes.append(dtype_dep)  # delay the specific processing of dtype_dep until generation time

        rest_dtypes = rest_dtypes - set(special_dtypes) - set(known_dtypes)
        if rest_dtypes:
            util.warning('unknown dtype(s): %s' % str(rest_dtypes))
        if not known_dtypes and not special_dtypes:
            util.warning('the given dtypes for \'%s\' are all unrecognizable; use the default dtypes' % self.name)
            self.can_disobey_dtype = False
            return default_dtypes
        dtype_list = []
        for dtype in special_dtypes:
            if dtype.lower() == 'int':
                dtype_list += util.pick_integer(default_dtypes)
            elif dtype.lower() == 'float':
                dtype_list += util.pick_float(default_dtypes)
            elif 'dtype' in dtype.lower():
                dtype_list.append('dtype')
            elif 'tensorshape' == dtype.lower():
                dtype_list += util.pick_integer(default_dtypes, unsigned=True)
                self.valid_ndims = ['1']
            elif 'scalar' == dtype.lower():
                dtype_list += util.pick_scalar(default_dtypes)
                # only allow 0D for 'scalar' type
                self.valid_ndims = ['0']
            elif 'numeric' == dtype.lower():
                dtype_list += util.pick_scalar(default_dtypes)
            else:
                print('special handling for %s is not implemented yet' % dtype)
                raise NotImplementedError

        dtype_list += known_dtypes

        # remove the duplicates
        dtype_list = list(set(dtype_list))
        return dtype_list

    def can_disobey_cat(self):
        assert self.can_disobey, 'Fuzzer Bug: selected a parameter that cannot violate constraints'
        categories = []
        if self.can_disobey_shape or self.can_disobey_ndim:
            categories.append('ndim')
        if self.can_disobey_dtype:
            categories.append('dtype')
        if self.can_disobey_range:
            categories.append('range')
        if self.can_disoeby_enum:
            categories.append('enum')

        return categories

    def gen(self, obey, default_ndims, dtype_map, data_construct, chosen_np_dtype=None, p_mutate=False):
        """
        This is the generator function for each parameter
        :return: the generated parameter
        """

        def _call_mutate(data, dtype, shape, obey):
            self.category = self.set_category(dtype)  # set param category
            if p_mutate:             # forcing boundary case
                data = self.mutator.mutate(self.name, self.category, data, obey, dtype, shape, self.curr_range, self.can_disobey_ndim, self.can_disobey_dtype, \
            self.can_disobey_shape, self.can_disobey_range, self.can_disoeby_enum)
                #data = self.mutate(data, dtype, shape)
            return data

        # reset self.pick_dtype & self.pick_ndim
        self.pick_dtype = None
        self.pick_ndim = None

        # if eo: pick dtype, ndim
        # if ee, pick one or several constraint to disobey 
        pick_dtype, pick_ndim, range_obey, enum_obey = self._pick_dtype_ndim(obey, default_ndims, dtype_map, chosen_np_dtype)
        #print('picked ndim for %s is %s. Defualts: %s' % (self.name, pick_ndim, str(default_ndims)))
       
        if self.choices:  
            # enumeratation type
            # no need to generate new value & same for both obey and disobey
            data = np.random.choice(self.choices)  # in string, need cast
            to_type = util.infer_type_from_str(data)
            
            if not enum_obey:
                data = self._gen_violate_enum(data, to_type, self.choices)

            self.data = util.try_cast(data, to_type)
            self.data = _call_mutate(data, to_type, shape=(), obey=enum_obey)
            return self.data


        if pick_dtype is None or pick_ndim is None:  # value should be None
            return None

        if len(pick_dtype.split('.')) > 1:
            pick_dtype = pick_dtype.split('.')[1]  # eg. only take the `float32` of the `np.float32`

        # after setting the dtype and ndim, generate the concrete values
        gen_shape = self._gen_shape_from_ndim(obey, pick_ndim)
        pick_ndim = util.check_shape_validity(gen_shape)  # make `pick_ndim` and `gen_shape` consistent

        # TODO: generate boundary case based on the shape

        try:
            data = self.gen_var_from_shape(gen_shape, pick_dtype, dtype_map, range_obey=range_obey)
        except (MemoryError, ValueError) as e :     
            # util.DEBUG('Error (%s) occurred when generating new value. Try again.'% str(e))
            raise FuzzerError('Error (%s) occurred when generating new value. Try again.'% str(e))
        


        self.data = _call_mutate(data, pick_dtype, gen_shape, obey)

        self.data, convert_tensor = self.convert_structure(self.data, pick_ndim)
        
        # if data_construct is not None and convert_tensor and pick_ndim==1:
        if data_construct is not None and convert_tensor: 
            self.data = self.convert_to_tensor(self.data, data_construct)
        #self.data = data
        self.pick_dtype = pick_dtype
        self.pick_ndim = pick_ndim

        return self.data        

    def convert_to_tensor(self, data, data_construct):
        # if data is None or isinstance(data, (str, int, float)):
        #     return data
        assert self.tensor_t is None or isinstance(self.tensor_t, list), 'tensor_t needs to be either None or a list'

        # there exist constraint, only call data_construct when tensor_t presents
        # if the generated data is ndarray, better to convert
        if self.tensor_t or isinstance(data, np.ndarray):
            data = data_construct(data)
        return data

    def convert_structure(self, data, pick_ndim):
        if self.spec is None:  # no constraint
            return data, True
        structure_spec = self.spec.get('structure')
        if structure_spec is None or pick_ndim != 1 or isinstance(data, str):
            # only convert the data if pick_ndim is 1
            # this is because we currently only support structure like list/tuple
            # also, won't convert a string to list/tuple
            return data, True

        assert(pick_ndim==1)
        assert isinstance(structure_spec, list)
        for each_spec in structure_spec:
            if 'list' in each_spec and util.is_iterable(data):  # we simply convert the given data to a list
                return list(data), False
            elif 'tuple' in each_spec and util.is_iterable(data):
                return tuple(data), False  # simply convert the given data to a tuple
        return data, True

    def add_dep_param_obj(self, param_obj):
        self.dep_param[param_obj.name] = param_obj

    def mark_shape_dep(self):
        # mark to know there's at least one var's shape depends on this
        self.shape_dep = True
        for rg in self.range_choices:
            rg.lower_bound = 0
            rg.upper_bound = MAX_DIM

    def _decide_from_default(self, pick_dtype, pick_ndim):
        """
        This function looks at the default value and decide whether the picked dtype & ndim make sense.
        If the dtype & ndim has inconsistency between the picked and the default,
        this function tries to resolve the inconsistency
        NOTE: when pick_dtype and pick_ndim got override, the info displayed during permutation would be inconsistent
        :param pick_dtype: the picked dtype from constraint info
        :param pick_ndim: the picked ndim from constraint info
        :return: (pick_dtype, pick_ndim) modified from default value info or untouched
        """
        assert not self.required

        if self.default is None:  # corner case: no default value provided
            return pick_dtype, pick_ndim

        # the default value is None, nothing really we can learn
        if self.default == 'None':
            # either leave the picked dtype & ndim untouched or just use 'None' as the param value

            def decide_override():
                # when override or leave it untouched both make sense
                choice = np.random.binomial(1, 0.5)
                return True if choice == 1 else False

            if decide_override():
                return None, None  # TODO: this override confuses the display during permutation

        # return them untouched for now
        return pick_dtype, pick_ndim

    def _pick_dtype_ndim(self, obey, default_ndims, dtype_map, chosen_np_dtype):
        range_obey = True
        enum_obey = True

        if obey:
            pick_dtype = self._pick_obey_dtype(dtype_map, chosen_np_dtype)

            if 'str' in pick_dtype:  # NOTE: force string generation to be 0D
                # TODO: also for bool
                pick_ndim = 0
            else:
                pick_ndim = self._pick_obey_ndim(default_ndims)

            # if not self.required:  # optional parameter, default value exists
            #     # perhaps we can learn something from the default values
            #     pick_dtype, pick_ndim = self._decide_from_default(pick_dtype, pick_ndim)
            

        else:  # dis-obey the constraints
            # multiple potential options to violate the constraints, e.g., dtype, ndim/shape, structure, tensor_t
            # this function only handles dtype and ndim
            constraint_cat = ['dtype', 'ndim', 'range', 'enum']
            can_disobey_cat = self.can_disobey_cat()
            num_cats_to_disobey = np.random.randint(len(can_disobey_cat)) + 1
            cats_to_disobey = list(np.random.choice(can_disobey_cat, num_cats_to_disobey, replace=False))
            cats_to_obey = list(set(constraint_cat) - set(cats_to_disobey))

            
            while cats_to_disobey:
                c = cats_to_disobey.pop()
                if c == 'dtype':
                    pick_dtype = self._pick_disobey_dtype(dtype_map)
                elif c == 'ndim':
                    pick_ndim = self._pick_disobey_ndim(default_ndims)
                elif c == 'range':
                    range_obey = False
                elif c=='enum':
                    enum_obey = False
                else:
                    raise NotImplementedError('unknown constraint category %s to dis-obey' % c)

            while cats_to_obey:
                c = cats_to_obey.pop()
                if c == 'dtype':
                    pick_dtype = self._pick_obey_dtype(dtype_map, None)
                elif c == 'ndim':
                    pick_ndim = self._pick_obey_ndim(default_ndims)

        if pick_dtype in dtype_map:  # TODO: this check is bc inconsistent dtype representation from obey and dis-obey
            pick_dtype = dtype_map[pick_dtype]
            
        return pick_dtype, pick_ndim, range_obey, enum_obey

    def get_dtype_dep(self, dtype_str): 
        # TODO: the string matching below is specific to MXNet which returns in form of `<class 'numpy.float32'>`
        m = re.search('^<class \'(.*)\'>', dtype_str)
        if m:  # to make it consistent with the other 2 libraries, only take `numpy.float32`
            dtype_str = m.group(1)

        if 'dtype:' in dtype_str:
            # depends on another param
            _, ref, is_var = util.gobble_var_dep(dtype_str, 'dtype:')
            assert is_var
            dtype = self._gen_value_from_var_dep(ref, 'dtype', False)
        else:
            dtype = dtype_str
        return dtype

    def _pick_obey_dtype(self, dtype_map, chosen_np_dtype):
        def process_picked_dtype(dtype_str):
            pick_dtype = self.get_dtype_dep(dtype_str)
            pick_dtype = self.get_package_dtype_name(pick_dtype, dtype_map)
            assert pick_dtype is not None
            return pick_dtype

        if chosen_np_dtype:
            return process_picked_dtype(chosen_np_dtype)

        default_dtypes = [k for k, v in dtype_map.items() if v is not None]
        # retry_times = 10
        # while True:  # ensure the picked dtype has a numpy correspondence
        if self.valid_dtypes:  # constraints for dtype exist
            pick_dtype = np.random.choice(self.valid_dtypes)
        else:  # constraint doesn't exist for dtype
            pick_dtype = np.random.choice(default_dtypes)

        return process_picked_dtype(pick_dtype)

    def check_dtype_dep(self, valid_dtypes):
        for t in valid_dtypes:
            if 'dtype:&' in t:
                return self.get_dtype_dep(t)
        return None

    def take_out_dtype_from(self, from_list, target):
        return [t for t in from_list if target not in t]

    def _pick_disobey_dtype(self, dtype_map):

        def get_dtype_nbit(dtype_str):
            # give int32, return (int, 32)
            pat = r'(int|float|uint|complex)([0-9]*)'
            m = re.search(pat, dtype_str)
            if m: 
                dtype = m.group(1)
                try:
                    nbit = int(m.group(2))
                except:
                    nbit= 0           
                return dtype, nbit

            return None, None

        def check_disobey(pick_dtype, valid_dtypes):
            # if int32 is a valid dtype, int16 is not a violation
            pick_type, pick_nbit = get_dtype_nbit(pick_dtype)

            if not pick_type:
                return True
            
            for vd in valid_dtypes:
                vd_type, vd_nbit = get_dtype_nbit(vd) 
                if not vd_type:
                    continue
                if vd_type == pick_type and vd_nbit >= pick_nbit:
                    return False
            
            return True


        util.DEBUG('trying to violate dtype constraint for %s' % self.name)
        default_dtypes = [k for k, v in dtype_map.items() if v is not None]
        while True:
            if self.can_disobey_dtype:
                if self.valid_dtypes == default_dtypes:
                    print('Warning: valid dtype == default dtypes; NO way to dis-obey the dtype constraint')
                    pick_dtype = np.random.choice(self.valid_dtypes)
                else:
                    dtype_dep = self.check_dtype_dep(self.valid_dtypes)
                    if dtype_dep is None:  # no dtype dependency
                        pick_dtype = np.random.choice(list(set(default_dtypes) - set(self.valid_dtypes)))
                        util.DEBUG('selected %s to violate dtype constraint' % pick_dtype)
                    else:
                        dtype_choices = self.take_out_dtype_from(default_dtypes, dtype_dep)
                        if not dtype_choices:
                            util.error('unable to violate dtype constraint')
                        pick_dtype = np.random.choice(dtype_choices)
                        util.DEBUG('selected %s to differ from dtype dep %s' % (pick_dtype, dtype_dep))
            else:
                util.DEBUG('no way to violate dtype constraint; selecting from default')
                pick_dtype = np.random.choice(default_dtypes)

            if pick_dtype in dtype_map and check_disobey(pick_dtype, self.valid_dtypes):
                return dtype_map[pick_dtype]

    def _pick_obey_ndim(self, default_ndims):
        if self.valid_ndims:
            pick_ndim = np.random.choice(self.valid_ndims)
            if pick_ndim.isnumeric():
                return int(pick_ndim)
            # there's some dependency
            if 'ndim:' in pick_ndim:
                _, ref, is_var = util.gobble_var_dep(pick_ndim, 'ndim:')
                if is_var:
                    pick_ndim = self._gen_value_from_var_dep(ref, 'ndim')
                    return pick_ndim
                else:
                    print('Error: expect "xxx" in "ndim(xxx)" a variable, rather than a constant')
                    exit(1)
            # depends on a constant
            _, ref, is_var = util.gobble_var_dep(pick_ndim, '')
            if is_var:
                return self._gen_value_from_var_dep(ref, 'eval')
            else:
                if not Param.shape_var or ref not in Param.shape_var or Param.shape_var[ref] is None:
                    # constraint file doesn't have 'shape_var' attribute OR
                    # constraint file doesn't have referred constant ref in 'shape_var' attribute OR
                    # the concrete value for ref is not initialized yet
                    Param.shape_var[ref] = np.random.randint(MAX_NUM_DIM + 1)
                return Param.shape_var[ref]
        else:
            pick_ndim = np.random.choice(default_ndims)
        return pick_ndim

    def _pick_disobey_ndim(self, default_ndims):
        util.DEBUG('trying to violate ndim constraint for %s' % self.name)
        if self.can_disobey_ndim:
            if self.valid_ndims == default_ndims:
                print('Warning: valid ndims == default ndims; NO way to dis-obey the ndim constraint')
                pick_ndim = np.random.choice(self.valid_ndims)
            else:
                default_ndims = [str(ndim) for ndim in default_ndims]  # convert to string to be consistent with self.valid_ndims
                pick_ndim = np.random.choice(list(set(default_ndims) - set(self.valid_ndims)))
                pick_ndim = int(pick_ndim)  # convert to int
                util.DEBUG('selected %d as ndim to violate constraint' % pick_ndim)
        else:
            util.DEBUG('no way to violate ndim constraint; selecting from default')
            pick_ndim = np.random.choice(default_ndims)
        return pick_ndim

    def _gen_value_from_var_dep(self, ref, relation, gen_shape=True):
        assert ref in self.dep_param
        dep_param_obj = self.dep_param[ref]
        if relation == 'dtype':
            try:
                return "%s" % dep_param_obj.data.dtype  # return the string form of dtype
            except AttributeError:
                return str(type(dep_param_obj.data)).split("'")[1]
        elif relation == 'len':
            try:
                return len(dep_param_obj.data)
            except TypeError:
                util.error('unable to get length of "%s"' % ref)
        elif relation == 'ndim':
            try:
                return dep_param_obj.data.ndim
            except AttributeError:
                # not an object with 'ndim' attribute, check if it's just 0D value
                pass

            try:
                _ = dep_param_obj.data / 1
                return 0  # just a 0D numerical value
            except TypeError:
                pass

            if dep_param_obj.pick_ndim is not None:
                return dep_param_obj.pick_ndim

            util.error('unable to get ndim of "%s"' % ref)
        elif relation == 'max_value':
            try:
                max_val = max(dep_param_obj.data)
                if gen_shape and not isinstance(max_val, (int, np.integer)):
                    print('Error: try to generate a shape value,'
                          ' but max value for "%s" with value %s is not an integer' % (ref, dep_param_obj.data))
                    raise TypeError
                return max_val
            except (TypeError, ValueError):
                util.error('unable to get max value for "%s" with value %s' % (ref, dep_param_obj.data))
        elif relation == 'min_value':
            try:
                min_val = min(dep_param_obj.data)
                if gen_shape and not isinstance(min_val, (int, np.integer)):
                    print('Error: try to generate a shape value,'
                          ' but min value for "%s" with value %s is not an integer' % (ref, dep_param_obj.data))
                    raise TypeError
                return min_val
            except (TypeError, ValueError):
                util.error('unable to get min value of "%s" with value %s' % (ref, dep_param_obj.data))
        elif relation == 'shape':
            try:
                shape = dep_param_obj.data.shape
                return shape
            except AttributeError:
                if isinstance(dep_param_obj, (int, float, complex, str)):
                    return []
                util.error('unable to get the shape for "%s" with value %s' % (ref, dep_param_obj.data))

        elif relation == 'eval':
            value = dep_param_obj.data
            # assumption here: for given '&a' that 'a' should be a number
            if isinstance(value, bool) or isinstance(value, np.bool_):
                util.error('referred value "%s" is a boolean value; cannot be used to decide another var' % ref)
            if not isinstance(value, (int, float)):
                util.error('referred value "%s" is not a single numeric value;'
                           'cannot be used to decide another var' % ref)
            return value
        else:
            util.error('unknown relation "%s"' % relation)

    def process_shape_tok_loop(self, tok, ndim):
        assert isinstance(tok, str)
        shape_value = 0
        sign = '+'
        while tok:  # process until tok is empty string
            tok, value = self.process_shape_tok(tok, ndim)
            if isinstance(value, tuple):  # the spec was "shape:&xxx"
                return value
            if value in '+-*/':
                sign = value
                continue
            elif value == '-1':
                return -1

            if not util.str_is_int(value):
                util.error('given shape value %s is invalid.' % value)
            value = int(value)
            # check for special values
            if sign == '+':
                shape_value += value
            elif sign == '-':
                assert shape_value > value
                shape_value -= value
            elif sign == '*':
                shape_value *= value
            else:  # sign is '/'
                if value == 0:
                    util.error('attempting to divide by 0')
                if shape_value % value != 0:
                    util.warning('%s/%s is not divisible, will use ceil(result) instead'
                                 % (str(shape_value), str(value)))
                    shape_value = int(shape_value / value) + 1
                else:
                    shape_value /= value
                    shape_value = int(shape_value)
        return shape_value

    def process_shape_tok(self, tok, ndim):
        if tok[0] in '+-*/':
            return tok[1:], tok[0]
        elif tok.isnumeric():
            return '', tok
        elif tok[0] == '>' or tok[0] == '<':  # implicitly 1D
            assert ndim == 1
            sign, shape_bound = util.parse_shape_bound(tok)
            if sign == '>':
                return '', str(np.random.randint(shape_bound + 1, MAX_DIM + 1))
            else:
                return '', str(np.random.randint(shape_bound - 1))
        elif tok[0] == '.':  # there's unknown number of dimensions
            return '', str(-1)  # put -1 as an indicator; need to call process_dot() later
        elif tok[0] == 'l' and 'len:' in tok:
            tok, ref, is_var = util.gobble_var_dep(tok, 'len:')
            if is_var:
                return tok, str(self._gen_value_from_var_dep(ref, 'len'))
            else:
                print('Error: expect "xxx" in "len(xxx)" a variable, rather than a constant')
                exit(1)
        elif tok[0] == 'n' and 'ndim:' in tok:
            tok, ref, is_var = util.gobble_var_dep(tok, 'ndim:')
            if is_var:
                return tok, str(self._gen_value_from_var_dep(ref, 'ndim'))
            else:
                print('Error: expect "xxx" in "ndim(xxx)" a variable, rather than a constant')
                exit(1)
        elif tok[0] == 'm' and 'max_value:' in tok:  # implicitly 1D
            tok, ref, is_var = util.gobble_var_dep(tok, 'max_value:')
            if is_var:
                return tok, str(self._gen_value_from_var_dep(ref, 'max_value'))
            else:
                print('Error: expect "xxx" in "max_value(xxx)" a variable, rather than a constant')
                exit(1)
        elif tok[0] == 's' and 'shape:' in tok:
            tok, ref, is_var = util.gobble_var_dep(tok, 'shape:')
            if is_var:
                return tok, tuple(self._gen_value_from_var_dep(ref, 'shape'))
            else:
                print('Error: expect "xxx" in "shape(xxx)" a variable, rather than a constant')
                exit(1)
        else:
            # referring to another var or constant value e.g. [batch_size,num_labels]
            tok, ref, is_var = util.gobble_var_dep(tok, '')
            if is_var:
                return tok, str(self._gen_value_from_var_dep(ref, 'eval'))
            else:
                if not Param.shape_var or ref not in Param.shape_var or Param.shape_var[ref] is None:
                    # constraint file doesn't have 'shape_var' attribute OR
                    # constraint file doesn't have referred constant ref in 'shape_var' attribute OR
                    # the concrete value for ref is not initialized yet
                    Param.shape_var[ref] = np.random.randint(MAX_DIM + 1)
                return tok, str(Param.shape_var[ref])

    def gen_shape_by_spec(self, shape_spec, ndim):
        # assumption: ndim and shape_spec are consistent
        # generate shape based on shape dependency
        if shape_spec[0] == '[' and shape_spec[-1] == ']':
            shape_spec = shape_spec[1:-1]  # remove '[]'
        shape_spec = shape_spec.replace(' ', '')  # remove space
        if shape_spec == '':  # shape spec was only '[]'
            return []
        shape_toks = shape_spec.split(',')

        shape = []

        for tok in shape_toks:
            value = self.process_shape_tok_loop(tok, ndim)
            if isinstance(value, tuple):
                return value
            shape.append(value)

        def process_dot(shape):
            new_shape = []
            shape_len = len(shape)
            for i in shape:
                if i == -1:
                    shape_len -= 1
                    max_dim_fill = MAX_NUM_DIM - shape_len
                    fill_size = np.random.randint(max_dim_fill)
                    shape_dim = np.random.randint(MAX_DIM + 1, size=fill_size)
                    new_shape += list(shape_dim)
                else:
                    new_shape.append(i)
            return new_shape

        # since -1 may exist in shape (due to '...'), process it
        shape = process_dot(shape)

        return shape

    def _gen_shape_from_ndim(self, obey, ndim):
        def choose_conform_shape_spec():
            for spec in self.shape_spec:
                if '...' in spec and len(spec.split(',')) <= ndim:
                    return spec
                if len(spec.split(',')) == ndim:
                    return spec
                if ':' in spec:  # there's param dependency, take higher priority than the chosen ndim
                    return spec
            return None

        if self.shape_spec:  # more explicit shape spec exists
            shape_spec = choose_conform_shape_spec()
            if shape_spec is not None and shape_spec != '':  # there is corresponding spec
                gen_shape = self.gen_shape_by_spec(shape_spec, ndim)
                if obey:
                    return gen_shape
                # disobey
                dim_from_shape = util.check_shape_validity(gen_shape)
                if dim_from_shape == ndim:  # want to disobey but the picked ndim unknowingly follows the constraint
                    ndim = ndim + 1 if ndim < MAX_NUM_DIM else ndim - 1
                    util.DEBUG('overruling selected ndim due to shape spec; selected ndim = %d' % ndim)
                # else the picked ndim is violating the constraint, proceed to generate shape

        # no corresponding shape spec, so just use ndim to generate info
        if ndim == 0:
            return tuple()  # an empty tuple for 0D
        elif ndim == 1:
            return tuple([np.random.randint(MAX_DIM+1)])
        elif ndim > 1:
            return tuple(np.random.randint(MAX_DIM+1, size=ndim))
        else:
            print('Error: Invalid Number of Dimension %d' % ndim)
            exit(1)

    def gen_var_from_shape(self, shape, np_dtype, dtype_map, range_obey=True):
        # int/uint
        m = re.search('^int([0-9]*)|^uint([0-9]*)', np_dtype)
        if m:
            self.curr_range = self._get_low_high_from_range(np_dtype, m.group(1), obey=range_obey)
            new_val = self._gen_int(np_dtype, shape)

        # float
        m = re.search('^float([0-9]*)', np_dtype)
        if m:
            self.curr_range = self._get_low_high_from_range(np_dtype, m.group(1), obey=range_obey)
            new_val = self._gen_float(np_dtype, shape)

        # complex
        m = re.search('^complex([0-9]*)', np_dtype)
        if m:
            n_bit = m.group(1)
            if n_bit.isnumeric():
                half_n_bit = str(int(int(n_bit) / 2))
            else:  # just complex
                half_n_bit = str(64)  # default to complex 128 bit

            float_dtype = 'float' + half_n_bit
            self.curr_range = self._get_low_high_from_range(float_dtype, half_n_bit, obey=range_obey)

            new_val = self._gen_complex(half_n_bit, np_dtype, shape)

        # bool
        if np_dtype == 'bool':
            new_val = self._gen_bool(shape)

        # str
        if np_dtype == 'str':
            # don't care about the shape of a string parameter
            new_val = self._gen_str()

        # dtype
        if np_dtype == 'dtype':
            new_val = self._gen_dtype(dtype_map)

        if 'None' in np_dtype:
            new_val = None


        if util.is_type_numeric(np_dtype):
            self.curr_range.set_boundary(np_dtype)    # set boundary cases for extreme values
        
        try:
            return new_val          
        except:     # if new_val is not defined
            util.error('given dtype "%s" is not recognizable' % np_dtype)


    def _gen_dtype(self, dtype_map):
        default_dtypes = [k for k, v in dtype_map.items() if v is not None]
        while True:
            chosen_dtype = np.random.choice(default_dtypes)
            chosen_dtype = dtype_map[chosen_dtype]
            if chosen_dtype:
                break
        # only retain dtype part
        chosen_dtype_tokens = chosen_dtype.split('.')
        if len(chosen_dtype_tokens) > 1:
            chosen_dtype = chosen_dtype_tokens[1]
        try:
            new_val = np.dtype(chosen_dtype)
        except TypeError:
            util.error('cannot create a valid dtype %s' % chosen_dtype)
        return new_val

    def _gen_str(self):
        # already forced pick_ndim=0 in _pick_dtype_ndim()
        print('Warning: trying to generate string; will not generate multi-dimensional string')
        letters = string.printable
        str_len = np.random.randint(0, high=1024)
        return ''.join(np.random.choice(list(letters), size=str_len))

    def _gen_bool(self, shape):
        if len(shape) == 0:
            return bool(np.random.choice([True, False]))
        return np.random.choice([True, False], size=shape)

    def _gen_int(self, np_dtype, shape):
        """
        generate integer value based on dtype and shape
        :param n_bit: string. represent the number of bits for the variable. e.g. '64' in 'int64'
        :param np_dtype: the target int numpy dtype, e.g. 'int32'
        :param shape: the desired shape of the generated variable
        :return: newly generated value
        """
        if len(shape) == 0:
            size = None
        else:
            size = shape

        low, high = self.curr_range.lower_bound, self.curr_range.upper_bound

        if low == high:
            if self.curr_range.lower_bound_inclusive and self.curr_range.upper_bound_inclusive:
                return getattr(np, np_dtype)(low) * np.ones(size)
            util.error('invalid range for "%s" (low == high)' % (self.name))
        elif low > high:
            util.error('invalid range for "%s" (low > high)' % (self.name))

        if low < 0 and re.search('^uint([0-9]*)', np_dtype):
            print('Warning: chosen "uint" but the lower bound could be negative, will override')
            self.curr_range.low = 0
            low = 0

        if low < high:
            try:
                new_val = np.random.randint(low, high=high, size=size, dtype=np_dtype)
            except (ValueError, MemoryError):
                util.error('given size %s is too big to be generated' % str(size))
        else:
            print('Warning: low >= high; will use low')
            new_val = low
        if size:  # not 0D
            new_val = new_val.astype(np_dtype)
        else:  # 0D
            new_val = int(new_val)   

        
        return new_val

    def process_range_loop(self, tok):
        range_value = 0
        sign = '+'
        while tok:  # process until tok is empty string
            tok, value, new_sign = self.process_range_tok(tok)
            if new_sign:
                sign = new_sign
            if value is None:
                continue

            # check for special values
            if sign == '+':
                range_value += value
            elif sign == '-':
                range_value -= value
            elif sign == '*':
                range_value *= value
            else:  # sign is '/'; this case is highly unlikely
                assert value != 0
                range_value /= value
        return range_value

    def process_range_tok(self, tok):
        if tok[0] in '+-*/':
            return tok[1:], None, tok[0]
        elif tok.isnumeric():
            return '', int(tok), ''
        elif tok[0] == 'l' and 'len:' in tok:
            tok, ref, is_var = util.gobble_var_dep(tok, 'len:')
            if is_var:
                return tok, self._gen_value_from_var_dep(ref, 'len', gen_shape=False), ''
            else:
                util.error('expect "%s" in "len:xx" a variable, rather than a constant' % ref)
        elif tok[0] == 'n' and 'ndim:' in tok:
            tok, ref, is_var = util.gobble_var_dep(tok, 'ndim:')
            if is_var:
                return tok, self._gen_value_from_var_dep(ref, 'ndim', gen_shape=False), ''
            else:
                util.error('expect "%s" in "ndim:xx" a variable, rather than a constant' % ref)
        elif tok[0] == 'm' and 'max_value:' in tok:  # implicitly 1D
            tok, ref, is_var = util.gobble_var_dep(tok, 'max_value:')
            if is_var:
                return tok, self._gen_value_from_var_dep(ref, 'max_value', gen_shape=False), ''
            else:
                util.error('expect "%s" in "max_value:xx" a variable, rather than a constant' % ref)
        else:
            # referring to another var or constant value e.g. [batch_size,num_labels]
            tok, ref, is_var = util.gobble_var_dep(tok, '')
            if is_var:
                return tok, self._gen_value_from_var_dep(ref, 'eval', gen_shape=False), ''
            else:
                if not Param.shape_var or ref not in Param.shape_var or Param.shape_var[ref] is None:
                    # constraint file doesn't have 'shape_var' attribute OR
                    # constraint file doesn't have referred constant ref in 'shape_var' attribute OR
                    # the concrete value for ref is not initialized yet
                    Param.shape_var[ref] = np.random.randint(MAX_DIM + 1)
                return tok, Param.shape_var[ref], ''

    def process_bound_value(self, bound, bound_dep, default):
        if bound_dep:
            value = self.process_range_loop(bound_dep)
        elif bound is None or bound == np.NINF or bound == np.inf:
            value = default
        else:
            value = bound
        return value

    def _pick_range_spec(self, np_dtype, choices):
        assert choices and isinstance(choices, list)

        range_spec = None
        if len(choices) == 1:
            range_spec = choices[0]
        else:
            for rgc in choices:
                if np_dtype in rgc.compat_dtype:
                    range_spec = rgc
                    break
        if range_spec is None:
            util.warning('cannot find a compatible range choice; picking the first one')
            range_spec = choices[0]

        assert range_spec is not None
        return range_spec

    def _get_low_high_from_range(self, np_dtype, n_bit, obey=True):
        default_low, default_high = util.get_default_range(n_bit, np_dtype)
        if not self.range_choices:
            return Range(None,np_dtype, default_low, default_high, None, None, False, False, default_low, default_high)
            #return default_low, default_high

        range_spec = self._pick_range_spec(np_dtype, self.range_choices)

        # NOTE: this epsilon is used when we have range such as (a, b]
        # since the random generator we use will have range [a, b) we have to modify the a and b to
        # achieve a range e.g., (a, b] and [a, b]
        epsilon = util.choose_epsilon(np_dtype)

        low = self.process_bound_value(range_spec.lower_bound, range_spec.lower_bound_dep, default_low)
        if not range_spec.lower_bound_inclusive:  # case like (a, b)
            low += epsilon  # add a constant epsilon to avoid to generate `a`
        high = self.process_bound_value(range_spec.upper_bound, range_spec.upper_bound_dep, default_high)
        if range_spec.upper_bound_inclusive:  # case like [a, b]
            high += epsilon  # NOTE: technically could generate a number in [b, b+epsilon), but no better solution
        
        valid_range = Range(None,np_dtype, low, high, None, None, range_spec.lower_bound_inclusive, range_spec.upper_bound_inclusive, default_low, default_high)
        # return low, high
        if obey:
            return valid_range
        else:
            return self._gen_violate_range(np_dtype, valid_range)

    def _gen_violate_enum(self, data, dtype, choices):

        def get_min_max(choices):
            min = MAX_INT
            max = MIN_INT
            for value in choices:
                if int(value) < min:
                    min = int(value)
                if int(value) > max:
                    max = int(value)
            return min, max

        util.DEBUG('trying to violate enum constraint for %s' % self.name)

        # if one of the value in choices is of type string, this param is of type string
        str_type = False
        for value in choices:
            if util.infer_type_from_str(value) == 'str':
                str_type=True
                break

        if str_type:
            data = util.str_mutation(data, 1)   # mutate the string with one edit distance

        # if all of the value in choices are not string
        elif dtype=='int':
            min, max = get_min_max(choices)
            data = random.choice([min-1, max+1])

        elif dtype == 'float':
            # no such case so far, not implemented
            raise NotImplementedError("Enum is of type float.")

        util.DEBUG('selected %s for enum while the choices are %s' % (data, str(choices)))
        return data

    def _gen_violate_range(self, dtype, range_obj):
        util.DEBUG('trying to violate range constraint for %s' % self.name)
        range_list = []
        if not range_obj.is_default('low'):
            range_list.append([range_obj.default_low, range_obj.lower_bound])
        if not range_obj.is_default('high'):
            range_list.append([range_obj.upper_bound, range_obj.default_high])

        if range_list == []:
            range_list.append([range_obj.default_low, range_obj.default_high])

        low, high = random.choice(range_list)

        util.DEBUG('selected range [%s, %s]' % (low, high))
        # TODO: lower and upper bound inclusive are wrong here
        return Range(None, dtype, low, high, None, None, True, True, range_obj.default_low, range_obj.default_high)

    def _gen_float(self, np_dtype, shape):
        # default_low, default_high = util.get_default_range(n_bits, np_dtype)
        # self.curr_range = self._get_low_high_from_range(np_dtype, default_low, default_high, obey=range_obey)
        low, high = self.curr_range.lower_bound, self.curr_range.upper_bound

        if low > high:
            print('Error: invalid range for "%s" (low > high): %s' % self.name)
            exit(1)

        if low == high:
            try:
                new_val = getattr(np, np_dtype)(low) * np.ones(shape)
            except (MemoryError, ValueError):
                util.error('given shape %s is too big to be generated' % str(shape))
        if low < high:
            try:
                new_val = np.random.uniform(low=low, high=high, size=shape)
            except (MemoryError, ValueError):
                util.error('given shape %s is too big to be generated' % str(shape))
        
        
        if not shape:  # 0D
            return float(new_val)
        new_val = new_val.astype(np_dtype)
        return new_val

    def _gen_complex(self, half_bit, np_dtype, shape):
        # if n_bit.isnumeric():
        #     half_n_bit = str(int(int(n_bit) / 2))
        # else:  # just complex
        #     half_n_bit = str(64)  # default to complex 128 bit

        float_dtype = 'float' + half_bit
        real_part = self._gen_float(float_dtype, shape)
        imagine_part = self._gen_float(float_dtype, shape)
        if len(shape) == 0:  # 0D
            return complex(real_part, imagine_part)
        
        real_part_flat = real_part.flatten()
        imagine_part_flat = imagine_part.flatten()
        imagine_part_flat = list(map(cmath.sqrt, imagine_part_flat))
        new_val = real_part_flat + imagine_part_flat
        new_val = new_val.reshape(*shape).astype(np_dtype)
        return new_val

    def get_package_dtype_name(self, dtype, dtype_map):
        """
        find the package-specific dtype name using substring matching
        :param dtype: the plain dtype name (e.g. float32)
        :param dtype_map: the data type mapping
        :return: return the package-specific name if found, otherwise None
        """
        # only care about the key
        for dtype_name in dtype_map.keys():
            if dtype in dtype_name:
                return dtype_name
        return dtype


    def set_category(self, dtype):


        if dtype == 'bool':
            return Param_Category.BOOL

        if dtype == 'str':
            return Param_Category.STR

        if util.is_type_numeric(dtype):
            return Param_Category.NUM
        
        return Param_Category.COMPLEX
        
