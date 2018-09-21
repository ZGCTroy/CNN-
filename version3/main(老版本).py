from data_helpers import *
from cnn_model_fn import *
import pandas as pd
from sklearn.model_selection import StratifiedKFold
from sklearn.model_selection import KFold
import tensorflow as tf
import numpy as np

# Hyper parameters
embedding_size = 8
batch_size = 1
kernel_size = 8
k_num = 1

def main():
    # TODO 1 : read data from a csv
    data = pd.read_csv('./data1/data1_feature_processed_8900.csv')

    # TODO 2 : Feature_column
    my_feature_columns = [
        tf.feature_column.embedding_column(
            categorical_column=tf.feature_column.categorical_column_with_identity(
                key="code",
                num_buckets=258,
            ),
            dimension=embedding_size,
        ),
    ]

    # TODO 3 : Logging
    tensors_to_log = {"probabilities": "softmax_tensor"}
    logging_hook = tf.train.LoggingTensorHook(
        tensors=tensors_to_log,
        every_n_iter=100
    )


    # TODO 4 : train
    best_prec = []
    best_recall = []
    best_fscore = []
    best_accuracy = []
    x = data['code'].values
    y = data['label'].values
    k = 0
    for train_index, test_index in KFold(n_splits=10).split(x):
        k += 1
        print('k = ',k)

        # split the train and test
        x_train, x_test = x[train_index], x[test_index]
        y_train, y_test = y[train_index], y[test_index]
        data_train = load_dataset(x_train, y_train, shuffle=True, repeat=False, batch_size=1)
        data_test = load_dataset(x_test, y_test, shuffle=False, repeat=False, batch_size=1)
        best_fscore.append(0.0)
        best_recall.append(0.0)
        best_prec.append(0.0)
        best_accuracy.append(0.0)

        # set a new classifier
        classifier = tf.estimator.Estimator(
            model_fn=cnn_model_fn,
            model_dir="./model/version1.0/model" + str(k),
            params={
                'feature_columns': my_feature_columns,
                'topk': 1,
                'embedding_size': embedding_size,
                'batch_size': batch_size,
                'kernel_size': kernel_size
            }
        )

        # train
        for epoch in range(0, 75):
            # Train
            classifier.train(
                input_fn= lambda : data_train.make_one_shot_iterator().get_next(),
                steps=None,
                hooks=[logging_hook],
            )

            # Evaluate
            evaluation = classifier.evaluate(
                input_fn= lambda :data_test.make_one_shot_iterator().get_next(),
                steps=None,
                hooks=[logging_hook]
            )
            print('classifier = ',k,'epoch = ',epoch)
            print('evaluation = ',evaluation)

            # get the power of model
            TP = evaluation['TP']
            FP = evaluation['FP']
            TN = evaluation['TN']
            FN = evaluation['FN']
            prec = TP/(TP+FP)
            recall = TP/(TP+FN)
            fscore = 2*TP/(2*TP+FP+FN)
            accuracy = evaluation['accuracy']
            if fscore > best_fscore[k-1]:
                best_prec[k-1] = prec
                best_fscore[k-1] = fscore
                best_accuracy[k-1] = accuracy
                best_recall[k-1] = recall
            if k == 1:
                break



    # TODO 5 : print the final power of model
    print()
    print('The average fscore of this model is ',np.average(best_fscore))
    print('The average recall of this model is ', np.average(best_recall))
    print('The average accuracy of this model is ', np.average(best_accuracy))
    print('The average prec of this model is ', np.average(best_prec))
    print()
    print('The max fscore of this model is ', np.max(best_fscore))
    print('The max recall of this model is ', np.max(best_recall))
    print('The max accuracy of this model is ', np.max(best_accuracy))
    print('The max prec of this model is ', np.max(best_prec))



if __name__ == '__main__':
    #tf.logging.set_verbosity(tf.logging.INFO)
    main()
