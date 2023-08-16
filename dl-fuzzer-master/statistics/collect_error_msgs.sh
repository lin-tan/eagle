#TensorFlow
#python collect_error_msgs.py --workdir=/local1/m346kim/dl-fuzzing/expr/tensorflow/docker_9_e5c96e_no_pp/workdir/expect_ok_prev_ok --output=/local1/m346kim/dl-fuzzing/code/dl-fuzzer/statistics/results/tensorflow/docker9_no_adapt.csv
#python collect_error_msgs.py --workdir=/local1/m346kim/dl-fuzzing/expr/tensorflow/docker_9_e5c96e_no_pp/workdir/expect_exception_prev_ok --output=/local1/m346kim/dl-fuzzing/code/dl-fuzzer/statistics/results/tensorflow/docker9_expect_exception.csv
#python collect_error_msgs.py --workdir=/local1/m346kim/dl-fuzzing/expr/tensorflow/docker_8_e5c96e/workdir/expect_ok_prev_ok --output=/local1/m346kim/dl-fuzzing/code/dl-fuzzer/statistics/results/tensorflow/docker8_expect_ok.csv
#python collect_error_msgs.py --workdir=/local1/m346kim/dl-fuzzing/expr/tensorflow/docker_7_f3ce6b_no_constr/workdir/expect_ok_prev_ok --output=/local1/m346kim/dl-fuzzing/code/dl-fuzzer/statistics/results/tensorflow/docker7_no_constr.csv
#python collect_error_msgs.py --workdir=/local1/m346kim/dl-fuzzing/expr/tensorflow/docker_5_f3ce6b_no_constr_no_pp/workdir/expect_ok_prev_ok --output=/local1/m346kim/dl-fuzzing/code/dl-fuzzer/statistics/results/tensorflow/docker5_baseline.csv
# PyTorch
#python collect_error_msgs.py --workdir=/local1/m346kim/dl-fuzzing/expr/pytorch/docker_6_e5c96e/workdir/expect_ok_prev_ok --output=/local1/m346kim/dl-fuzzing/code/dl-fuzzer/statistics/results/pytorch/docker6_expect_ok.csv
#python collect_error_msgs.py --workdir=/local1/m346kim/dl-fuzzing/expr/pytorch/docker_7_e5c96e_no_pp/workdir/expect_ok_prev_ok --output=/local1/m346kim/dl-fuzzing/code/dl-fuzzer/statistics/results/pytorch/docker7_no_adapt.csv
#python collect_error_msgs.py --workdir=/local1/m346kim/dl-fuzzing/expr/pytorch/docker_7_e5c96e_no_pp/workdir/expect_exception_prev_ok --output=/local1/m346kim/dl-fuzzing/code/dl-fuzzer/statistics/results/pytorch/docker7_expect_exception.csv
#python collect_error_msgs.py --workdir=/local1/m346kim/dl-fuzzing/expr/pytorch/docker_8_e5c96e_no_constr/workdir/expect_ok_prev_ok --output=/local1/m346kim/dl-fuzzing/code/dl-fuzzer/statistics/results/pytorch/docker8_no_constr.csv
#python collect_error_msgs.py --workdir=/local1/m346kim/dl-fuzzing/expr/pytorch/docker_9_e5c96e_no_constr_no_pp/workdir/expect_ok_prev_ok --output=/local1/m346kim/dl-fuzzing/code/dl-fuzzer/statistics/results/pytorch/docker9_baseline.csv
# MXNet
#python collect_error_msgs.py --workdir=/local1/m346kim/dl-fuzzing/expr/mxnet/docker_4_9c92ca_no_pp/workdir/expect_ok_prev_ok --output=/local1/m346kim/dl-fuzzing/code/dl-fuzzer/statistics/results/mxnet/docker4_no_adapt.csv
#python collect_error_msgs.py --workdir=/local1/m346kim/dl-fuzzing/expr/mxnet/docker_4_9c92ca_no_pp/workdir/expect_exception_prev_ok --output=/local1/m346kim/dl-fuzzing/code/dl-fuzzer/statistics/results/mxnet/docker4_expect_exception.csv
#python collect_error_msgs.py --workdir=/local1/m346kim/dl-fuzzing/expr/mxnet/docker_5_9c92ca/workdir/expect_ok_prev_ok --output=/local1/m346kim/dl-fuzzing/code/dl-fuzzer/statistics/results/mxnet/docker5_expect_ok.csv
#python collect_error_msgs.py --workdir=/local1/m346kim/dl-fuzzing/expr/mxnet/docker_6_e5c96e_no_constr/workdir/expect_ok_prev_ok --output=/local1/m346kim/dl-fuzzing/code/dl-fuzzer/statistics/results/mxnet/docker6_no_constr.csv
#python collect_error_msgs.py --workdir=/local1/m346kim/dl-fuzzing/expr/mxnet/docker_7_e5c96e_no_constr_no_pp/workdir/expect_ok_prev_ok --output=/local1/m346kim/dl-fuzzing/code/dl-fuzzer/statistics/results/mxnet/docker7_baseline.csv
python collect_error_msgs.py --workdir=/local1/y2647li/dl-fuzzing/expr/mxnet/docker_14_3a5b96_eo/workdir/expect_ok_constr_adapt --output=/home/m346kim/dl-fuzzer/statistics/results/mxnet/docker14_expect_ok.csv
python collect_error_msgs.py --workdir=/local1/y2647li/dl-fuzzing/expr/mxnet/docker_15_3a5b96_base/workdir/expect_ok_no_constr_no_adapt --output=/home/m346kim/dl-fuzzer/statistics/results/mxnet/docker15_baseline.csv
python collect_error_msgs.py --workdir=/local1/y2647li/dl-fuzzing/expr/mxnet/docker_18_571d2f_eo_nat/workdir/expect_ok_constr_no_adapt --output=/home/m346kim/dl-fuzzer/statistics/results/mxnet/docker18_no_adapt.csv
python collect_error_msgs.py --workdir=/local1/y2647li/dl-fuzzing/expr/mxnet/docker_17_571d2f_nc/workdir/expect_ok_no_constr_adapt --output=/home/m346kim/dl-fuzzer/statistics/results/mxnet/docker17_no_constr.csv

#pushd /local1/m346kim/dl-fuzzing/code/dl-fuzzer/statistics/results/tensorflow > /dev/null
#echo "===================== Summarizing TensorFlow ===================="
#tail -5 docker8_expect_ok.csv > summary 
#tail -5 docker9_expect_exception.csv >> summary
#tail -5 docker5_baseline.csv >> summary
#tail -5 docker7_no_constr.csv >> summary
#tail -5 docker9_no_adapt.csv >> summary
#popd > /dev/null

#pushd /local1/m346kim/dl-fuzzing/code/dl-fuzzer/statistics/results/pytorch > /dev/null
#echo "===================== Summarizing PyTorch ===================="
#tail -5 docker6_expect_ok.csv > summary
#tail -5 docker7_expect_exception.csv >> summary
#tail -5 docker9_baseline.csv  >> summary
#tail -5 docker8_no_constr.csv >> summary
#tail -5 docker7_no_adapt.csv >> summary
#popd > /dev/null

pushd /home/m346kim/dl-fuzzer/statistics/results/mxnet > /dev/null
echo "===================== Summarizing MXNet ===================="
tail -5 docker14_expect_ok.csv > summary
#tail -5 docker4_expect_exception.csv >> summary
tail -5 docker15_baseline.csv >> summary
tail -5 docker17_no_constr.csv >> summary
tail -5 docker18_no_adapt.csv >> summary
popd > /dev/null
