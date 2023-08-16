import sys
sys.path.insert(0,'..')
from extract_utils import *
from shutil import copyfile




src1 = './tf/danning+layer/'
src2 = './tf/danning/'
dest = './tf/danning_all/'

f_src1 = get_file_list(src1)
f_src2 = get_file_list(src2)

for f1 in f_src1:
    copyfile(src1+f1, dest+f1)

for f2 in f_src2:
    copyfile(src2+f2, dest+f2)



# csv_list_file = './tf_list'
# csv_layer_list_file = './tf+layer_list'
# dest = './tf/danning+layer/'
# count = 21
# old_cnt = 166

# csv_list = read_list(csv_list_file)
# csv_layer_list = read_list(csv_layer_list_file)

# csv_fname = [x.split('/')[-1].replace('*','_') for x in csv_list]
# csv_layer_fname = [x.split('/')[-1].replace('*','_') for x in csv_layer_list]


# cnt= 0 
# for i in range(len(csv_layer_fname)):
#     if csv_layer_fname[i] not in csv_fname[:old_cnt]:
#         copyfile(csv_layer_list[i], dest+csv_layer_fname[i])
#         cnt+=1

#     if cnt == count:
#         break
        


# for f in csv_fname[:old_cnt]:
#     if f not in csv_layer_fname:
#         print(f)
# tf: tf.keras.activations.get-identifier.csv       # deleted 167->166


