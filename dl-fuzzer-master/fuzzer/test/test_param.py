"""Tests to verify the functionality of Param
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
from param import Param


class TestParam:
    def __init__(self):
        pass

    @classmethod
    def setup_class(cls):
        """This method is run once for each class before any tests are run"""
        dtype_config = util.read_yaml(os.path.abspath('dtype_config.yaml'))
        cls.dtype_config = dtype_config

    @classmethod
    def teardown_class(cls):
        """This method is run once for each class _after_ all tests are run"""
        pass

    def setUp(self):
        """This method is run once before _each_ test method is executed"""

    def teardown(self):
        """This method is run once after _each_ test method is executed"""

    def test_param_init_none_spec(self):
        p = Param('a', None, TestParam.dtype_config, required=True)
