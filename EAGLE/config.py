# the directory where data is stored, including generated input and output files
DATA_DIR = '/mnt/equivalentmodels_data'

# specifics of done file
TEST_DONE_COLS = ['rule', 'lib', 'version', 'api', 'input_index', 'done']
TEST_DONE_FILE = "test_done.csv"

# number of arguments generated
NUM_OF_ARGS = 1000
# number of inputs generated
NUM_OF_INPUT = 450

TF_NAME = "tensorflow"
PT_NAME = "pytorch"

# the max value for matrix input generation
MAX_MATRIX_VALUE = 100

TIMEOUT = 30