#!/bin/bash


# all disabled fuzz optional
python cnt_exceptions.py \
    --workdir=/local1/xdanning/docter/expr/tensorflow/tf_1_aa6e25_baseline/workdir/expect_ok_no_constr_no_adapt \
    --title=tf_baseline \
    --output=/local1/xdanning/docter/stat/tf_baseline.csv

python cnt_exceptions.py \
    --workdir=/local1/xdanning/docter/expr/tensorflow/tf_1_aa6e25_eonat/workdir/expect_ok_constr_no_adapt \
    --title=tf_eo \
    --output=/local1/xdanning/docter/stat/tf_eo.csv

    
python cnt_exceptions.py \
    --workdir=/local1/xdanning/docter/expr/tensorflow/tf_1_aa6e25_ee/workdir/expect_exception_constr_no_adapt \
    --title=tf_ee \
    --output=/local1/xdanning/docter/stat/tf_ee.csv




python cnt_exceptions.py \
    --workdir=/local1/xdanning/docter/expr/tensorflow/tf_2_d08b4b3_baseline/workdir/expect_ok_no_constr_no_adapt \
    --title=tf_baseline_fuzzoptional \
    --output=/local1/xdanning/docter/stat/tf_baseline_fuzzoptional.csv

python cnt_exceptions.py \
    --workdir=/local1/xdanning/docter/expr/tensorflow/tf_2_d08b4b3_eo/workdir/expect_ok_constr_no_adapt \
    --title=tf_eo_fuzzoptional \
    --output=/local1/xdanning/docter/stat/tf_eo_fuzzoptional.csv

python cnt_exceptions.py \
    --workdir=/local1/xdanning/docter/expr/tensorflow/tf_2_d08b4b3_ee/workdir/expect_exception_constr_no_adapt \
    --title=tf_ee_fuzzoptional \
    --output=/local1/xdanning/docter/stat/tf_ee_fuzzoptional.csv