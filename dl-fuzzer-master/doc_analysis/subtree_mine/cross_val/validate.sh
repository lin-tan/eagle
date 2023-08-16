#!/bin/bash


# python divide_data.py

# init.py

# python parse_mine.py tf ../sample/tf_label.csv ./chuck_5/tf_chuck.yaml ../mining_data/tf/word_map ../mining_data/tf/inverse_word_map  ./val_mining_data/tf/  > ./val_mining_data/tf/tf_log
# python build_mapping.py tf ../sample/tf_label.csv ./val_mining_data/tf/ ./val_rule/tf/ > ./val_rule/tf_log
# python eval_fast.py tf ../sample/tf_label.csv ./chuck_5/tf_chuck.yaml ./val_rule/tf/ ./val_result/tf.csv


# python parse_mine.py pt ../sample/pt_label.csv ./chuck_5/pt_chuck.yaml ../mining_data/pt/word_map ../mining_data/pt/inverse_word_map  ./val_mining_data/pt/  > ./val_mining_data/pt/pt_log
# python build_mapping.py pt ../sample/pt_label.csv ./val_mining_data/pt/ ./val_rule/pt/ > ./val_rule/pt_log
# python eval.py pt ../sample/pt_label.csv ./chuck_5/pt_chuck.yaml ./val_rule/pt/ ./val_result/pt.csv


# python parse_mine.py mx ../sample/mx_label.csv ./chuck_5/mx_chuck.yaml ../mining_data/mx/word_map ../mining_data/mx/inverse_word_map  ./val_mining_data/mx/  > ./val_mining_data/mx/mx_log
# python build_mapping.py mx ../sample/mx_label.csv ./val_mining_data/mx/ ./val_rule/mx/ > ./val_rule/mx_log
# python eval.py mx ../sample/mx_label.csv ./chuck_5/mx_chuck.yaml ./val_rule/mx/ ./val_result/mx.csv




# use 30%

# python parse_mine.py tf ../sample/tf_label.csv ./chuck_5/tf_chuck.yaml ../mining_data/tf/word_map ../mining_data/tf/inverse_word_map  ./val_mining_data/tf/  > ./val_mining_data/tf/tf_log
# python build_mapping.py tf ../sample/tf_label.csv ./val_mining_data/tf/ ./val_rule/tf/ > ./val_rule/tf_log
# python eval_fast.py tf ../sample/tf_label.csv ./chuck_5/tf_chuck.yaml ./val_rule/tf/ ./val_result/tf.csv


# python parse_mine.py pt ../sample/pt_label30.csv ./chuck30_5/pt_chuck.yaml ../mining_data/pt/word_map ../mining_data/pt/inverse_word_map  ./val_mining_data/pt/  > ./val_mining_data/pt/pt_log
# python build_mapping.py pt ../sample/pt_label30.csv ./val_mining_data/pt/ ./val_rule/pt/ > ./val_rule/pt_log
# python eval_fast.py pt ../sample/pt_label30.csv ./chuck30_5/pt_chuck.yaml ./val_rule/pt/ ./val_result/pt30.csv


# didn't evaluate, only the last step
python parse_mine.py mx ../sample/mx_label30.csv ./chuck30_5/mx_chuck.yaml ../mining_data/mx/word_map ../mining_data/mx/inverse_word_map  ./val_mining_data/mx/  # > ./val_mining_data/mx/mx_log
python build_mapping.py mx ../sample/mx_label30.csv ./val_mining_data/mx/ ./val_rule/mx/ # > ./val_rule/mx_log
python eval_fast.py mx ../sample/mx_label30.csv ./chuck30_5/mx_chuck.yaml ./val_rule/mx/ ./val_result/mx30.csv