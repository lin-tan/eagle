"""
constants defined for the fuzzer
"""
from enum import Enum, auto
import sys

# threshold on how many permutations fuzzer wants to do
# if there will be more, will try to reduce the permutations
MAX_PERMUTE = 10000

# generated Tensor cannot be more than 5D
MAX_NUM_DIM = 5

# max length for each dimension
MAX_DIM = 20

# default values if user doesn't specify --max_iter or --max_time
DEFAULT_MAX_ITER = 10000
DEFAULT_MAX_TIME = 12000

MAX_INT = sys.maxsize
MIN_INT = -sys.maxsize-1

NAN_EXIT = 100      # exit code for nan bug
ZERO_DIV_EXIT = 101  # exit code for division by zero in python
SYS_EXIT = 102          # exit code for SystemEExit(`sys.exit()`)

INCON_EXIT = 200  # exit code for inconsistency bug

MAX_SEED_SIZE = 4000000000  # 4GiB

# enum class for the fuzzer to signal the testing status
class Status(Enum):
    INIT = auto()
    PASS = auto()
    FAIL = auto()
    TIMEOUT = auto()
    SIGNAL = auto()
    # NAN = auto()


class Param_Category(Enum):
    # the parameter category
    NUM = auto()          
    # NDARRAY = auto()        # multi-dimensional array
    STR = auto()            # string
    BOOL = auto()           # boolean
    COMPLEX = auto()        # complex objects or others (dtype)


