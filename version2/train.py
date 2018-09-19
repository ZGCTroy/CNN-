from data_helpers import *
from cnn_model_fn import *
import pandas as pd
from sklearn.model_selection import StratifiedKFold
from sklearn.model_selection import KFold
from sklearn.model_selection import train_test_split
import tensorflow as tf
import numpy as np
from matplotlib import pyplot as plt
import os
os.environ["CUDA_VISIBLE_DEVICES"] = "0,1"
gpu_options = tf.GPUOptions(allow_growth = True)
sess = tf.Session(config=tf.ConfigProto(gpu_options = gpu_options))


# Hyper parameters

class Trainer():
    def __init__(self, datapath,weights=1.0, embedding_size=8, batch_size=1, kernel_size=8):
        self.weights = weights
        self.datapath = datapath
        self.best_evaluation = []
        self.embedding_size = embedding_size
        self.batch_size = batch_size
        self.kernel_size = kernel_size
        self.my_feature_columns = [
            tf.feature_column.embedding_column(
                categorical_column=tf.feature_column.categorical_column_with_identity(
                    key="code",
                    num_buckets=258,
                ),
                dimension=embedding_size,
            ),
        ]
        self.tensors_to_log = {"probabilities": "softmax_tensor"}
        self.logging_hook = tf.train.LoggingTensorHook(
            tensors=self.tensors_to_log,
            every_n_iter=1000
        )

    def train(self, data,nEpochs, topk,validation_input_fn):
        # TODO 1 : Data
        x = data['code'].values
        y = data['label'].values
        data_train = load_dataset(x, y, shuffle=True, repeat=False, batch_size=1)

        # TODO 2 : Classifer
        classifier = tf.estimator.Estimator(
            model_fn=cnn_model_fn,
            model_dir="./model/top1",
            params={
                'feature_columns': self.my_feature_columns,
                'topk': topk,
                'embedding_size': self.embedding_size,
                'batch_size': self.batch_size,
                'kernel_size': self.kernel_size,
                'weights': self.weights
            }
        )

        # TODO 3 : Train
        best_evaluation = {}
        for epoch in range(nEpochs):
            # Train
            print('epoch -', epoch)
            classifier.train(
                input_fn=lambda: data_train.make_one_shot_iterator().get_next(),
                steps=None,
                hooks=[self.logging_hook],
            )

            # Evaluate
            evaluation = classifier.evaluate(
                input_fn=lambda: validation_input_fn.make_one_shot_iterator().get_next(),
                steps=None,
                hooks=[self.logging_hook]
            )
            print(evaluation)
            if best_evaluation == {}:
                best_evaluation = evaluation
            elif evaluation['F1-Score'] > best_evaluation['F1-Score']:
                best_evaluation = evaluation
        return best_evaluation

    def main(self, topk,nEpochs):
        # TODO 1 : Data
        #data_validation = pd.read_csv('./data1/validation.csv')
        mylist = []
        for chunk in pd.read_csv('./data1/validation.csv', chunksize=200):
            mylist.append(chunk)

        data_validation = pd.concat(mylist, axis=0)
        del mylist
        x_validation = data_validation['code'].values
        y_validation = data_validation['label'].values
        validation_input_fn = load_dataset(x_validation, y_validation, shuffle=False, repeat=False, batch_size=1)

        #reader = pd.read_csv(self.datapath, iterator=True)
        list = []
        for chunk in pd.read_csv(self.datapath, chunksize=200):
            list.append(chunk)

        data = pd.concat(list, axis=0)
        del list
        self.best_evaluation = {
            'F1-Score': 0.0,
            'Recall': 0.0,
            'Precision': 0.0,
            'Accuracy': 0.0,
            'AUC': 0.0
        }

        # TODO 2 : train or test in different topk
        print('top -', topk)
        evaluation = self.train(data, nEpochs=nEpochs, topk=topk, validation_input_fn=validation_input_fn)
        if evaluation['F1-Score'] > self.best_evaluation['F1-Score']:
            self.best_evaluation = evaluation
       # loop = True
        #while loop:
           # try:
                #data = reader.get_chunk(size=100)  # size = None 表示全部取完，即只有1个chunk，即一次读取全部数据
                #evaluation = self.train(data,nEpochs=nEpochs,topk=topk,validation_input_fn=validation_input_fn)
                #if evaluation['F1-Score'] > self.best_evaluation['F1-Score']:
                    #self.best_evaluation = evaluation
            #except StopIteration:
               # loop = False

        print('The best evaluation is')
        print(self.best_evaluation)

def main():
    trainer = Trainer(datapath='./data1/train.csv',weights=1.0)
    trainer.main(topk=1,nEpochs=25)


if __name__ == '__main__':
    # tf.logging.set_verbosity(tf.logging.INFO)
    main()
