#!/bin/bash


for i in {1..5};do
  mkdir "workdir$i"
  pushd "workdir$i" > /dev/null
  mkdir "ok"
  mkdir "ee"
  mkdir "base"
  popd > /dev/null
  modes=( "ok" "ee" "base" )
  for m in ${modes[@]};do
    workdir="workdir$i/$m"
    args=(
      doc_analysis/extract_constraint/tf/constraint_4/changed/tf.quantization.quantize_and_dequantize.yaml
      tensorflow/tensorflow_dtypes.yml
      --max_iter=1000
      --cluster
      --dist_threshold=0.5
      --dist_metric=jaccard
      --adapt_to=prev_ok
      --fuzz_optional
      --timeout=10
      --gen_script
      --workdir="$workdir"
    )
    if [[ "$m" == "ok" || "$m" == "base" ]];then
      args+=( --obey )
    fi
    if [ "$m" == "base" ];then
      args+=( --ignore --consec_fail=2000 )
    fi
    python fuzzer/fuzzer-driver.py "${args[@]}" > "$workdir"/output_log
  done
done
