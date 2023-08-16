import importlib
import itertools
import multiprocessing as mp
import os
import sys
import pickle
import queue
import signal
import time
from contextlib import contextmanager

import numpy as np
from scipy.spatial.distance import squareform, pdist
from sklearn.cluster import AgglomerativeClustering

import util
from util import CustomCrash
from constant import MAX_NUM_DIM, Status, MAX_PERMUTE, NAN_EXIT, ZERO_DIV_EXIT, SYS_EXIT
from errors import FuzzerError
from param import Param


class FuzzerFailureStatus:
    def __init__(self):
        self.consec_fail_count = 0  # used to determine if too many cases failed in expect_ok case
        self.is_consec_fail = False
        self.reduce_failure = False
        self.ok_seed_list = []
        self.excpt_seed_list = []


class Fuzzer:
    """
    For fuzzing by specified from one configuration
    """
    def __init__(self, config, data_construct=None):
        self.config = config
        self.data_construct = data_construct

        self.exit_flag = False
        self.fstatus = FuzzerFailureStatus()
        self.import_statements = []
        self.total_iter = 0
        self.tried_empty = False
        self.model_input = False
        self.valid_permute_dtypes = []

        # after this, may want to check first if package is importable
        # NOTE: doing this means every Fuzzer object would try to do the import
        # this may not be the most efficient way to check if package is importable
        self._check_target_package()
        return

    def _check_target_package(self):
        mod = None
        self.root_mod = None
        try:
            print('Trying to import target package...')
            mod = importlib.import_module(self.config.package)  # only import at the init stage of a Fuzzer object
            # root_mod = mod
            self.root_mod = mod
            self.import_statements.append('import %s' % self.config.package)
        except ModuleNotFoundError:
            util.error('cannot import the specified module %s; need to correct in config file.' % self.config.package)

        assert mod is not None

        if mod.__version__ != self.config.version:
            util.error('version specified in config %s does not match with the one in environment %s'
                       % (self.config.version, mod.__version__))

        print('Package %s %s imported successfully' % (self.config.package, self.config.version))

        # parse title to get down to the function
        # e.g. `tf.math.sin` needs first get to the `math` module, and then `sin`
        title_toks = self.config.title.split('.')
        assert len(title_toks) > 1
        assert title_toks[-1] == self.config.target
        self.target_func_statement = '.'.join([self.config.package] + title_toks[1:])

        # go down the chain to get the target function
        target_func = self.get_func_ptr(mod, self.config.title)
        # for i, t in enumerate(title_toks):
        #     if i == 0:  # the root module (e.g. tf in case of tensorflow)
        #         continue
        #     if i < len(title_toks) - 1:  # until the second last
        #         try:
        #             mod = getattr(mod, t)
        #         except AttributeError:
        #             import_statement = '.'.join(title_toks[:i + 1])
        #             self.import_statements.append(import_statement)
        #             mod = importlib.import_module(import_statement)
        #     else:
        #         break

        # test the target function exists
        if target_func: # not none
            self._target_func = target_func
        else: 
            util.error('target function %s does not exist in package %s' % (self.config.target, self.config.package))
        # try:
        #     target_func = getattr(mod, self.config.target)
        #     self._target_func = target_func
        # except AttributeError:
        #     util.error('target function %s does not exist in package %s' % (self.config.target, self.config.package))

        # test the data_construct
        if self.data_construct is None:
            return

        data_construct_toks = self.data_construct.split('.')
        mod = self.root_mod
        for t in data_construct_toks:
            try:
                mod = getattr(mod, t)
            except AttributeError:
                util.error('given data construnct %s is not found in package %s'
                           % (self.data_construct, self.config.package))
        assert mod is not None
        self.data_construct = mod

    
    def get_func_ptr(self, package, title):
        # return the function pointer 
        # package: the package object (get from importlib)
        # title: tensorflow.keras.layers.GlobalMaxPooling3D
        # title_toks: something like ['tensorflow', 'keras', 'layers', 'GlobalMaxPool3D']
        title_toks = title.split('.')
        mod = package
        for i, t in enumerate(title_toks):
            if i == 0:  # the root module (e.g. tf in case of tensorflow)
                continue
            if i < len(title_toks) - 1:  # until the second last
                try:
                    mod = getattr(mod, t)
                except AttributeError:
                    import_statement = '.'.join(title_toks[:i + 1])
                    self.import_statements.append(import_statement)
                    mod = importlib.import_module(import_statement)
            else:
                break
        try:
            target_func = getattr(mod, title_toks[-1])
            return target_func
        except:
            return None

    @property
    def default_ndims(self):
        return list(np.arange(MAX_NUM_DIM+1))

    def add_ok_seed(self, seed_path):
        # only save the seed_path to save memory
        self.fstatus.ok_seed_list.append(seed_path)

    def add_excpt_seed(self, seed_path):
        # only save the seed_path to save memory
        self.fstatus.excpt_seed_list.append(seed_path)

    def _generate_model_input(self):
        # TODO
        # hardcode
        # input= (np.random.randn(1,32,32,16)).astype(np.float32)
        input_constr = util.def_model_input_constr(self.config.package)
        input_param = Param('model_input', input_constr, self.config.dtype_map, required=True, 
            guided_mutate = self.config.guided_mutate, special_value=False)

        p_mutate = True if util.random_prob(self.config.mutate_p) else False
        input_value = input_param.gen(True, self.default_ndims, self.config.dtype_map,
                             self.data_construct, chosen_np_dtype=None, p_mutate=p_mutate)
        return input_value

    def _run_max_iter(self, max_iter, obey, gen_script=False):
        runforever = False
        if max_iter == -1:  # run indefinitely
            runforever = True
        seeds = self._check_exist_seed() # currently empty
        count = 0
        while True:
            count += 1
            if count > max_iter and not runforever:
                break
            print('{:#^50}'.format(' %d/%d begin ' % (count, max_iter)))
            # making param to reset the shape_var
            Param.reset_shape_var()
            try:
                # generate new inputs
                new_seed = self._generate_new_input(obey) #self._generate(seeds, obey=obey, reduce_failure=self.fstatus.reduce_failure)
            except FuzzerError as e:
                util.warning('fuzzer failed to generate an input, will try again')
                continue
            if self.exit_flag:
                return
            if not new_seed:
                util.warning('Empty Input')
            # new_seed: new input
            self._test(new_seed, count, obey=obey, gen_script=gen_script, save=self.config.save)
            print('{:#^50}'.format(' %d/%d done ' % (count, max_iter)))
            print('{:-^50}'.format(''))

    # def _run_max_time(self, max_time, obey, gen_script=False):
    #     # didn't maintain
    #     def runforever():
    #         seeds = self._check_exist_seed()
    #         while True:
    #             new_seed = self._generate_new_input(obey)
    #             if self.exit_flag:
    #                 return
    #             if not new_seed:
    #                 print('Error: Failed to generate input, will try again')
    #                 continue
    #             self._test(new_seed, obey=obey, gen_script=gen_script)

    #     if max_time == -1:  # run indefinitely
    #         runforever()
    #         # NOTE: if max_time == 0, anything after this is unreachable

    #     @contextmanager
    #     def timeout(sec):
    #         signal.signal(signal.SIGALRM, raise_timeout)
    #         # Schedule the signal to be sent after ``time``.
    #         signal.alarm(sec)
    #         try:
    #             yield
    #         except TimeoutError:
    #             pass
    #         finally:
    #             # Unregister the signal so it won't be triggered
    #             # if the timeout is not reached.
    #             signal.signal(signal.SIGALRM, signal.SIG_IGN)

    #     def raise_timeout(signum, frame):
    #         print("The time limit specified has been reached, exiting...")
    #         os._exit(0)

    #     with timeout(max_time):
    #         runforever()

    def run(self, obey=True, max_iter=0, max_time=0, gen_script=False):
        assert max_iter != 0 or max_time != 0

        start = time.time()
        if max_iter:
            self._run_max_iter(max_iter, obey, gen_script=gen_script)
        else:
            self._run_max_time(max_time, obey, gen_script=gen_script)
        end = time.time()

        def output_fuzzing_time(sec):
            timefile = self.config.workdir + '/fuzz_time'
            msg = '\n### Total time used for input generation and testing: %.2f sec\n' % sec
            util.output_time(timefile, sec, msg)

        def output_mutate_coverage():
            out = self.config.output_mutate_coverage()
            util.write_csv(self.config.workdir + '/mutate_op_coverage.csv', out)

        output_fuzzing_time(end - start)
        if self.config.mutate_p>0:
            output_mutate_coverage()

    def _check_exist_seed(self):
        """
        This function checks if seeds exist
        if exists, use one of the existing seeds to mutate
        TODO: consider if this func makes sense: we don't have coverage to guide mutation
        :return:
        """
        seeds = []
        return seeds
    
    def _crosscheck_types(self, valid_python_types, valid_dtypes):
        """
        check if valid_dtypes is also valid in python types
        e.g. if dtype combination of (float32, float32, int32) is valid
        then, (float, float, int) should also be valid
        :param valid_python_types: list of dict in form {param1: py_type1, param2: py_type2, ...}
        :param valid_dtypes: list of dict in form {param1: dtype1, param2: dtype2, ...}
        :return:
        """
        # each element of the set is a tuple of python types
        python_type_set = set([tuple(t.values()) for t in valid_python_types])

        incon_dtypes = []
        for dt in valid_dtypes:
            tup = tuple(map(util.convert_dtype_to_pytype, dt.values()))
            if tup not in python_type_set:
                incon_dtypes.append(tuple(dt.values()))
                print(incon_dtypes[-1], end='')
                print(' is valid <--> ', end='')
                print(tup, end='')
                print(' is invalid')
        return set(incon_dtypes)

    def _pick_disobey_param(self, param_list, obey):
        # param_list: a list of parameter name as parameters to choose from

        if obey:
            return []

        # violating constraint
        # Note: it's not interesting to make all parameters to violate constraints
        # because one parameter violating constraints will lead to the entire function call fail
        # so, it's more interesting to make one parameter violate at a time
        
        disobey_candidates_required_param = [p.name for p in self.config.required_param.values() if p.can_disobey]
        disobey_candidates_optional_param = [p.name for p in self.config.optional_param.values() if p.can_disobey]
        disobey_params = disobey_candidates_required_param + disobey_candidates_optional_param
        # if self.config.fuzz_optional:
        #     pnames = [pname for pname in disobey_all]
        # else:  # only fuzz required params
        #disobey_params = [pname for pname in disobey_all]

        candidate = list(set(disobey_params) & set(param_list)) # intersection of two list (param can disobey & param to fuzz)
        if candidate:  # possible to disobey constraints
            disobey_param = list(np.random.choice(candidate, size=1))  # pick 1 random param to disobey
            util.DEBUG('selected %s to violate constraints' % disobey_param)
            return disobey_param

        util.warning('no parameter can disobey constraints, falling back to random generation')
        return []

    def _pick_mutate_param(self, param_list):
        if util.random_prob(self.config.mutate_p):
            mutate_candidates_required_param = [p.name for p in self.config.required_param.values()]
            mutate_candidates_optional_param = [p.name for p in self.config.optional_param.values()]
            mutate_all = mutate_candidates_required_param + mutate_candidates_optional_param
            candidate = list(set(mutate_all) & set(param_list)) # intersection of two list (param can disobey & param to fuzz)
            if candidate:
                mutate_param = list(np.random.choice(candidate, size=1))  # pick 1 random param to disobey
                util.DEBUG('selected %s to mutate ' % mutate_param)
                return mutate_param  
            else:
                util.warning('no parameter can mutate')
        return [] 

    def _gen_from_dtype_comb(self, obey, dtype_comb={}):

        # disobey_param = self._pick_disobey_param(obey)  

        def gen_from_dtype_helper(name, param_obey, p_mutate):
            chosen_dtype = dtype_comb.get(name)
            if name in self.config.required_param:
                p_obj = self.config.required_param[name]
            else:
                p_obj = self.config.optional_param[name]
            return p_obj.gen(param_obey, self.default_ndims, self.config.dtype_map,
                             self.data_construct, chosen_np_dtype=chosen_dtype, p_mutate=p_mutate)

        gen_inputs = {}     # dict: generated input
        # param2fuzz = []     # parameter to fuzz
        for pname in self.config.gen_order:     # pname : string
            if pname in self.config.optional_param: # if pname is optional param.
                # if not self.config.fuzz_optional:   
                #     # skip if not "fuzz_optional"
                #     continue
                if not util.random_prob(threshold=self.config.fuzz_optional_p):
                    # include each optional parameter under probability "fuzz_optional_p"
                    continue
            gen_inputs[pname] = None
        
        util.DEBUG('Parameter to generate: '+str(list(gen_inputs.keys())))
        disobey_param = self._pick_disobey_param(list(gen_inputs.keys()), obey)   # pick parameter to disobey
        mutate_param = self._pick_mutate_param(list(gen_inputs.keys()))   # whether to mutate

        for pname in self.config.gen_order: # generate all param in case it has dependency 
            p_obey = not pname in disobey_param             # whether to follow constraint
            p_mutate = (pname in mutate_param)              # whether to mutate
            data = gen_from_dtype_helper(pname, p_obey, p_mutate)
            if pname in gen_inputs:
                gen_inputs[pname] = data

        return gen_inputs


    def _generate_new_input(self, obey):
        gen_inputs = {}

        def need_to_try_empty_input():
            # if all inputs are optional & expect_ok => try empty input first
            if obey and not self.config.required_param and not self.tried_empty:
                return True
            # if at least one required input & expect exception => try empty input first
            if not obey and self.config.required_param and not self.tried_empty:
                return True
            return False

        if need_to_try_empty_input():  # try empty only once
            self.tried_empty = True
            print('-- Try Empty Input --')
            return gen_inputs

        return self._gen_from_dtype_comb(obey)


    def _test(self, seed, count=None, obey=True, gen_script=False, save=False):
        """
        This function tests the target function with seed
        :return: 0 if the test was fine; 1 if the test had issue; 2 if the test timeout
        """
        seed_fpath, is_duplicate = '', False
        model_input_path, input_duplicate = '', False
        test_script_path = ''
        #model_input_path, input_is_duplicate = '', False
        # try:
        seed_fpath, is_duplicate = util.save_seed_to_file(seed, self.config.workdir, count, save=save)
        # except OverflowError:
        #     util.DEBUG('OverflowError when trying to save file.')
        #     return

        # seed = util.load_seed('/local1/xdanning/test/workdir/209915c258f04626e8a64a7c0e1eff8c30419b87.p')

        self.total_iter += 1

        
        if self.config.model_test:
            while True:
                try: 
                    model_input = self._generate_model_input()
                    if util.detect_nan_inf(model_input):
                        raise FuzzerError('Model input contains nan/inf.')
                    model_input_path, input_duplicate = util.save_seed_to_file(model_input, self.config.workdir, count, save_to_file='gen_order_model_input', file_type='model input', save=save)
                    break
                except FuzzerError as e:
                    util.warning('fuzzer failed to generate a model input. Will try again.')
                
        else:
            model_input=False

        # if we want to generate a python script to reproduce the generated input
        test_script_path, content = util.gen_input_test_script(seed_fpath, model_input_path, 
                                                      self.import_statements,
                                                      self.config.package,
                                                      self.target_func_statement, save=save) if gen_script else ''

        
        util.write_record(os.path.join(self.config.workdir, 'script_record'), '%s, %s\n' % (test_script_path, count))
        if is_duplicate and (self.config.model_test == False or input_duplicate):    
            # assume the chance that both layer_obj and model_input duplicate is low
            util.warning('skipping a duplicate')
            return Status.PASS
        
        exception_list = self.config.exceptions

        worker_func = self._expect_ok if obey else self._expect_exception
        
        res_queue = mp.Queue(1)
        p = mp.Process(target=worker_func, args=(seed, model_input, res_queue, seed_fpath, exception_list, self.config.model_test, count))
        p.start()
        

        def check_process(process, tlimit):
            start_time = time.time()
            while time.time() - start_time < tlimit:
                try:
                    self.fstatus, res_status = res_queue.get(timeout=0.1)
                    assert res_status == Status.PASS or res_status == Status.FAIL
                    if res_status == Status.FAIL:
                        # failure: either (expect_ok & got exception) or (expect_exception & no exception)
                        util.report_failure(seed_fpath, test_script_path, self.config.workdir)
                    break
                except queue.Empty:
                    if not process.is_alive():
                        res_status = Status.SIGNAL
                        break
            else:  # time limit reached
                process.terminate()
                res_status = Status.TIMEOUT

            process.join()
            return res_status

        status = check_process(p, self.config.timeout)
        # if status == Status.FAIL:
        #     # failure: either (expect_ok & got exception) or (expect_exception & no exception)
        #     util.report_failure(seed_fpath, test_script_path, self.config.workdir)
        
        if status == Status.PASS or status == Status.FAIL:
            return status

        if not save:
            util.save_seed(seed_fpath, seed)
            if self.config.model_test:
            # if model_input!=False:
                util.save_seed(model_input_path, model_input)
            util.save_file(test_script_path, content)


        # either Timeout or Signal error
        # # in case `save` == False, save the input and the script
        # seed_fpath, is_duplicate = util.save_seed_to_file(seed, self.config.workdir, count)
        # if not test_script_path:
        #     test_script_path = util.gen_input_test_script(seed_fpath, model_input_path, 
        #                                               self.import_statements,
        #                                               self.config.package,
        #                                               self.target_func_statement)
        if (p.exitcode < 0 and -p.exitcode != signal.SIGTERM) or p.exitcode == NAN_EXIT or p.exitcode==ZERO_DIV_EXIT or p.exitcode==SYS_EXIT:
            util.report_signal_error_input(p.exitcode, seed_fpath, test_script_path, self.config.workdir, model_input_path)
            return Status.SIGNAL



        # timeout_error
        if -p.exitcode != signal.SIGTERM:  # TODO: remove this debug block later when problem is clear
            debug_log_fname = self.config.workdir + '/debug.log'
            with open(debug_log_fname, 'w+') as f:
                f.write('# this file is to record a timeout that had exitcode other than SIGTERM\n')
                f.write('-------------------------\n')
                f.write('input = %s\n' % seed_fpath)
                f.write('exit code = %d\n' % -p.exitcode)
                f.write('-------------------------\n')
            exit(1)

        util.report_timeout_error_input(seed_fpath, test_script_path, self.config.workdir)
        return Status.TIMEOUT

    def _run_model_test(self, layer, model_input=None):
        util.DEBUG('Model Testing: layer created')
        contain_nan = False
        if self.config.package == 'mxnet':
            layer.initialize()  # mxnet requires initialization
        #model = util.build_model(self.config.package, self.root_mod, ret, model_input.shape)
        #print('Testing model: model built successfully')
        #pred = model.predict(model_input)
        pred = layer(model_input)
        # if self.package=='mxnet':
        try:
            pred=pred.asnumpy()
        except:
            pass
            
        try:
            if np.isnan(pred).any():    # if output contains nan
                contain_nan = True
                # # don't record nan bug if any of the parameters or model_input contains nan or inf
                # for arg in seed:
                #     if _detect_nan_inf(seed[arg]):
                #         contain_nan=False
                #         break
                # #if contain_nan: # if input param. doesn't contain nan/inf
                # if _detect_nan_inf(model_input):
                #     contain_nan=False

        except:
            pass

        if contain_nan:
            raise CustomCrash(NAN_EXIT)
            # sys.exit(NAN_EXIT)
            #sys.exit(NAN_EXIT) # this will exit the whole fuzzer



    def _run_test(self, seed, model_test):
        

        verbose_ctx = util.verbose_mode(self.config.verbose)
        contain_nan = False
        with verbose_ctx:
            ret = self._target_func(**seed)
            if not model_test and self.config.check_nan:
                try:        # in case ret is not valid for np.isnan
                    if np.isnan(ret).any():
                        contain_nan = True
                except:
                    pass

        if contain_nan:
            raise CustomCrash(NAN_EXIT)
            #sys.exit(NAN_EXIT)
        
        return ret
                



    def _expect_ok(self, seed, model_input, res_queue, seed_fpath='', exception_list=[], model_test=False, count=None):
        # NOTE: although we expect status to be ok, the constraints could be very loose
        # so even though we think we might have generated valid input according to constraints
        # might still cause exceptions
        constructor_fail=True
        try:
            # verbose_ctx = util.verbose_mode(self.config.verbose)
            # with verbose_ctx:
            #   self._target_func(**seed)
            layer_obj = self._run_test(seed, model_test)
            if model_test:
                constructor_fail=False
                self._run_model_test(layer_obj, model_input)
            if seed_fpath:  # seed_fpath == '' when we don't want to save the input
                self.add_ok_seed(seed_fpath)
            else:
                res_queue.put((self.fstatus, Status.Pass))
                return
            self.fstatus.is_consec_fail = False
            self.fstatus.consec_fail_count = 0
            res_queue.put((self.fstatus, Status.PASS))
            return
        except SystemExit: 
            sys.exit(SYS_EXIT)
        except ZeroDivisionError:
            sys.exit(ZERO_DIV_EXIT)
            # sys.exit(ZERO_DIV_EXIT)
        except CustomCrash as cc:
            sys.exit(cc.code)
        except Exception as e:
            # NOTE: with current setting, due to lack of detailed documentation
            # exceptions frequently occur in this case (especially on what valid data type should be)
            # MAY WANT TO consider to ADD another mode of execution to only care about sys signals
            print('FuzzerMessage: expects function execution to be ok, but exception occurred.')
            print('------------ Exception Message ------------')
            print(e)
            print('-------------------------------------------')

            if not seed_fpath:  # when we don't want to save the seed
                res_queue.put((self.fstatus, Status.FAIL))
                return
            # save exception message to file
            assert seed_fpath.endswith('.p')
            if constructor_fail:
                e_fpath = seed_fpath[:-2] + '.e'
            else:
                e_fpath = seed_fpath[:-2] + '.emt'      # exception for model testing
            # only writes if not exist
            util.write_record(os.path.join(self.config.workdir, 'exception_record'), '%s, %s\n' % (e_fpath, count))
            if self.config.save and not os.path.exists(e_fpath):
                with open(e_fpath, 'w+') as wf:
                    wf.write(str(e))

            self.add_excpt_seed(seed_fpath)
            self.fstatus.consec_fail_count += 1
            # if self.fstatus.is_consec_fail:
            #     if self.fstatus.consec_fail_count > self.config.consec_fail:
            #         util.warning('max consecutive failure reached, will try to reduce failure')
            #         self.fstatus.reduce_failure = True
            # else:
            #     self.fstatus.is_consec_fail = True
            res_queue.put((self.fstatus, Status.FAIL))
            return

    def _expect_exception(self, seed, model_input, res_queue, seed_fpath='', exception_list=[], model_test=False, count=None):
        had_exception = False
        constructor_fail=True
        try:
        #     verbose_ctx = util.verbose_mode(self.config.verbose)
        #     with verbose_ctx:
        #         self._target_func(**seed)
            layer_obj = self._run_test(seed, model_test)
            if model_test:
                constructor_fail=False
                self._run_model_test(layer_obj, model_input)
        except Exception as e:
            # save exception message to file
            print('FuzzerMessage: expects function execution to be ok, but exception occurred.')
            print('------------ Exception Message ------------')
            print(e)
            print('-------------------------------------------')
            if seed_fpath:
                assert seed_fpath.endswith('.p')
                if constructor_fail:
                    e_fpath = seed_fpath[:-2] + '.e'
                else:
                    e_fpath = seed_fpath[:-2] + '.emt'      # exception for model testing
                util.write_record(os.path.join(self.config.workdir, 'exception_record'), '%s, %s\n' % (e_fpath, count))
                # # only writes if not exist
                if self.config.save and not os.path.exists(e_fpath):
                    with open(e_fpath, 'w+') as wf:
                        wf.write(str(e))
                
            had_exception = True
            if len(exception_list) == 0:  # we don't know the valid exceptions, so we treat any exception as valid
                res_queue.put((self.fstatus, Status.PASS))
                return
            if type(e).__name__ in exception_list:  # in the valid list, also ok
                res_queue.put((self.fstatus, Status.PASS))
                return
            # not in the valid list
            # might be an error but it could be caused by insufficient knowledge of valid exceptions
            util.warning('Caught exception %s is not in the valid exception list, but may not be an error.'
                         % type(e).__name__)
            res_queue.put((self.fstatus, Status.PASS))
            return

        if not had_exception:
            print('Error: expected to have exception but got no exception')
            res_queue.put((self.fstatus, Status.FAIL))
            return

    # def confirm_timeout(self, seed, obey, seed_fpath):
    #     """
    #     basically do the testing again with a bigger timeout limit
    #     :param seed: the input to be tested
    #     :param obey: flag to indicate whether to follow constraints
    #     :param seed_fpath: the input seed path
    #     :return: status of the testing
    #     """
    #     new_timeout = min(self.config.timeout * 10, 1800)  # 10x the specified timeout or .5h whichever the less
    #     util.warning("#### Going to retry the timeout with %d sec" % new_timeout)

    #     exception_list = self.config.exceptions

    #     worker_func = self._expect_ok if obey else self._expect_exception

    #     test_script_path = util.gen_input_test_script(seed_fpath,
    #                                                   self.import_statements,
    #                                                   self.target_func_statement)
    #     res_queue = mp.Queue(1)
    #     p = mp.Process(target=worker_func, args=(seed, res_queue, seed_fpath, exception_list))

    #     p.start()

    #     def check_process(process, tlimit):
    #         start_time = time.time()
    #         while time.time() - start_time < tlimit:
    #             try:
    #                 self.fstatus, res_status = res_queue.get(timeout=0.1)
    #                 assert res_status == Status.PASS or res_status == Status.FAIL
    #                 if res_status == Status.FAIL:
    #                     # failure: either (expect_ok & got exception) or (expect_exception & no exception)
    #                     util.report_failure(seed_fpath, test_script_path, self.config.workdir)
    #                 util.warning('a Timeout disappeared')
    #                 break
    #             except queue.Empty:
    #                 if not process.is_alive():
    #                     res_status = Status.SIGNAL
    #                     break
    #         else:  # time limit reached
    #             res_status = Status.TIMEOUT
    #             process.terminate()
    #             util.warning('a Timeout occurred')

    #         process.join()
    #         return res_status

    #     status = check_process(p, new_timeout)
    #     if status == Status.PASS or status == Status.FAIL:
    #         return status

    #     # signal error
    #     if p.exitcode < 0 and -p.exitcode != signal.SIGTERM:
    #         test_script_path = util.gen_input_test_script(seed_fpath,
    #                                                       self.import_statements,
    #                                                       self.target_func_statement)
    #         util.report_signal_error_input(p.exitcode, seed_fpath, test_script_path, self.config.workdir)
    #         return Status.SIGNAL

    #     # Timeout error
    #     return Status.TIMEOUT

    def rerun_timeout_input(self, obey):
        # read the timeout_record
        timeout_record = '/'.join([self.config.workdir, 'timeout_record'])
        confirmed_timeout_record = timeout_record + '_confirmed'

        if not os.path.exists(timeout_record):  # no timeout to re-run
            return

        with open(timeout_record, 'r') as f:
            timeout_inputs = f.read().splitlines()

        print("##### re-run the the timeout input ####")
        print("--- %d timeout input need to re-run ---" % len(timeout_inputs))
        for idx, input_i in enumerate(timeout_inputs):
            print("[%d/%d] testing %s --" % (idx+1, len(timeout_inputs), input_i))
            data = pickle.load(open(input_i, 'rb'))
            confirm_status = self.confirm_timeout(data, obey, input_i)
            if confirm_status == Status.TIMEOUT:
                with open(confirmed_timeout_record, 'a') as outf:
                    outf.write(input_i + '\n')
        if os.path.exists(confirmed_timeout_record):  # timeout_record_confirmed is only created if input timeout again
            os.rename(confirmed_timeout_record, timeout_record)
            util.sync_input_script(timeout_record)
        else:
            os.remove(timeout_record)  # all timeout input won't timeout if given more time, so delete
            os.remove(timeout_record.replace('record', 'script_record'))  # also delete the timeout_script_record

