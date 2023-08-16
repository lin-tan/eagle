# this script count how many subsequences we actually used
# one subseq is used when we have rules for at least one sentences related.


import pandas as pd 
import csv

def check_nan(s):
    if pd.isna(s):
        return ''
    else:
        return s

def count_subseq_data(filename, df):
    # stop_cat = [
    #     'not useful',
    #     'not used',
    #     'not clear',
    #     'error',
    #     "can't handle",
    #     'cannot handle',
    #     'not general',
    #     'deprecated'
    # ]
    stop_cat = ['not useful']
    complex_cat = ['complex']

    cat_cnt = {
        'dtype': 0,
        'ds': 0,
        'shape': 0,
        'validvalue':0
    }

    #subseq_data={}  
    # for i, row in df.iterrows():
    #     idx = int(row['idx'])
    #     if idx not in subseq_data:
    #         subseq_data[idx] = False  # false means not used

    #     if subseq_data[idx]==True:
    #         continue
    #     cat = check_nan(row['cat'])
    #     if cat!='' and cat not in stop_cat:
    #         subseq_data[idx]=True
    subseq_data = {}
    complex_cnt = 0
    for i, row in df.iterrows():  
        idx = int(row['idx'])  
        cat_col = check_nan(row['cat'])
        if cat_col!='' and cat_col not in stop_cat:
            if cat_col in complex_cat:
                subseq_data[idx]=False
                complex_cnt+=1
                continue
            subseq_data[idx] = True
            cats = cat_col.split('+')
            for c in cats:
                if c not in cat_cnt:
                    print(filename+'  idx '+str(idx))
                    break
                cat_cnt[c]+=1
        else:
            subseq_data[idx]=False

    return subseq_data, complex_cnt, cat_cnt

def count_used(subseq_data):
    ret = 0
    for subseq in  subseq_data:
        if subseq_data[subseq]:
            ret +=1
    return ret

def update_cat_cnt(init_cnt, add_cnt):
    for c in add_cnt:
        init_cnt[c] += add_cnt[c]
    return init_cnt

def main():
    path = {
        'tf_name.csv': {'lib': 'tf', 'type': 'name'},
        'tf_descp2.csv': {'lib': 'tf', 'type': 'descp'},
        'pt_name.csv': {'lib': 'pt', 'type': 'name'},
        'pt_docdtype.csv': {'lib': 'pt', 'type': 'dd'},
        'pt_descp.csv': {'lib': 'pt', 'type': 'descp'},
        'mx_name.csv': {'lib': 'mx', 'type': 'name'},
        'mx_docdtype.csv': {'lib': 'mx', 'type': 'dd'},
        'mx_descp.csv': {'lib': 'mx', 'type': 'descp'},
    }
    
    num_used_subseq = {
        # including names
        'tf': 0,
        'pt': 0,
        'mx': 0,
        'name': 0,
        'descp': 0,
        'total': 0
    }

    num_complex_subseq = {
        # including names
        'tf': 0,
        'pt': 0,
        'mx': 0,
        'name': 0,
        'descp': 0,
        'total': 0
    }


    cat_cnt = {
        'dtype': 0,
        'ds': 0,
        'shape': 0,
        'validvalue':0
    }

    total_subseq = {
        'others': 0,  # including descp+doc_dtype
        'name': 0,
        'total': 0
    }





    for csv_file in path:
        df = pd.read_csv('../cnt_useful/csv/'+csv_file)
        subseq_data, complex_cnt, cat_cnt_tmp = count_subseq_data(csv_file, df)
        num_subseq = len(subseq_data.keys())
        num_used  = count_used(subseq_data)
        cat_cnt = update_cat_cnt(cat_cnt, cat_cnt_tmp)
        print('{}: {} total, {} excluded ({} complex), {} left'.format(csv_file, num_subseq, num_subseq-num_used, complex_cnt, num_used))
        
        if path[csv_file]['type'] == 'dd':
            src_type = 'descp'
        else:   
            src_type = path[csv_file]['type']

        num_used_subseq[path[csv_file]['lib']] += num_used
        num_used_subseq[src_type] += num_used
        num_used_subseq['total'] += num_used

        num_complex_subseq[path[csv_file]['lib']] += complex_cnt
        num_complex_subseq[src_type] += complex_cnt
        num_complex_subseq['total'] += complex_cnt


        if path[csv_file]['type']=='name':
            total_subseq['name'] += num_subseq
        else:
            total_subseq['others'] += num_subseq

        total_subseq['total'] += num_subseq



    print('Number of sequences descp/name (used/not used)')
    print(total_subseq)
    
    print('Number of used subsequences')
    print(num_used_subseq)

    print('Number of complex(unused) subsequences')
    print(num_complex_subseq)

    print('Number(percent) of used subseq for each catgory')
    for c in cat_cnt:
        print('{} : {}({})'.format(c, cat_cnt[c], cat_cnt[c]/num_used_subseq['total']))



main()

