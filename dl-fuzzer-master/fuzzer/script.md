A bug I can reproduce from Audee:

~~~python
import tensorflow as tf
import numpy as np
from tensorflow.keras import Model, Input

kwargs={'max_value': 0.5761369157060329, 'negative_slope': 0.7845179761191806, 'threshold': None}
layer = tf.keras.layers.ReLU(**kwargs)

input= (np.random.randn(1,32,32,16)).astype(np.float32)
x = Input(batch_shape=input.shape)
y = layer(x)
model = Model(x, y)
model.predict(input)
~~~

Reason: `None` is converted to nan

example command:
target config: /Users/danning/Desktop/deepflaw/dl-fuzzer/doc_analysis/extract_constraint/tf/constraint_4/changed/tf.autograph.set_verbosity.yaml

dtype_config: /Users/danning/Desktop/deepflaw/dl-fuzzer/tensorflow/tensorflow_dtypes.yml

--max_iter=10
--gen_script
--obey
--timeout=10

If without constriant: use --ignore

python fuzzer-driver.py \
/Users/danning/Desktop/deepflaw/exp/code/DocTer-Ext/doc_analysis/extract_constraint/tf/constraint_layer/changed/tf.keras.layers.alphadropout.yaml \
../tensorflow/tensorflow_dtypes.yml \
--workdir=../../../workdir \
--max_iter=1 --obey  --gen_script  --timeout=10  > ./dn_workdir/workdir/out




/Users/danning/Desktop/deepflaw/exp/code/DocTer-Ext/doc_analysis/extract_constraint/tf/constraint_layer/changed/tf.keras.layers.alphadropout.yaml

