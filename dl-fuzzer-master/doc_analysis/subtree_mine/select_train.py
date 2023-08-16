import pandas as pd
from util import *
import random

def main(label_path, save_path, train_size):
    label_df = pd.read_csv(label_path)
    all_api_param = set()
    for index, row in label_df.iterrows():
        api = row['API']
        arg = row['Arg']
        all_api_param.add((api, arg))

    sample = random.sample(list(all_api_param), train_size)
    sample_sent_idx = []
    for index, row in label_df.iterrows():
        api = row['API']
        arg = row['Arg']
        if (api, arg) in sample:
            sample_sent_idx.append(index)
        
    sample_df = label_df.iloc[sample_sent_idx]
    sample_df.to_csv(save_path, index=False)
    # print(len(all_api_param))
    # # print(sample_df.groupby(['API', 'Arg']).size().reset_index().rename(columns={0:'count'}))
    # print(sample_df.groupby(['API', 'Arg']).size())

main('./sample/tf_label30.csv', './sample/tf_label500.csv', 500)
main('./sample/pt_label30.csv', './sample/pt_label500.csv', 500)
main('./sample/mx_label30.csv', './sample/mx_label500.csv', 500)