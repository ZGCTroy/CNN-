from preprocess_to_pandas import Preprocessor
from train import Trainer
from test import Tester


def main():
    # # TODO 1 : Preprocess
    #  preprocessor = Preprocessor()               # 创建预处理器
    #  preprocessor.merge_alldata_into_a_csv()     # 合并分散的多个文件到一个数据集,生成 origin_data.csv (不限制长度的)
    #  preprocessor.feature_process(t=1)           # 截取片段8900，使用数据增强 ，1个数据生成 t 个数据
    #  preprocessor.split_train_test(datapath='./data1/origin_data.csv') # 分割train and test

    # # TODO 2 : Train
    topk = 1
    trainer = Trainer(datapath='./data1/train.csv', weights=1.0)
    trainer.main(topk=topk,nEpochs=1)

    # # TODO 3 : Test
    # tester = Tester(datapath='./data1/test.csv', weights=1.0)
    # tester.main(topk=topk)


if __name__ == '__main__':
    main()
