from extract_utils import *
from doc_parser import *
from pat_cls import *
import sys
import traceback


def run(source_dir, yml_files, save_to, all_pat, dt_map, all_target, stop_name, test=False):


    save_cnt = 0
    for i, f in enumerate(yml_files):
        #print(f)

        print('{}/{}    {}'.format(i, len(yml_files), f))
        info = read_yaml(source_dir+f)
            
        parser = Parser(info, dt_map, all_target = all_target, stop_name=stop_name)
        
        try:

            #parser.refine_required_optional()
            # match patterns
            for pt in all_pat:
                stop_val = pt['config'].get('stop', None)

                func = 'parser.'+pt['config']['method']

                if pt['obj'] == None:
                    eval('%s()'%(func))

                elif stop_val!=None:
                    eval('%s(%s,stop=%s)'%(func,"pt['obj']",stop_val))
                else:
                    eval('%s(%s)'%(func,"pt['obj']"))

        except:
            print(pt)
            traceback.print_exc()
            break

        
        if test:
            prettyprint(info)

        #save info here
        #if parser.cnt>0:
        if check_changed(parser.info):
            save_cnt+=1
            save_addr = save_to+'changed/'
        else:
            save_addr = save_to+'unchanged/'

        if not test: 
            save_yaml(save_addr+f, parser.info)

    return save_cnt

def load_pat(pat_config, pat_dir, pat_cnt_save_dir):
    all_pat = []
    # load dt_map and all_targets
    
    dt_map = Pat(pat_dir+pat_config['dt_map_file'], pat_cnt_save_dir)
    all_target = Pat(pat_dir+pat_config['all_target_file'], pat_cnt_save_dir)

    # load rest of the pattern files

    for pf in pat_config['pat_file']:
        tmp_dict = {}
        if pf.get('file', None):
            tmp_dict['obj'] = Pat(pat_dir+pf['file'], pat_cnt_save_dir)
        else:
            tmp_dict['obj'] = None
        tmp_dict['config'] = pf

        all_pat.append(tmp_dict)

    return dt_map, all_target, all_pat

def main(framework, idx_test=-1):
    def _remove_v1(file_list):
        # this is only for tf, to remove all apis from tf.compat.v1
        ret = []
        for f in file_list:
            if 'tf.compat.v1' in f:
                continue
            ret.append(f)

        return ret
                

    pat_config = read_yaml('./{}/pat_config.yaml'.format(framework))
    
    source_dir = pat_config['source_dir']
    save_to = pat_config['save_to']
    pat_dir = pat_config['pat_dir']
    pat_cnt_save_dir = pat_config['pat_cnt_save_dir']

    stop_name = pat_config.get('stop_name', [])
    
    files = get_file_list(source_dir)

    if isinstance(idx_test, str):
        idx_test = files.index(idx_test)

    dt_map, all_target, all_pat = load_pat(pat_config, pat_dir, pat_cnt_save_dir)

    if idx_test== -1:
        yml_files = files
        test = False
    else:
        yml_files = files[idx_test:idx_test+1]
        test = True

    if not test:
        del_file(save_to)  # delete recursively all files existing in the save source_dir

    if framework=='tf':
        yml_files = _remove_v1(yml_files)
    save_cnt = run(source_dir, yml_files, save_to, all_pat, dt_map, all_target, stop_name, test)

    print(str(save_cnt)+' Changed!')

    if not test:    
        for pt in all_pat:
            if pt.get('obj', None): 
                pt['obj'].save_cnt()



if __name__ == "__main__":

    framework = sys.argv[1]
    
    idx_test = -1

    try:
        idx_test= str(sys.argv[2])
    except:
        pass

    main(framework, idx_test)
        

   