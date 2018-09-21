#!~/tensorflow/bin/python3
# -*- coding: utf-8 -*-
import os
import tensorflow as tf
import random
import numpy as np
# Just disables the warning, doesn't enable AVX/FMA
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

FIELD_DEFAULTS = [[""],[0],[0.0]]
COLUMNS = ['code','label','length']

def _parse_line(line):
    # Decode the line into its fields
    fields = tf.decode_csv(line,FIELD_DEFAULTS)

    # Pack the result into a dictionary
    features = dict(zip(COLUMNS,fields))

    # Separate  the label from the features
    label = features.pop('label')

    features['code'] = tf.string_split([features['code']], ',').values
    features['code'] = tf.string_to_number(features['code'], out_type=tf.int32)
    features['code'] = tf.reshape(features['code'], [-1, 1])
    return (features, label)

def load_dataset(filepath,shuffle=True,repeat=True,batch_size=1):
    dataset = tf.data.TextLineDataset(filepath).skip(1)
    dataset = dataset.map(_parse_line)
    if shuffle :
        dataset = dataset.shuffle(1000)
    if repeat :
        dataset = dataset.repeat()
    dataset = dataset.batch(batch_size=batch_size)
    return dataset

def main():
    dataset = load_dataset("../data1/test.csv",shuffle=False,repeat=False,batch_size=1)
    print()
    sess = tf.Session()
    print(sess.run(dataset))

if __name__=='__main__':
    main()