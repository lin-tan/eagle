TF30_5219278_eo/workdir/expect_ok_constr/tf.register_tensor_conversion_function.yaml_workdir/out
KeyError: 'There are no fields in dtype float32.'


torch.cuda.synchronize.yaml  param.py line687


only ee
tf.random.all_candidate_sampler.yaml
################# 114/1000 begin #################
<<< DEBUG Parameter to generate: ['unique', 'num_sampled', 'num_true', 'true_classes'] >>>
<<< DEBUG selected ['num_true'] to violate constraints >>>
<<< DEBUG selected ['unique'] to mutate  >>>
<<< DEBUG Need to follow constraint. Will not mutate bool type >>>
<<< DEBUG trying to violate range constraint for num_true >>>
<<< DEBUG selected range [20, 255] >>>
============================================
Saving seed to file /home/workdir/expect_exception_constr/tf.random.all_candidate_sampler.yaml_workdir/a1db29dbcd0a342049e6981e9c399f312f962ec6.p
============================================
Error: expected to have exception but got no exception


################# 371/1000 begin #################
<<< DEBUG Parameter to generate: ['name', 'seed', 'unique', 'num_sampled', 'num_true', 'true_classes'] >>>
<<< DEBUG selected ['true_classes'] to violate constraints >>>
<<< DEBUG trying to violate dtype constraint for true_classes >>>
<<< DEBUG selected tf.string to violate dtype constraint >>>
<<< DEBUG trying to violate ndim constraint for true_classes >>>
<<< DEBUG selected 1 as ndim to violate constraint >>>
Warning: trying to generate string; will not generate multi-dimensional string
============================================
Saving seed to file /home/workdir/expect_exception_constr/tf.random.all_candidate_sampler.yaml_workdir/da983a193613a58811d22e42745fd0c8fb1e04be.p
============================================


################## 4/1000 begin ##################
<<< DEBUG Parameter to generate: ['name', 'batch_dims', 'axis', 'indices', 'params'] >>>
<<< DEBUG selected ['batch_dims'] to violate constraints >>>
Warning: trying to generate string; will not generate multi-dimensional string
<<< DEBUG trying to violate dtype constraint for batch_dims >>>
<<< DEBUG selected tf.bool to violate dtype constraint >>>
============================================
Saving seed to file /Users/danning/Desktop/deepflaw/exp2/workdir/xxx/e5b1caf5a62bf34f3cb6d02471c86907da1bcb3b.p 
============================================



<<< DEBUG Parameter to generate: ['name', 'unique', 'num_sampled', 'num_true', 'true_classes'] >>>
<<< DEBUG selected ['unique'] to violate constraints >>>
<<< DEBUG trying to violate dtype constraint for unique >>>
<<< DEBUG selected tf.float64 to violate dtype constraint >>>
<<< DEBUG trying to violate ndim constraint for unique >>>
<<< DEBUG selected 4 as ndim to violate constraint >>>
============================================
Saving seed to file /home/workdir/expect_exception_constr/tf.random.all_candidate_sampler.yaml_workdir/dc5c0cd9957480c3c49c189d990b502305f3dce2.p


################# 94/1000 begin ##################
<<< DEBUG Parameter to generate: ['name', 'unique', 'num_sampled', 'num_true', 'true_classes'] >>>
<<< DEBUG selected ['num_sampled'] to violate constraints >>>
<<< DEBUG trying to violate dtype constraint for num_sampled >>>
<<< DEBUG selected tf.string to violate dtype constraint >>>
Warning: trying to generate string; will not generate multi-dimensional string
============================================
Saving seed to file /home/workdir/expect_exception_constr/tf.random.all_candidate_sampler.yaml_workdir/c5c9c17ec114809bcccaf29b2e50ddf7a819799c.p

