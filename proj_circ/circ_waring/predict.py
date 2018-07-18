#!/usr/bin/python
# -*- coding:utf-8 -*-
import pickle
import xgboost as xgb

from sklearn.base import BaseEstimator, TransformerMixin

#from predict import StatsFeatures
#import feature
#from feature import StatsFeatures

#%%
# 加载训练好的模型
vectorizer_n = pickle.load(open("model/vectorizer_i.pickle", 'rb'))
selector = pickle.load(open("model/selector_i.pickle", 'rb'))

bst = xgb.core.Booster({'nthread':4}) #init model
bst.load_model("model/model_xgb_i.model") # load data

# 读取测试文件，分词预处理后的文件，每行一个新闻或微博，一定是内容，不是标题
def predict_corpus(corpus):
    X_test = vectorizer_n.transform(corpus)
    X_test = selector.transform(X_test)
   
    return bst.predict(xgb.core.DMatrix(X_test))

#%% 
class StatsFeatures(BaseEstimator, TransformerMixin):
    
    def __init__(self):
        self.neg = set()
        f = open("corpus/neg_words.txt","r+", encoding='UTF-8')
        for content in f:
            self.neg.add(content)
        f.close()

    def fit(self, X, y=None):
        return self

    def getcnt(self,x):
        return len(list(set(x)))

    def getnegcnt(self,x):
        negcnt = 0
        words = x.split()
        for w in words:
            if w in self.neg:
                negcnt = negcnt+1
        return negcnt
    
# =============================================================================
#        韩老师原始自定义特征计算函数
#     def transform(self, X):
#         return [[len(x),self.getcnt(x),self.getcnt(x)/len(x),self.getnegcnt(x),self.getnegcnt(x)/len(x)] for x in X]
# =============================================================================
#针对分词后部分新闻词数量<1   许欢 2018.06.19
    def transform(self, X):
        data = []
        for x in X:
            if len(x) == 0:
                length  = 1
            else :
                length = len(x)
            data.append([len(x),self.getcnt(x),self.getcnt(x)/length,
                         self.getnegcnt(x),self.getnegcnt(x)/length])            
        return data



if __name__ == '__main__':
    import pre
    import predict    

    record_ = [{'id': 1,
                'content': '一个恐怖的数字[怒]据国家癌症中心发布☞全国每天约有10000人确诊为癌症，平均每分钟就有7人确诊[怒]不过放心，癌症是可以治愈的，但……需要很多'}
               ]
    # predict
    corpus=[]
    files=open("corpus/test_new.txt","r", encoding="utf-8").readlines()
    for item in files:
        corpus.append(item.strip())
    contents = [pre.handle_content(i_content) for i_content in corpus]

    correlations = predict.predict_corpus(contents)
    print(correlations)
    

