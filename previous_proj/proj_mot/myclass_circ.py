#!/usr/bin/python
# -*- coding:utf-8 -*-
#%%
from sklearn.base import BaseEstimator, TransformerMixin
import logging.config
import numpy as np

# 日志记录
logging.config.fileConfig("conf/logger.conf")
logger = logging.getLogger("rotating")

#%% 
class StatsFeatures_cor(BaseEstimator, TransformerMixin):
    
    def __init__(self):
        self.neg = set()
        f = open("corpus/xizang_education.txt","r+", encoding='UTF-8')
        for content in f:
            self.neg.add(content.strip())
        f.close()
        
        self.company = set() # 公司
        f = open("corpus/xizang_school.txt","r+", encoding='UTF-8')
        for content in f:
            self.company.add(content.strip())
        f.close()

        self.regulators = set() # 监管机构及领导
        f = open("corpus/xizang_province.txt","r+", encoding='UTF-8')
        for content in f:
            self.regulators.add(content.strip())
        f.close()      
        
    def fit(self, X, y=None):
        return self

    def getcnt(self,x):    
        words = x.split()    
        return len(list(set(words)))

    def getnegcnt(self,x):
        negcnt = 0
        words = x.split()
        words_set=set(words)
        for w in words_set:
            if w in self.neg:
                negcnt = negcnt+1
        return negcnt
    
    def getorgcnttf(self,x):
        companycnt=0
        companytf=0
        regcnt = 0
        regtf = 0
        
        words = x.split()
        words_set=set(words)
        
        for w in words_set:
            if w in self.company:
                companycnt = companycnt+1
                companytf=companytf+words.count(w)
                
            if w in self.regulators:
                regcnt = regcnt+1
                regtf=regtf+words.count(w)            
        orgcnt = [companycnt, companytf, regcnt, regtf]        
        return orgcnt
    
    def transform(self, X):
        data = []
        for x in X:
            words = x.split()
            if len(words) == 0:
                length  = 1
            else :
                length = len(words)

            data.append([len(x),self.getcnt(x),self.getcnt(x)/length, 
                         self.getnegcnt(x),self.getnegcnt(x)/length] + self.getorgcnttf(x))    
        return data

#%%
class Statskeywords_cor(BaseEstimator, TransformerMixin):
    
    def __init__(self, topk = 100):
        self.topk = topk
        
        self.keywords = set()
        f = open("corpus/keywords.txt","r+", encoding='UTF-8')
        num = 0
        for content in f:
            if num < topk:
                self.keywords.add(content.strip().replace('\n', ''))
            num += 1
        f.close() 
    
    def fit(self, X, y=None):
        return self 
    
    def transform(self, X):
        '''
        文本中关键词的词频
        '''                        
        col_n = len(X)
        data = {keyword:np.zeros((1, col_n)).tolist()[0] for keyword in self.keywords}
        data['关键词的个数'] = np.zeros((1, col_n)).tolist()[0]
        for index, x in enumerate(X):
            words = x.split()
            words_set = set(words)  
            keycnt = 0
            for word in words_set:
                if word in self.keywords:
                    keycnt+=1
                    data[word][index] = words.count(word)
                data['关键词的个数'][index] = keycnt
        count_data = np.transpose(np.array([t for t in data.values()]))
        return count_data                



