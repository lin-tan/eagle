from util import * 
dtype_ls = read_yaml('./dtype_ls.yaml')
common_dt = set()
common_ds = set()
stat = {}
for fm in dtype_ls:
    stat[fm] = {}
    for cat in dtype_ls[fm]:
        if cat == 'dtype':
            if common_dt:
                common_dt.intersection_update(set(dtype_ls[fm][cat]))
            else:
                common_dt.update(set(dtype_ls[fm][cat]))
            #common_dt.update(set(dtype_ls[fm][cat]))
        elif cat == 'structure':
            if common_ds:
                common_ds.intersection_update(set(dtype_ls[fm][cat]))
            else:
                common_ds.update(set(dtype_ls[fm][cat]))
        stat[fm][cat] = len(dtype_ls[fm][cat])

print('Common dtype: {}, Common dstructure: {}'.format(len(list(common_dt)), len(list(common_ds))))
print(common_dt)
for fm in stat:
    print(stat[fm])