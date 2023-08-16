import sys
sys.path.insert(0,'..')
from util import *
import pandas as pd
import numpy as np


def isnan(num):
    return num!=num


def same_constr(cell1, cell2):
    if isnan(cell1)  and isnan(cell2):
        return True
    if cell1 == cell2 :
        return True
    try:
        if int(cell1) == int(cell2):
            return True
    except:
        pass
    return False

cat = ['dtype', 'structure', 'shape', 'ndim', 'range', 'enum']

def main(annotator1, annotator2, save_path):
    # annotator1: Danning
    # annotator2: Hung
    count = 0
    df1 = pd.read_csv(annotator1)
    df1["Normalized_descp"] = df1["Normalized_descp"].str.lower()
    # df1['structure'] = df1['structure'] + df1['tensor_t']
    df2 = pd.read_csv(annotator2)
    disagreement = pd.DataFrame(columns = df2.columns)
    for index, row in df2.iterrows():
        api = row['API']
        arg = row['Arg']
        descp = row['Descp']
        normalized_descp = row['Normalized_descp'].lower()
        map = np.where((df1['API']==api) & (df1['Arg']==arg) & (df1['Descp']==descp) & (df1['Normalized_descp']==normalized_descp))
        if not map[0]: 
            map = np.where((df1['API']==api) & (df1['Arg']==arg) & (df1['Normalized_descp']==normalized_descp))
        # map = df1.query("API == '%s' and Arg == '%s' and Descp == '%s' and Normalized_descp == '%s'" % (api, arg, descp, normalized_descp))
        assert (len(map) == 1)
        # print(type(row))
        if not map[0]:
            print(api)
            print(arg)
            print(descp)
            print(normalized_descp)
            print()
        for c in cat:
            # print(map[0])
            if same_constr(row[c], df1.iloc[map].iloc[0][c])  :  
                continue
            elif c=='structure':
                if same_constr(row[c], df1.iloc[map].iloc[0][c]) or same_constr(row[c], df1.iloc[map].iloc[0]['tensor_t']):
                    continue

            
                # print(row[c])
                # print(df1.iloc[map].iloc[0][c])
                # print()
                # print('reach here')

            # print(row[c])
            # print(df1.iloc[map].iloc[0][c])
            # print()
            disagreement = disagreement.append(row)
            disagreement = disagreement.append(df1.iloc[map])
            disagreement = disagreement.append(pd.Series(), ignore_index=True)
            count +=1 
            break
                # disagreemen
    # print(disagreement)
    disagreement.to_csv(save_path)
    print(count)
        # print()
        # print(df1.loc[map])

main('../sample/tf_label30.csv', './rebuttal_labeled_tf.csv', './tf_disagrement.csv')
main('../sample/pt_label30.csv', './rebuttal_labeled_pt.csv', './pt_disagrement.csv')
main('../sample/mx_label30.csv', './rebuttal_labeled_mx.csv', './mx_disagrement.csv')