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
# clf = pickle.load(open("model/clf_i.pickle", 'rb'))
bst = xgb.Booster({'nthread':4}) #init model
bst.load_model("model/model_xgb_i.model") # load data

# 读取测试文件，分词预处理后的文件，每行一个新闻或微博，一定是内容，不是标题
def predict_corpus(corpus):
    X_test = vectorizer_n.transform(corpus)
    X_test = selector.transform(X_test)
    # 预测输出的结果，1是相关，0是不相关
    # return clf.predict(X_test.toarray())
    return bst.predict(xgb.DMatrix(X_test))

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
    
    def transform(self, X):
        return [[len(x),self.getcnt(x),self.getcnt(x)/len(x),self.getnegcnt(x),self.getnegcnt(x)/len(x)] for x in X]


#%%
#def judge_negative(content):
#    """
#    判断文章正负面
#    :param content:
#    :return:
#    """       
#    tendency = chapter_pipeline.predict([content])
#    tendency = int(tendency[0])    
#    
#    return tendency

#%%
if __name__ == '__main__':
    import pre
    import predict    

    record_ = [{'id': 1,
                'content': '一个恐怖的数字[怒]据国家癌症中心发布☞全国每天约有10000人确诊为癌症，平均每分钟就有7人确诊[怒]不过放心，癌症是可以治愈的，但……需要很多'}
               ]
    # predict
    contents = [pre.handle_content(i_record['content']) for i_record in record_]

    correlations = predict.predict_corpus(contents)
    print(correlations)
    
#    content = record_[0]['content']
#    tendency = predict.judge_negative(content)
#    
#    print(tendency)
