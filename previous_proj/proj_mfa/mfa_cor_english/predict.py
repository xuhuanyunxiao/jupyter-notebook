#!/usr/bin/env python
# -*- coding: utf-8 -*-


from sklearn.base import BaseEstimator, TransformerMixin


class StatsFeatures(BaseEstimator, TransformerMixin):
    
    def __init__(self):
        pass

    def fit(self, X, y=None):
        return self

    def getcnt(self,x):        
        return len(list(set(x)))
    
    def transform(self, X):
        data = []
        for x in X:
            if len(x) == 0:
                length  = 1
            else :
                length = len(x)
            data.append([len(x),self.getcnt(x),self.getcnt(x)/length])            
        return data











