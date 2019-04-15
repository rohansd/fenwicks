import tensorflow as tf

# todo: non-colab environment
from .utils.colab_tpu import TPU_ADDRESS
import datetime
import os


# todo: make validation set optional.
def get_tpu_estimator(n_trn, n_val, model_func, work_dir, ws_dir=None, ws_vars=None, trn_bs=128,
                      val_bs=None) -> tf.contrib.tpu.TPUEstimator:
    """
    Create a TPUEstimator object ready for training and evaluation.

    :param n_trn: Total number of training records.
    :param n_val: Total number of validation records.
    :param model_func: Model function for TPUEstimator. Can be built with `get_clf_model_func'.
    :param work_dir: Directory for storing intermediate files (such as checkpoints) generated during training.
    :param ws_dir: Directory containing warm start files, usually a pre-trained model checkpoint.
    :param ws_vars: List of warm start variables, usually from a pre-trained model.
    :param trn_bs: Batch size for training.
    :param val_bs: Batch size for validation. Default: all validation records in a single batch.
    :return: A TPUEstimator object, ready for training and evaluation.
    """
    steps_per_epoch = n_trn // trn_bs
    if val_bs is None:
        val_bs = n_val

    cluster = tf.contrib.cluster_resolver.TPUClusterResolver(TPU_ADDRESS)

    tpu_cfg = tf.contrib.tpu.TPUConfig(
        iterations_per_loop=steps_per_epoch,
        per_host_input_for_training=tf.contrib.tpu.InputPipelineConfig.PER_HOST_V2)

    now = datetime.datetime.now()
    work_dir = os.path.join(work_dir,
                            f'{now.year}-{now.month:02d}-{now.day:02d}-{now.hour:02d}:{now.minute:02d}:{now.second:02d}')

    trn_cfg = tf.contrib.tpu.RunConfig(cluster=cluster, model_dir=work_dir, tpu_config=tpu_cfg)

    ws = None if ws_dir is None else tf.estimator.WarmStartSettings(ckpt_to_initialize_from=ws_dir,
                                                                    vars_to_warm_start=ws_vars)

    return tf.contrib.tpu.TPUEstimator(model_fn=model_func, model_dir=work_dir, train_batch_size=trn_bs,
                                       eval_batch_size=val_bs, config=trn_cfg, warm_start_from=ws)


def get_clf_model_func(model_arch, opt_func, reduction=tf.losses.Reduction.MEAN):
    """
    Build a model function for a classification task to be used in a TPUEstimator, based on a given model architecture
    and optimizer. Both the model architecture and optimizer must be callables, not model or optimizer objects. The
    reason for this design is to ensure that all variables are created in the same Tensorflow graph, which is created
    by the TPUEstimator.

    :param model_arch: Model architecture: a callable that builds a neural net model.
    :param opt_func: Optimization function: a callable that returns an optimizer.
    :param reduction: Whether to average (`tf.losses.Reduction.MEAN`) or sum (`tf.losses.Reduction.SUM`) losses
                      for different training records. Default: average.
    :return: Model function ready for TPUEstimator.
    """

    def model_func(features, labels, mode, params):
        phase = 1 if mode == tf.estimator.ModeKeys.TRAIN else 0
        tf.keras.backend.set_learning_phase(phase)

        model = model_arch()
        logits = model(features)

        loss = tf.losses.sparse_softmax_cross_entropy(labels, logits, reduction=reduction)
        step = tf.train.get_or_create_global_step()

        opt = opt_func()
        opt = tf.contrib.tpu.CrossShardOptimizer(opt, reduction=reduction)

        # train_op = tf.contrib.training.create_train_op(loss, optimizer)
        grads_and_vars = opt.compute_gradients(loss)
        with tf.control_dependencies(model.get_updates_for(features)):
            train_op = opt.apply_gradients(grads_and_vars, global_step=step)

        classes = tf.math.argmax(logits, axis=-1)
        metric_func = lambda classes, labels: {'accuracy': tf.metrics.accuracy(classes, labels)}
        tpu_metrics = (metric_func, [classes, labels])

        return tf.contrib.tpu.TPUEstimatorSpec(mode=mode, loss=loss, predictions={"predictions": classes},
                                               train_op=train_op, eval_metrics=tpu_metrics)

    return model_func
