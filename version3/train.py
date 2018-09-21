from data_helpers import *
from cnn_model_fn import *
import pandas as pd
from sklearn.model_selection import StratifiedKFold
from sklearn.model_selection import KFold
from sklearn.model_selection import train_test_split
import tensorflow as tf
import numpy as np
from matplotlib import pyplot as plt


# Hyper parameters

class Trainer():
    def __init__(self, train_path,validation_path,weights=1.0, embedding_size=8, batch_size=1, kernel_size=8):
        self.weights = weights
        self.train_path = train_path
        self.validation_path = validation_path
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
            every_n_iter=100
        )

    def train(self, nEpochs, topk):
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
        
        # TODO 2 : Train
        best_evaluation = {}
        train_dataset = load_dataset(filepath=self.train_path,shuffle=True,repeat=None,batch_size=1)
        validation_dataset = load_dataset(filepath=self.validation_path, shuffle=False, repeat=None, batch_size=1)
        for epoch in range(nEpochs):
            # Train
            classifier.train(
                input_fn=lambda: train_dataset.make_one_shot_iterator().get_next(),
                steps=None,
                hooks=[self.logging_hook],
            )

            # Evaluate
            evaluation = classifier.evaluate(
                input_fn=lambda: validation_dataset.make_one_shot_iterator().get_next(),
                steps=None,
                hooks=[self.logging_hook],

            )
            print(evaluation)
            if best_evaluation == {}:
                best_evaluation = evaluation
            elif evaluation['F1-Score'] > best_evaluation['F1-Score']:
                best_evaluation = evaluation
        return best_evaluation

    def main(self, topk,nEpochs):
        # TODO 1 : evaluation
        self.best_evaluation = {
            'F1-Score': 0.0,
            'Recall': 0.0,
            'Precision': 0.0,
            'Accuracy': 0.0,
            'AUC': 0.0
        }

        # TODO 2 : train or test in different topk
        print('top -', topk)
        evaluation = self.train(nEpochs=nEpochs,topk=topk)
        if evaluation['F1-Score'] > self.best_evaluation['F1-Score']:
            self.best_evaluation = evaluation


        # TODO 3 : print the best evaluation
        print('The best evaluation is')
        print(self.best_evaluation)

def main():
    trainer = Trainer(train_path='../data1/train.csv',validation_path='../data1/validation.csv',weights=1.0)
    trainer.main(topk=1,nEpochs=1)


if __name__ == '__main__':
    tf.logging.set_verbosity(tf.logging.INFO)
    main()
