# EAGLE: Creating Equivalent Graphs to Test Deep Learning Libraries

This repository contains codes for reproducing bugs in the paper EAGLE: Creating Equivalent Graphs to Test Deep Learning Libraries. If a specific input is needed to reproduce a bug, the input file is provided in the same directory as the reproducing code.

## The list of bugs

### TensorFlow

|Rule|API|New|Link|
|---|---|---|---|
| Rule 1  | [tf.math.xdivy](tensorflow/rule_1/rule_1_tf_bug_1.ipynb)                                    | yes | [Link](https://github.com/tensorflow/tensorflow/issues/51643) |
| Rule 1  | [tf.realdiv](tensorflow/rule_1/rule_1_tf_bug_2.ipynb)                                       | yes | [Link](https://github.com/tensorflow/tensorflow/issues/51643) |
| Rule 1  | [tf.nn.compute_average_loss](tensorflow/rule_1/rule_1_tf_bug_3.ipynb)                       | yes | [Link](https://github.com/tensorflow/tensorflow/issues/51643) |
| Rule 1  | [tf.math.sign](tensorflow/rule_1/rule_1_tf_bug_4.ipynb)                                     | yes | fixed in 2.7 |
| Rule 1  | [tf.math.log1p](tensorflow/rule_1/rule_1_tf_bug_5.ipynb)                                    | yes | fixed in 2.7 |
| Rule 1  | [tf.linalg.matrix_rank](tensorflow/rule_1/rule_1_tf_bug_6.ipynb)                            | yes | fixed in 2.7 |
| Rule 1  | [tf.image.non_max_suppression](tensorflow/rule_1/rule_1_tf_bug_7.ipynb)                     | yes | [Link](https://github.com/tensorflow/tensorflow/issues/54264) |
| Rule 1  | [tf.math.count_nonzero](tensorflow/rule_1/rule_1_tf_bug_8.ipynb)                            | yes | fixed in 2.7 |
| Rule 1  | [tf.math.reduce_sum](tensorflow/rule_1/rule_1_tf_bug_9.ipynb)                               | yes | [Link](https://github.com/tensorflow/tensorflow/issues/54265) |
| Rule 1  | [tf.math.reduce_mean](tensorflow/rule_1/rule_1_tf_bug_10.ipynb)                             | yes | [Link](https://github.com/tensorflow/tensorflow/issues/54265) |
| Rule 8  | [tf.keras.layers.ReLU](tensorflow/rule_8/rule_8_tf_bug_1.ipynb)                             | yes | [Link](https://github.com/keras-team/keras/issues/15009) |
| Rule 8  | [tf.keras.layers.BatchNormalization](tensorflow/rule_8/rule_8_tf_bug_2.ipynb)               | yes | [Link](https://github.com/keras-team/keras/issues/15009) |
| Rule 8  | [tf.keras.layers.Dropout](tensorflow/rule_8/rule_8_tf_bug_3.ipynb)                          | no | [Link](https://github.com/tensorflow/tensorflow/issues/25980) |
| Rule 10 | [tf.keras.layers.Bidirectional](tensorflow/rule_10/rule_10_tf_bug_1.ipynb)                  | no | [Link](https://github.com/tensorflow/tensorflow/issues/39635) |
| Rule 13 | [tfio.image.encode_gif, tf.io.decode_gif](tensorflow/rule_13/rule_13_tf_bug_1.ipynb)        | yes | [Link](https://github.com/tensorflow/tensorflow/issues/54266) |
| Rule 14 | [tf.image.extract_glimpse](tensorflow/rule_14/rule_14_tf_bug_1.ipynb)                       | no | [Link](https://github.com/tensorflow/tensorflow/issues/38545) |
| Rule 16 | [tf.keras.Sequential.from_config](tensorflow/rule_16/rule_16_tf_bug_1.ipynb)                | no | [Link](https://github.com/tensorflow/tensorflow/issues/40981) |
| Rule 16 | [tf.keras.models.save](tensorflow/rule_16/rule_16_tf_bug_2.ipynb)                           | no | [Link](https://github.com/tensorflow/tensorflow/issues/42459) |

### PyTorch

|Rule|API|New|Link|
|---|---|---|---|
| Rule 8  | [torch.sspaddmm](pytorch/rule_8/rule_8_pt_bug_1.ipynb)                            | no | [Link](https://github.com/pytorch/pytorch/issues/45113) |
| Rule 8  | [torch.smm](pytorch/rule_8/rule_8_pt_bug_2.ipynb)                                 | no | [Link](https://github.com/pytorch/pytorch/issues/45113) |
| Rule 8  | [torch.sspaddmm](pytorch/rule_8/rule_8_pt_bug_3.ipynb) (crash)                    | no | fixed in 1.8 |
| Rule 8  | [torch.smm](pytorch/rule_8/rule_8_pt_bug_4.ipynb) (crash)                         | no | fixed in 1.8 |
| Rule 12  | [torch.fmod](pytorch/rule_12/rule_12_pt_bug_1.ipynb)                             | no | [Link](https://github.com/pytorch/pytorch/issues/47779) |
| Rule 12  | [torch.remainder](pytorch/rule_12/rule_12_pt_bug_2.ipynb)                        | no | [Link](https://github.com/pytorch/pytorch/issues/47779) |
| Rule 12  | [torch.nn.functional.cosine_similarity](pytorch/rule_12/rule_12_pt_bug_3.ipynb)  | no | [Link](https://github.com/pytorch/pytorch/issues/61454) |








