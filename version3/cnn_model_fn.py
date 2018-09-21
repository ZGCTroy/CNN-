import tensorflow as tf

# Hyper parameters


def cnn_model_fn(features, labels, mode, params):
    # TODO 1: Input Layer
    embedding_layer = tf.feature_column.input_layer(
        features,
        params['feature_columns'],
    )
    input = tf.reshape(
        embedding_layer,
        shape=[params['batch_size'], -1, params['embedding_size'], 1],
        name="Input"
    )

    # TODO 2: Convolutional Layer && Pooling Layer && Activation Layer
    conv1 = tf.layers.conv2d(
        inputs=input,
        filters=64,
        kernel_size=[params['kernel_size'], params['embedding_size']],
        padding='valid',
        activation=tf.nn.relu,
        name="conv1"
    )
    # pool1 = tf.layers.max_pooling2d(
    #     inputs=conv1,
    #     pool_size=[kernel_size, 1],
    #     strides=1,
    #     padding='valid',
    #     name="pool1"
    # )
    # reshape_pool1 = tf.transpose(pool1,[0,1,3,2])
    # conv2 = tf.layers.conv2d(
    #     inputs=reshape_pool1,
    #     filters=64,
    #     kernel_size=[kernel_size, nConvFilters],
    #     padding='valid',
    #     activation=tf.nn.relu,
    #     name="conv2"
    # )
    # pool2 = tf.layers.max_pooling2d(
    #     inputs=conv2,
    #     pool_size=[kenrnel, 1],
    #     padding='valid',
    #     strides=1,
    #     name="pool2"
    # )

    # TODO 3: Dense Layer && Dropout Layer
    # max_over_time = tf.reduce_max(conv1, axis=1, name="max_over_time")
    transpose1 = tf.transpose(
        conv1,
        [0, 3, 2, 1],
        name="transpose1"
    )
    # transpose1 = tf.reshape(transpose1,[64,-1])
    max_over_time = tf.nn.top_k(transpose1, params['topk']).values
    last_reshape = tf.reshape(
        max_over_time, [1, 64 * params['topk']], name="last_reshape"
    )
    dense1 = tf.layers.dense(
        inputs=last_reshape,
        units=16,
        activation=tf.nn.relu,
        name="dense1"
    )
    # dropout1 = tf.layers.dropout(
    #     inputs=dense1,
    #     rate=0.5,
    #     training=mode == tf.estimator.ModeKeys.TRAIN,
    #     name="dropout1",
    # )
    # dense2 = tf.layers.dense(
    #     inputs=dropout1,
    #     units=512,
    #     activation=tf.nn.relu,
    #     trainable=True,
    #     reuse=False,
    #     name="dense2"
    # )
    # dropout2 = tf.layers.dropout(
    #     inputs=dense2,
    #     rate=0.5,
    #     training=mode == tf.estimator.ModeKeys.TRAIN,
    #     name="dropout2",
    # )

    # TODO 4: Logits Layer
    logits = tf.layers.dense(
        inputs=dense1,
        units=2,
        reuse=False,
        name="logits"
    )

    # TODO 5: Predict
    predictions = {
        "classes": tf.argmax(input=logits, axis=1),
        "probabilities": tf.nn.softmax(logits, name="softmax_tensor")
    }
    if mode == tf.estimator.ModeKeys.PREDICT:
        return tf.estimator.EstimatorSpec(mode=mode, predictions=predictions)

    # TODO 6: Train
    loss = tf.losses.sparse_softmax_cross_entropy(labels=labels, logits=logits, weights=params['weights'])
    tf.summary.scalar('loss', loss)
    if mode == tf.estimator.ModeKeys.TRAIN:
        optimizer = tf.train.GradientDescentOptimizer(learning_rate=0.001)
        train_op = optimizer.minimize(
            loss=loss, global_step=tf.train.get_global_step()
        )
        return tf.estimator.EstimatorSpec(mode=mode, loss=loss, train_op=train_op)

    # TODO 7 : Evaluation
    prec = tf.metrics.precision(labels=labels, predictions=predictions["classes"])
    recall = tf.metrics.recall(labels=labels, predictions=predictions["classes"])
    f1_score = (
        2 * prec[0] * recall[0] / (prec[0] + recall[0]),
        2 * prec[1] * recall[1] / (prec[1] + recall[1])
    )
    eval_metric_ops = {
        "Recall": recall,
        "Precision": prec,
        "F1-Score": f1_score,
        "AUC": tf.metrics.auc(
            labels=labels, predictions=predictions["classes"]
        ),
        "Accuracy": tf.metrics.accuracy(
            labels=labels, predictions=predictions["classes"]
        )
    }
    return tf.estimator.EstimatorSpec(mode=mode, loss=loss, eval_metric_ops=eval_metric_ops)
