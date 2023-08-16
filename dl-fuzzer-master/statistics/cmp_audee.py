import sys
from os import walk
import re
import glob
import pickle
import os.path
from os import path



# path = {
#     'TF_baseline': '/local1/m346kim/dl-fuzzing/expr/tensorflow/docker_5_f3ce6b_no_constr_no_pp/workdir/expect_ok_prev_ok',
#     'TF_ADP_NC': '/local1/m346kim/dl-fuzzing/expr/tensorflow/docker_7_f3ce6b_no_constr/workdir/expect_ok_prev_ok/',
#     'TF_EO_NAT': '/local1/m346kim/dl-fuzzing/expr/tensorflow/docker_9_e5c96e_no_pp/workdir/expect_ok_prev_ok/',
#     'TF_EE': '/local1/y2647li/dl-fuzzing/expr/tensorflow/docker_11_571d2f_ee/workdir/expect_exception_constr_adapt/'
# }

exp = 'TF8_c6ab3aa'
dir_path = {
    'TF_baseline': '/local1/xdanning/docter/expr/tensorflow/'+exp+'_baseline/workdir/expect_ok_no_constr/',
    'TF_EE': '/local1/xdanning/docter/expr/tensorflow/'+exp+'_ee/workdir/expect_exception_constr/',
    'TF_EO': '/local1/xdanning/docter/expr/tensorflow/'+exp+'_eo/workdir/expect_ok_constr/'
}

API_list = {
    'tf.keras.layers.Conv2D': 
        {'kernel_size': 0},
    'tf.keras.layers.Embedding':
        {'input_dim': 0},
    'tf.keras.layers.Dense':
        {'units':0},
    'tf.keras.layers.Conv2DTranspose':
        {'dilation':(1,2)}
    #'tf.keras.layers.BatchNormalization' : 
}

for mode in dir_path:
    for api in API_list:
        file_path = dir_path[mode]+api.lower()+'.yaml_workdir/'  # !!!may need to modify this line!!!
        #print(file_path)
        target_inputs = glob.glob('{}*.p'.format(file_path))
        
        for arg in API_list[api]:
            cnt = 0
            pass_cnt = 0
            for input_path in target_inputs:
                #print(input_path)
                # if path.exists(input_path.replace('.p', '.e')):
                #     continue
                data = pickle.load(open(input_path, 'rb'))

                if arg not in data:
                    continue
                '''
                try:
                    if len(data[arg].shape)>1:
                        print('shape: '+str(data[arg].shape))
                except:
                    print(data[arg])

                '''
                try:
                    

                    if data[arg] == API_list[api][arg] or API_list[api][arg] in data[arg]:
                        # print(input_path)
                        cnt+=1
                        
                        # print('aaa' + str(path.exists(input_path[:-1]+'e')))
                        # print(input_path[:-1]+'e')
                        
                        if not path.exists(input_path[:-1]+'e'):
                            pass_cnt+=1

                except:
                    continue
            print('{} {}: {}={} for {}/{} inputs, {} passed'.format(mode, api, arg, API_list[api][arg], cnt, len(target_inputs), pass_cnt))


        


