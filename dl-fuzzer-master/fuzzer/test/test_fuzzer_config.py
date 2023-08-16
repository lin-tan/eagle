"""Tests to verify the functionality of FuzzerConfig
Since FuzzerConfig uses Param class while initializing the parameters,
the tests here is also indirectly testing Param
"""
from nose.tools import raises
from nose.tools import nottest
import copy
import nose
import os
import sys
from contextlib import contextmanager
from io import StringIO
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # to import module from parent dir

import numpy as np

import util
from errors import FuzzerError
from fuzzer_config import FuzzerConfig


@contextmanager
def captured_output():
    new_out, new_err = StringIO(), StringIO()
    old_out, old_err = sys.stdout, sys.stderr
    try:
        sys.stdout, sys.stderr = new_out, new_err
        yield sys.stdout, sys.stderr
    finally:
        sys.stdout, sys.stderr = old_out, old_err


class TestFuzzerConfig:
    def __init__(self):
        self.args = {
            'adapt_to': 'prev_ok',
            'cluster': True,
            'consec_fail': 10,
            'dist_metric': 'jaccard',
            'dist_threshold': 0.5,
            'dtype_config': None,
            'fuzz_optional': True,
            'max_iter': 100,
            'max_time': 100,
            'obey': True,
            'target_config': None,
            'timeout': 10,
            'verbose': True,
            'workdir': '/tmp/',
        }

        self.constraints = None

    @classmethod
    def setup_class(cls):
        """This method is run once for each class before any tests are run"""
        target_config = util.read_yaml(os.path.abspath('basic_target_config.yaml'))
        dtype_config = util.read_yaml(os.path.abspath('dtype_config.yaml'))
        cls.target_config = target_config
        cls.dtype_config = dtype_config

    @classmethod
    def teardown_class(cls):
        """This method is run once for each class _after_ all tests are run"""
        pass

    def setUp(self):
        """This method is run once before _each_ test method is executed"""
        self.args['target_config'] = copy.deepcopy(TestFuzzerConfig.target_config)
        self.args['dtype_config'] = copy.deepcopy(TestFuzzerConfig.dtype_config)

    def teardown(self):
        """This method is run once after _each_ test method is executed"""
        # restore
        self.args['target_config'] = copy.deepcopy(TestFuzzerConfig.target_config)
        self.args['dtype_config'] = copy.deepcopy(TestFuzzerConfig.dtype_config)

    @raises(FuzzerError)
    def test_empty_init(self):
        FuzzerConfig({})

    @raises(TypeError)
    def test_invalid_kwargs(self):
        args = {
            'invalid_arg': None
        }
        FuzzerConfig(args)

    def test_basic_config_ok(self):
        # using the basic config provided in this tester class should be ok
        FuzzerConfig(self.args)

    @raises(FuzzerError)
    def test_missing_dtype_config(self):
        self.args.pop('dtype_config')
        nose.tools.ok_(FuzzerConfig(self.args))

    @raises(FuzzerError)
    def test_missing_target_config(self):
        self.args.pop('target_config')
        FuzzerConfig(self.args)

    @raises(FuzzerError)
    def test_missing_target_inputs(self):
        self.args['target_config'].pop('inputs')
        FuzzerConfig(self.args)

    def test_missing_target_constraints(self):
        constraints = self.args['target_config'].get('constraints')
        nose.tools.assert_is_not_none(constraints)
        self.args['target_config'].pop('constraints')
        constraints = self.args['target_config'].get('constraints')
        nose.tools.assert_is_none(constraints)
        nose.tools.ok_(FuzzerConfig(self.args))

    def test_check_config_validity_missing_any(self):
        allowed_kwargs = {
            'adapt_to',
            'consec_fail',
            'fuzz_optional',
            'timeout',
            'verbose',
        }

        for keyword in allowed_kwargs:
            key_value = self.args.pop(keyword)
            with captured_output() as (out, err):
                FuzzerConfig(self.args)
            io_output = out.getvalue().strip()
            nose.tools.assert_equal(io_output, 'FuzzerWarning: "%s" is None' % keyword)
            self.args[keyword] = key_value  # restore

    @nottest
    def test_constraints_setup(self):
        target_config = self.args['target_config']
        constraints = target_config.get('constraints')
        nose.tools.assert_is_not_none(constraints)
        return constraints

    # testing ndim related #
    def test_constraint_no_ndim(self):
        constraints = self.test_constraints_setup()
        constraints['b'].pop('ndim')
        config = FuzzerConfig(self.args)
        nose.tools.assert_list_equal(config.required_param['b'].valid_ndims, [])

    def test_constraint_invalid_ndim(self):
        constraints = self.test_constraints_setup()
        constraints['b']['ndim'] = ['[]']
        nose.tools.assert_raises(FuzzerError, FuzzerConfig, self.args)

        constraints['b']['ndim'] = ['}{|*@$%%']
        nose.tools.assert_raises(FuzzerError, FuzzerConfig, self.args)

    def test_constraint_ndim_dep_ndim_var(self):
        constraints = self.test_constraints_setup()
        constraints['b']['ndim'] = ['ndim:&a']  # b's ndim == a's ndim
        config = FuzzerConfig(self.args)
        nose.tools.assert_set_equal(config.required_param['a'].var_dep, set())
        nose.tools.assert_set_equal(config.required_param['a'].const_dep, set())
        nose.tools.assert_set_equal(config.required_param['b'].var_dep, {'a'})
        nose.tools.assert_set_equal(config.required_param['b'].const_dep, set())
        nose.tools.assert_equal(config.gen_order, ['a', 'b'])

    @raises(FuzzerError)
    def test_constraint_ndim_dep_ndim_nonexistent_var(self):
        constraints = self.test_constraints_setup()
        constraints['b']['ndim'] = ['ndim:&c']  # xxx in ndim:&xxx is not in the input list
        FuzzerConfig(self.args)

    @raises(FuzzerError)
    def test_constraint_ndim_dep_ndim_var_itself(self):
        constraints = self.test_constraints_setup()
        constraints['b']['ndim'] = ['ndim:&b']
        FuzzerConfig(self.args)

    @raises(FuzzerError)
    def test_constraint_ndim_dep_ndim_constant(self):
        constraints = self.test_constraints_setup()
        constraints['b']['ndim'] = ['ndim:const']  # xxx in ndim:xxx should be a var
        FuzzerConfig(self.args)

    def test_constraint_ndim_dep_constant(self):
        constraints = self.test_constraints_setup()
        constraints['b']['ndim'] = ['const']  # ok
        nose.tools.ok_(FuzzerConfig(self.args))

    def test_constraint_ndim_int(self):
        constraints = self.test_constraints_setup()
        constraints['b']['ndim'] = ['1']  # ok
        nose.tools.ok_(FuzzerConfig(self.args))
        constraints['b']['ndim'] = [1]  # also ok
        nose.tools.ok_(FuzzerConfig(self.args))

    def test_constraint_ndim_float(self):
        constraints = self.test_constraints_setup()
        constraints['b']['ndim'] = ['1.12']
        nose.tools.assert_raises(FuzzerError, FuzzerConfig, self.args)
        constraints['b']['ndim'] = [1.12]
        nose.tools.assert_raises(FuzzerError, FuzzerConfig, self.args)

    def test_constraint_ndim_question_mark(self):
        constraints = self.test_constraints_setup()
        constraints['b']['ndim'] = ['?']
        config = FuzzerConfig(self.args)
        nose.tools.assert_list_equal(config.required_param['b'].valid_ndims, [])

    def test_constraint_ndim_greater(self):
        constraints = self.test_constraints_setup()
        constraints['b']['ndim'] = ['>2']
        config = FuzzerConfig(self.args)
        nose.tools.assert_true(all(int(ndim) > 2 for ndim in config.required_param['b'].valid_ndims))

    def test_constraint_ndim_greater_equal(self):
        constraints = self.test_constraints_setup()
        constraints['b']['ndim'] = ['>=2']
        config = FuzzerConfig(self.args)
        nose.tools.assert_true(all(int(ndim) >= 2 for ndim in config.required_param['b'].valid_ndims))

    def test_constraint_ndim_less(self):
        constraints = self.test_constraints_setup()
        constraints['b']['ndim'] = ['<2']
        config = FuzzerConfig(self.args)
        nose.tools.assert_true(all(2 > int(ndim) >= 0 for ndim in config.required_param['b'].valid_ndims))

    def test_constraint_ndim_less_equal(self):
        constraints = self.test_constraints_setup()
        constraints['b']['ndim'] = ['<=2']
        config = FuzzerConfig(self.args)
        nose.tools.assert_true(all(0 <= int(ndim) <= 2 for ndim in config.required_param['b'].valid_ndims))

    # testing shape related #
    def test_constraint_no_shape(self):
        constraints = self.test_constraints_setup()
        constraints['b'].pop('shape', None)
        config = FuzzerConfig(self.args)
        nose.tools.assert_is_none(config.required_param['b'].shape_spec)

    def test_constraint_invalid_shape(self):
        constraints = self.test_constraints_setup()
        constraints['b']['shape'] = ['()']
        nose.tools.assert_raises(FuzzerError, FuzzerConfig, self.args)

        constraints['b']['shape'] = ['']
        nose.tools.assert_raises(FuzzerError, FuzzerConfig, self.args)

        constraints['b']['shape'] = ['[]']
        nose.tools.assert_raises(FuzzerError, FuzzerConfig, self.args)

    def test_constraint_shape_int(self):
        constraints = self.test_constraints_setup()
        # the shape are just numbers
        constraints['a']['shape'] = ['[2, 2]']
        constraints['b']['shape'] = ['[2, 2]']
        config = FuzzerConfig(self.args)
        nose.tools.assert_set_equal(config.required_param['a'].var_dep, set())
        nose.tools.assert_set_equal(config.required_param['a'].const_dep, set())
        nose.tools.assert_set_equal(config.required_param['b'].var_dep, set())
        nose.tools.assert_set_equal(config.required_param['b'].const_dep, set())

    @raises(FuzzerError)
    def test_constraint_shape_float(self):
        constraints = self.test_constraints_setup()
        # the shape are float
        constraints['a']['shape'] = ['[2.5, 2.5]']
        constraints['b']['shape'] = ['[2., 2.]']
        FuzzerConfig(self.args)

    def test_constraint_shape_greater(self):
        constraints = self.test_constraints_setup()
        constraints['a']['shape'] = ['[>2]']
        constraints['b']['shape'] = ['[>5]']
        config = FuzzerConfig(self.args)
        nose.tools.assert_set_equal(config.required_param['a'].var_dep, set())
        nose.tools.assert_set_equal(config.required_param['a'].const_dep, set())
        nose.tools.assert_set_equal(config.required_param['b'].var_dep, set())
        nose.tools.assert_set_equal(config.required_param['b'].const_dep, set())

        # shape is [>=number]
        constraints['a']['shape'] = ['[>=2]']
        constraints['b']['shape'] = ['[>=5]']
        config = FuzzerConfig(self.args)
        nose.tools.assert_set_equal(config.required_param['a'].var_dep, set())
        nose.tools.assert_set_equal(config.required_param['a'].const_dep, set())
        nose.tools.assert_set_equal(config.required_param['b'].var_dep, set())
        nose.tools.assert_set_equal(config.required_param['b'].const_dep, set())

        # invalid shape
        constraints['a']['shape'] = ['[]']
        nose.tools.assert_raises(FuzzerError, FuzzerConfig, self.args)

        constraints['a']['shape'] = ['[>=]']
        nose.tools.assert_raises(FuzzerError, FuzzerConfig, self.args)

        constraints['a']['shape'] = ['[>]']
        nose.tools.assert_raises(FuzzerError, FuzzerConfig, self.args)

    def test_constraint_shape_greater_var(self):
        constraints = self.test_constraints_setup()
        constraints['b']['shape'] = ['[>&a]']
        config = FuzzerConfig(self.args)
        nose.tools.assert_set_equal(config.required_param['a'].var_dep, set())
        nose.tools.assert_set_equal(config.required_param['a'].const_dep, set())
        nose.tools.assert_set_equal(config.required_param['b'].var_dep, {'a'})
        nose.tools.assert_set_equal(config.required_param['b'].const_dep, set())
        nose.tools.assert_equal(config.gen_order, ['a', 'b'])

        # shape is [>=number]
        constraints['b']['shape'] = ['[>=&a]']  # gre
        config = FuzzerConfig(self.args)
        nose.tools.assert_set_equal(config.required_param['a'].var_dep, set())
        nose.tools.assert_set_equal(config.required_param['a'].const_dep, set())
        nose.tools.assert_set_equal(config.required_param['b'].var_dep, {'a'})
        nose.tools.assert_set_equal(config.required_param['b'].const_dep, set())
        nose.tools.assert_equal(config.gen_order, ['a', 'b'])

    def test_constraint_shape_dep_constant(self):
        constraints = self.test_constraints_setup()
        constraints['b']['shape'] = ['[batch_size,num_labels]']
        config = FuzzerConfig(self.args)
        nose.tools.assert_set_equal(config.required_param['a'].var_dep, set())
        nose.tools.assert_set_equal(config.required_param['a'].const_dep, set())
        nose.tools.assert_set_equal(config.required_param['b'].var_dep, set())
        nose.tools.assert_set_equal(config.required_param['b'].const_dep, {'batch_size', 'num_labels'})

    def test_constraint_shape_dep_var(self):
        constraints = self.test_constraints_setup()
        constraints['b']['shape'] = ['[batch_size, &a]']
        config = FuzzerConfig(self.args)
        nose.tools.assert_set_equal(config.required_param['a'].var_dep, set())
        nose.tools.assert_set_equal(config.required_param['a'].const_dep, set())
        nose.tools.assert_set_equal(config.required_param['b'].var_dep, {'a'})
        nose.tools.assert_set_equal(config.required_param['b'].const_dep, {'batch_size'})
        nose.tools.assert_equal(config.gen_order, ['a', 'b'])

    def test_constraint_shape_dep_dot(self):
        constraints = self.test_constraints_setup()
        constraints['b']['shape'] = ['[...,num_labels]']
        config = FuzzerConfig(self.args)
        nose.tools.assert_set_equal(config.required_param['a'].var_dep, set())
        nose.tools.assert_set_equal(config.required_param['a'].const_dep, set())
        nose.tools.assert_set_equal(config.required_param['b'].var_dep, set())
        nose.tools.assert_set_equal(config.required_param['b'].const_dep, {'num_labels'})

    def test_constraint_shape_dep_ndim_var(self):
        constraints = self.test_constraints_setup()
        constraints['b']['shape'] = ['[ndim:&a]']
        config = FuzzerConfig(self.args)
        nose.tools.assert_set_equal(config.required_param['a'].var_dep, set())
        nose.tools.assert_set_equal(config.required_param['a'].const_dep, set())
        nose.tools.assert_set_equal(config.required_param['b'].var_dep, {'a'})
        nose.tools.assert_set_equal(config.required_param['b'].const_dep, set())
        nose.tools.assert_equal(config.gen_order, ['a', 'b'])

    @raises(FuzzerError)
    def test_constraint_shape_dep_ndim_constant(self):
        constraints = self.test_constraints_setup()
        constraints['b']['shape'] = ['[ndim:const]']
        config = FuzzerConfig(self.args)
        nose.tools.assert_set_equal(config.required_param['a'].var_dep, set())
        nose.tools.assert_set_equal(config.required_param['a'].const_dep, set())
        nose.tools.assert_set_equal(config.required_param['b'].var_dep, set())
        nose.tools.assert_set_equal(config.required_param['b'].const_dep, {'const'})

    def test_constraint_shape_dep_len_var(self):
        constraints = self.test_constraints_setup()
        constraints['b']['shape'] = ['[len:&a]']
        config = FuzzerConfig(self.args)
        nose.tools.assert_set_equal(config.required_param['a'].var_dep, set())
        nose.tools.assert_set_equal(config.required_param['a'].const_dep, set())
        nose.tools.assert_set_equal(config.required_param['b'].var_dep, {'a'})
        nose.tools.assert_set_equal(config.required_param['b'].const_dep, set())
        nose.tools.assert_equal(config.gen_order, ['a', 'b'])

    @raises(FuzzerError)
    def test_constraint_shape_dep_len_constant(self):
        constraints = self.test_constraints_setup()
        constraints['b']['shape'] = ['[len:const]']
        FuzzerConfig(self.args)

    def test_constraint_shape_dep_max_value_var(self):
        constraints = self.test_constraints_setup()
        constraints['b']['shape'] = ['[max_value:&a]']
        config = FuzzerConfig(self.args)
        nose.tools.assert_set_equal(config.required_param['a'].var_dep, set())
        nose.tools.assert_set_equal(config.required_param['a'].const_dep, set())
        nose.tools.assert_set_equal(config.required_param['b'].var_dep, {'a'})
        nose.tools.assert_set_equal(config.required_param['b'].const_dep, set())
        nose.tools.assert_equal(config.gen_order, ['a', 'b'])

    def test_constraint_shape_arithmetic(self):
        constraints = self.test_constraints_setup()
        constraints['b']['shape'] = ['[&a+1]']  # the actual value won't be clear until the generation phase
        config = FuzzerConfig(self.args)
        nose.tools.assert_set_equal(config.required_param['a'].var_dep, set())
        nose.tools.assert_set_equal(config.required_param['a'].const_dep, set())
        nose.tools.assert_set_equal(config.required_param['b'].var_dep, {'a'})
        nose.tools.assert_set_equal(config.required_param['b'].const_dep, set())

        constraints['b']['shape'] = ['[&a-1]']  # the actual value won't be clear until the generation phase
        config = FuzzerConfig(self.args)
        nose.tools.assert_set_equal(config.required_param['a'].var_dep, set())
        nose.tools.assert_set_equal(config.required_param['a'].const_dep, set())
        nose.tools.assert_set_equal(config.required_param['b'].var_dep, {'a'})
        nose.tools.assert_set_equal(config.required_param['b'].const_dep, set())

        constraints['b']['shape'] = ['[&a*2]']  # the actual value won't be clear until the generation phase
        config = FuzzerConfig(self.args)
        nose.tools.assert_set_equal(config.required_param['a'].var_dep, set())
        nose.tools.assert_set_equal(config.required_param['a'].const_dep, set())
        nose.tools.assert_set_equal(config.required_param['b'].var_dep, {'a'})
        nose.tools.assert_set_equal(config.required_param['b'].const_dep, set())

        constraints['b']['shape'] = ['[&a/2]']  # the actual value won't be clear until the generation phase
        config = FuzzerConfig(self.args)
        nose.tools.assert_set_equal(config.required_param['a'].var_dep, set())
        nose.tools.assert_set_equal(config.required_param['a'].const_dep, set())
        nose.tools.assert_set_equal(config.required_param['b'].var_dep, {'a'})
        nose.tools.assert_set_equal(config.required_param['b'].const_dep, set())

        constraints['b']['shape'] = ['[len:&a,ndim:&a+const]']
        config = FuzzerConfig(self.args)
        nose.tools.assert_set_equal(config.required_param['a'].var_dep, set())
        nose.tools.assert_set_equal(config.required_param['a'].const_dep, set())
        nose.tools.assert_set_equal(config.required_param['b'].var_dep, {'a'})
        nose.tools.assert_set_equal(config.required_param['b'].const_dep, {'const'})

        # constraints['b']['shape'] = ['[-len:&a-1,ndim:&a+const]']
        # config = FuzzerConfig(self.args)
        # nose.tools.assert_set_equal(config.required_param['a'].var_dep, set())
        # nose.tools.assert_set_equal(config.required_param['a'].const_dep, set())
        # nose.tools.assert_set_equal(config.required_param['b'].var_dep, {'a'})
        # nose.tools.assert_set_equal(config.required_param['b'].const_dep, {'const'})

    # testing range related #
    def test_constraint_no_range(self):
        constraints = self.test_constraints_setup()
        constraints['b'].pop('range', None)
        config = FuzzerConfig(self.args)
        nose.tools.assert_is_none(config.required_param['b'].l_bound)
        nose.tools.assert_is_none(config.required_param['b'].l_bound_dep)
        nose.tools.assert_is_none(config.required_param['b'].r_bound)
        nose.tools.assert_is_none(config.required_param['b'].r_bound_dep)

    def test_constraint_invalid_range(self):
        constraints = self.test_constraints_setup()
        constraints['b']['range'] = ['rAndomStr']
        nose.tools.assert_raises(FuzzerError, FuzzerConfig, self.args)

        constraints['b']['range'] = ['[*)']
        nose.tools.assert_raises(FuzzerError, FuzzerConfig, self.args)

        constraints['b']['range'] = ['[0]']
        nose.tools.assert_raises(FuzzerError, FuzzerConfig, self.args)

    def test_constraint_range(self):
        constraints = self.test_constraints_setup()
        constraints['b']['range'] = ['(0, inf)']
        config = FuzzerConfig(self.args)
        nose.tools.assert_equal(config.required_param['b'].l_bound, 1)
        nose.tools.assert_is_none(config.required_param['b'].l_bound_dep)
        nose.tools.assert_equal(config.required_param['b'].r_bound, np.inf)
        nose.tools.assert_is_none(config.required_param['b'].r_bound_dep)

        constraints['b']['range'] = ['[0, inf)']
        config = FuzzerConfig(self.args)
        nose.tools.assert_equal(config.required_param['b'].l_bound, 0)
        nose.tools.assert_is_none(config.required_param['b'].l_bound_dep)
        nose.tools.assert_equal(config.required_param['b'].r_bound, np.inf)
        nose.tools.assert_is_none(config.required_param['b'].r_bound_dep)

        constraints['b']['range'] = ['[0, 2)']
        config = FuzzerConfig(self.args)
        nose.tools.assert_equal(config.required_param['b'].l_bound, 0)
        nose.tools.assert_is_none(config.required_param['b'].l_bound_dep)
        nose.tools.assert_equal(config.required_param['b'].r_bound, 1)
        nose.tools.assert_is_none(config.required_param['b'].r_bound_dep)

        constraints['b']['range'] = ['(0, 3)']  # NOTE: if input is (0, 2), problem arises
        config = FuzzerConfig(self.args)
        nose.tools.assert_equal(config.required_param['b'].l_bound, 1)
        nose.tools.assert_is_none(config.required_param['b'].l_bound_dep)
        nose.tools.assert_equal(config.required_param['b'].r_bound, 2)
        nose.tools.assert_is_none(config.required_param['b'].r_bound_dep)

        constraints['b']['range'] = ['[0, 3]']
        config = FuzzerConfig(self.args)
        nose.tools.assert_equal(config.required_param['b'].l_bound, 0)
        nose.tools.assert_is_none(config.required_param['b'].l_bound_dep)
        nose.tools.assert_equal(config.required_param['b'].r_bound, 3)
        nose.tools.assert_is_none(config.required_param['b'].r_bound_dep)

        constraints['b']['range'] = ['(-inf, 0]']
        config = FuzzerConfig(self.args)
        nose.tools.assert_equal(config.required_param['b'].l_bound, np.NINF)
        nose.tools.assert_is_none(config.required_param['b'].l_bound_dep)
        nose.tools.assert_equal(config.required_param['b'].r_bound, 0)
        nose.tools.assert_is_none(config.required_param['b'].r_bound_dep)

        constraints['b']['range'] = ['[const1, const2]']
        config = FuzzerConfig(self.args)
        nose.tools.assert_is_none(config.required_param['b'].l_bound)
        nose.tools.assert_equal(config.required_param['b'].l_bound_dep, 'const1')
        nose.tools.assert_is_none(config.required_param['b'].r_bound)
        nose.tools.assert_equal(config.required_param['b'].r_bound_dep, 'const2')

        constraints['b']['range'] = ['[&a, const2]']
        config = FuzzerConfig(self.args)
        nose.tools.assert_is_none(config.required_param['b'].l_bound)
        nose.tools.assert_equal(config.required_param['b'].l_bound_dep, '&a')
        nose.tools.assert_is_none(config.required_param['b'].r_bound)
        nose.tools.assert_equal(config.required_param['b'].r_bound_dep, 'const2')
        nose.tools.assert_set_equal(config.required_param['b'].var_dep, {'a'})

        # NOTE: it doesn't make sense to have ndim:constant
        # the validity checking is delayed to the generation phase
        # so it's ok to have this at FuzzerConfig stage
        constraints['b']['range'] = ['[-ndim:const, ndim:const]']
        config = FuzzerConfig(self.args)
        nose.tools.assert_is_none(config.required_param['b'].l_bound)
        nose.tools.assert_equal(config.required_param['b'].l_bound_dep, '-ndim:const')
        nose.tools.assert_is_none(config.required_param['b'].r_bound)
        nose.tools.assert_equal(config.required_param['b'].r_bound_dep, 'ndim:const')
        nose.tools.assert_set_equal(config.required_param['b'].const_dep, {'const'})

        constraints['b']['range'] = ['[-ndim:&a, ndim:&a]']
        config = FuzzerConfig(self.args)
        nose.tools.assert_is_none(config.required_param['b'].l_bound)
        nose.tools.assert_equal(config.required_param['b'].l_bound_dep, '-ndim:&a')
        nose.tools.assert_is_none(config.required_param['b'].r_bound)
        nose.tools.assert_equal(config.required_param['b'].r_bound_dep, 'ndim:&a')
        nose.tools.assert_set_equal(config.required_param['b'].var_dep, {'a'})

        constraints['b']['range'] = ['[0, max_value:&a]']
        config = FuzzerConfig(self.args)
        nose.tools.assert_equal(config.required_param['b'].l_bound, 0)
        nose.tools.assert_is_none(config.required_param['b'].l_bound_dep)
        nose.tools.assert_is_none(config.required_param['b'].r_bound)
        nose.tools.assert_equal(config.required_param['b'].r_bound_dep, 'max_value:&a')
        nose.tools.assert_set_equal(config.required_param['b'].var_dep, {'a'})

    def test_constraint_dtype(self):
        constraints = self.test_constraints_setup()
        default_dtype_list = [dtype for dtype, value in TestFuzzerConfig.dtype_config.items() if value is not None]

        # dtype spec is None, expect default
        constraints['b']['dtype'] = None
        config = FuzzerConfig(self.args)
        nose.tools.assert_list_equal(config.required_param['b'].valid_dtypes, default_dtype_list)

        # dtype spec is [], expect default
        constraints['b']['dtype'] = []
        config = FuzzerConfig(self.args)
        nose.tools.assert_list_equal(config.required_param['b'].valid_dtypes, default_dtype_list)

        # dtype spec has unknown dtype, expect unknown dtype is ignored
        constraints['b']['dtype'] = ['xyz']
        config = FuzzerConfig(self.args)
        nose.tools.assert_list_equal(config.required_param['b'].valid_dtypes, default_dtype_list)

        # dtype spec has unknown dtype, expect unknown dtype is ignored
        constraints['b']['dtype'] = ['xyz', 'int32']
        config = FuzzerConfig(self.args)
        nose.tools.assert_list_equal(config.required_param['b'].valid_dtypes, ['int32'])

        # only valid dtype present
        constraints['b']['dtype'] = ['int32']
        config = FuzzerConfig(self.args)
        nose.tools.assert_list_equal(config.required_param['b'].valid_dtypes, ['int32'])

        # TensorShape
        constraints['b']['dtype'] = ['TensorShape']
        config = FuzzerConfig(self.args)
        nose.tools.assert_list_equal(sorted(config.required_param['b'].valid_dtypes),
                                     sorted(['uint32', 'uint64', 'uint8', 'uint16']))
        nose.tools.assert_equal(config.required_param['b'].valid_ndims, ['1'])

        # scalar
        scalar_dtypes = ['uint8', 'uint16', 'uint32', 'uint64',
                         'int8', 'int16', 'int32', 'int64',
                         'float16', 'float32', 'float64']
        constraints['b']['dtype'] = ['scalar']
        config = FuzzerConfig(self.args)
        nose.tools.assert_list_equal(sorted(config.required_param['b'].valid_dtypes),
                                     sorted(scalar_dtypes))
        nose.tools.assert_equal(config.required_param['b'].valid_ndims, ['0'])

        # b's dtype is same as a's dtype
        constraints['b']['dtype'] = ['dtype:&a']
        config = FuzzerConfig(self.args)
        nose.tools.assert_set_equal(config.required_param['b'].var_dep, {'a'})
        nose.tools.assert_set_equal(config.required_param['b'].const_dep, set())

