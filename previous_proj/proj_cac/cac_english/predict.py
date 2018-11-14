#!/usr/bin/env python
# -*- coding: utf-8 -*-


from sklearn.base import BaseEstimator, TransformerMixin


class StatsFeatures(BaseEstimator, TransformerMixin):
    
    def __init__(self):
        pass

    def fit(self, X, y=None):
        return self

    def getcnt(self,x): 
        words = x.split()
        return len(list(set(words)))
    
    def transform(self, X):
        data = []
        for x in X:
            words = x.split()
            if len(words) == 0:
                length  = 1
            else :
                length = len(words)
            data.append([len(x),self.getcnt(x),self.getcnt(x)/length])            
        return data











