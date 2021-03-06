from data_helpers import *
from cnn_model_fn import *
import pandas as pd
import tensorflow as tf
from matplotlib import pyplot as plt


# Hyper parameters

class Tester():
    def __init__(self,test_path,embedding_size=8, batch_size=1, kernel_size=8,weights=1.0):
        self.weights = weights
        self.test_path = test_path
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

    def test(self, data, topk=1):
        # TODO 1 : Classifer
        classifier = tf.estimator.Estimator(
            model_fn=cnn_model_fn,
            model_dir="./model_without_cv/version1.0/top" + str(topk),
            params={
                'feature_columns': self.my_feature_columns,
                'topk': topk,
                'embedding_size': self.embedding_size,
                'batch_size': self.batch_size,
                'kernel_size': self.kernel_size,
                'weights': self.weights
            }
        )

        # TODO 2 : Evaluate
        evaluation = classifier.evaluate(
            input_fn=lambda: load_dataset(self.test_path,shuffle=False,repeat=False,batch_size=1),
            steps=None,
            hooks=[self.logging_hook]
        )
        print(evaluation)
        return evaluation

    def main(self,topk):
        # TODO 1 : initialize
        self.best_evaluation = {
            'F1-Score': 0.0,
            'Recall': 0.0,
            'Precision': 0.0,
            'Accuracy': 0.0,
            'AUC': 0.0
        }

        # TODO 2 : test in different topk
        print('top -',topk)
        evaluation = self.test(data)
        if evaluation['F1-Score'] > self.best_evaluation['F1-Score']:
            self.best_evaluation = evaluation

        print('The best evaluation is')

        # TODO 3 : print the best evaluation
        print(self.best_evaluation)

def main():
    tester = Tester(test_path='../data1/test.csv',weights=1.0)
    tester.main()


if __name__ == '__main__':
    # tf.logging.set_verbosity(tf.logging.INFO)
    main()
