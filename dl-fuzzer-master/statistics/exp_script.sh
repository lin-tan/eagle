bash setup_exp.sh tensorflow 2
bash setup_exp.sh pytorch 2
bash setup_exp.sh mxnet 2


bash prepair_bug_list.sh /local1/xdanning/docter/expr/tensorflow/TF37_a20925b_baseline/workdir expect_ok_no_constr
bash prepair_bug_list.sh /local1/xdanning/docter/expr/tensorflow/TF38_a20925b_baseline/workdir expect_ok_no_constr



bash prepair_bug_list.sh /local1/xdanning/docter/expr/pytorch/PT37_a20925b_baseline/workdir expect_ok_no_constr
bash prepair_bug_list.sh /local1/xdanning/docter/expr/pytorch/PT38_a20925b_baseline/workdir expect_ok_no_constr



bash prepair_bug_list.sh /local1/xdanning/docter/expr/mxnet/MX37_a20925b_baseline/workdir expect_ok_no_constr
bash prepair_bug_list.sh /local1/xdanning/docter/expr/mxnet/MX38_a20925b_baseline/workdir expect_ok_no_constr

