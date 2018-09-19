from data_helpers import *
from cnn_model_fn import *
import pandas as pd
import tensorflow as tf
from matplotlib import pyplot as plt
import os
os.environ["CUDA_VISIBLE_DEVICES"] = "0,1"
gpu_options = tf.GPUOptions(allow_growth = True)
sess = tf.Session(config=tf.ConfigProto(gpu_options = gpu_options))


# Hyper parameters

class Tester():
    def __init__(self,datapath,embedding_size=8, batch_size=1, kernel_size=8,weights=1.0):
        self.weights = weights
        self.datapath = datapath
        self.embedding_size = embedding_size
        self.batch_size = batch_size
        self.kernel_size = kernel_size
        self.best_evaluation = {}
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
            every_n_iter=100
        )

    def test(self, data, topk):
        # TODO 1 : Data
        x = data['code'].values
        y = data['label'].values
        data_test = load_dataset(x, y, shuffle=False, repeat=False, batch_size=1)

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

        # TODO 3 : Evaluate
        evaluation = classifier.evaluate(
            input_fn=lambda: data_test.make_one_shot_iterator().get_next(),
            steps=None,
            hooks=[self.logging_hook]
        )
        print(evaluation)
        return evaluation

    def main(self,topk):
        # TODO 1 : Data
        #reader = pd.read_csv(self.datapath, iterator=True)
        mylist = []
        for chunk in pd.read_csv(self.datapath, chunksize=200):
            mylist.append(chunk)

        data = pd.concat(mylist, axis=0)
        del mylist
        self.best_evaluation = {
            'F1-Score': 0.0,
            'Recall': 0.0,
            'Precision': 0.0,
            'Accuracy': 0.0,
            'AUC': 0.0
        }

        # TODO 2 : test in different topk
        print('top -',topk)
        evaluation = self.test(data,topk)
        if evaluation['F1-Score'] > self.best_evaluation['F1-Score']:
            self.best_evaluation = evaluation
       #loop = True
        #while loop:
           # try:
                #data = reader.get_chunk(size=None)  # size = None 表示全部取完，即只有1个chunk，即一次读取全部数据
               # evaluation = self.test(data)
               # if evaluation['F1-Score'] > self.best_evaluation['F1-Score']:
                    #self.best_evaluation = evaluation
           # except StopIteration:
               # loop = False

        print('The best evaluation is')
        print(self.best_evaluation)

def main():
    tester = Tester(datapath='./data1/test.csv',weights=1.0)
    tester.main()


if __name__ == '__main__':
    # tf.logging.set_verbosity(tf.logging.INFO)
    main()
