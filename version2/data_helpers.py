#!~/tensorflow/bin/python3
# -*- coding: utf-8 -*-
import os
import tensorflow as tf
import random
import numpy as np
# Just disables the warning, doesn't enable AVX/FMA
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

def _parse_line(features,label):
    features = tf.string_split([features], ',').values
    features = tf.string_to_number(features, out_type=tf.int32)
    features = tf.reshape(features, [-1, 1])
    x = {}
    x['code']=features
    return (x, label)

def load_dataset(x,y,shuffle=True,repeat=True,batch_size=1):
    dataset = tf.data.Dataset.from_tensor_slices((x, y))
    dataset = dataset.map(_parse_line)
    if shuffle :
        dataset = dataset.shuffle(1000)
    if repeat :
        dataset = dataset.repeat()
    dataset = dataset.batch(batch_size=batch_size)

    return dataset