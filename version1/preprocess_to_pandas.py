import pandas as pd
import os
import random
import numpy as np
from sklearn.model_selection import train_test_split
class Preprocessor():
    def __init__(self,max_sequence_length=8900,min_sequence_length=100,pos_data_path = './data1/pos',neg_data_path = './data1/neg'):
        self.max_sequence_length = max_sequence_length
        self.min_sequence_length = min_sequence_length
        self.codes = []
        self.labels = []
        self.words_num = []
        self.pos_data_path = pos_data_path
        self.neg_data_path = neg_data_path
        self.pos_num = 0
        self.neg_num = 0

    # 处理单个程序，以字符串的形式返回程序代码，如 '000，001，023，045，000，123，100，000，'
    def process_single_file(self,filepath,label):
        with open(filepath) as f:
            code = ""
            for line in f:
                code += "000,"
                for k in range(0,len(line)-2, 2):
                    num = str(int(line[k:k+2], 16)+1)
                    if len(num) == 1:
                        code += "00" + num + ','
                    if len(num) == 2:
                        code += "0" + num + ','
        words_num = len(code)/4
        if words_num >= self.min_sequence_length:
            self.codes.append(code)
            self.words_num.append(words_num)
            self.labels.append(label)
            return 1
        return 0

    # 将代码长度至少为min_sequence_length单个程序集合成整体数据集为DataFrame形式,{'label':int,'words_num':int,'code':string},存储为csv
    def merge_alldata_into_a_csv(self):
        # TODO 1 : process the single positive program
        for filename in os.listdir(self.pos_data_path):
            filepath = os.path.join(self.pos_data_path, filename)
            self.pos_num += self.process_single_file(filepath,0)

        # TODO 2 : process the single negative program
        for filename in os.listdir(self.neg_data_path):
            filepath = os.path.join(self.neg_data_path, filename)
            self.neg_num += self.process_single_file(filepath,1)

        # TODO 3 : combine to a DataFrame and save to a csv
        origin_data = pd.DataFrame({
            'label':self.labels,
            'words_num':self.words_num,
            'code':self.codes
        })
        origin_data.to_csv('./data1/origin_data.csv',index=False)

        # TODO 4 : print information
        print(origin_data.info())
        print(origin_data.describe())
        print(origin_data)
        print('the number of positive data is ',self.pos_num)
        print('the number of negative data is ', self.neg_num)

    # 特征处理，对任意长的code，设置限制最长为8900
    def feature_process(self,t=1):
        # TODO 1 : read data from a csv
        data = pd.read_csv('./data1/origin_data.csv')

        # TODO 2 : shuffle the data
        data = data.sample(frac=1).reset_index(drop=True)

        # TODO 3 : reduce the number of code below min_sequence_length
        labels = data['label'].values
        codes = data['code'].values
        words_num = data['words_num'].values
        codes_processed = []
        label_processed = []
        words_num_processed = []

        # 随机截取
        for id in range(len(labels)):
            code = codes[id]
            for i in range(min(int(1+words_num[id]/self.max_sequence_length),t)):
                if words_num[id] > self.max_sequence_length:
                    start_pos = 4*random.randint(0,words_num[id]-self.max_sequence_length-1)
                    code = codes[id][start_pos:start_pos+4*self.max_sequence_length]
                codes_processed.append(code)
                label_processed.append(labels[id])
                words_num_processed.append(words_num[id])

        # TODO 4 : save to csv
        data_feature_processed = pd.DataFrame({
            'label':label_processed,
            'words_num':words_num_processed,
            'code':codes_processed
        })
        data_feature_processed = data_feature_processed.sample(frac=1).reset_index(drop=True)
        data_feature_processed.to_csv('./data1/data_feature_processed_'+str(self.max_sequence_length)+'.csv',index=False)

    def split_train_test(self,datapath):
        data = pd.read_csv(datapath)
        data_train,data_test = train_test_split(data,train_size=0.75,test_size=0.25)
        data_train,data_validation = train_test_split(data_train,train_size=0.7,test_size=0.3)
        data_train.to_csv('./data1/train.csv',index=False)
        data_validation.to_csv('./data1/validation.csv',index=False)
        data_test.to_csv('./data1/test.csv',index=False)

def main():
    # # TODO 1 : 创建预处理器
    preprocessor = Preprocessor()
    #
    # # TODO 2 : 合并分散的多个文件到一个数据集,生成 origin_data.csv (不限制长度的)
    # preprocessor.merge_alldata_into_a_csv()
    #
    # # TODO 3 : 截取片段8900，使用数据增强 ，1个数据生成 t 个数据
    # preprocessor.feature_process(t=1)

    # TODO 4 : 分割train and test
    preprocessor.split_train_test(datapath='./data1/origin_data.csv')


if __name__ == '__main__':
    main()

