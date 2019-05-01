#!/usr/bin/python
# -*- coding: utf-8 -*-

import numpy as np
from scipy.sparse import csr_matrix


def get_word_frequency(cut_matrix):
    """ 获得词频 """
    from sklearn.feature_extraction.text import CountVectorizer
    vectorizer = CountVectorizer(token_pattern=r"(?u)\b[^@]+\b", lowercase=False)
    frequency_matrix = vectorizer.fit_transform(cut_matrix)
    word_frequency = frequency_matrix.toarray().sum(axis=0)
    feature_name = vectorizer.get_feature_names()
    feature_frequency = zip(feature_name, word_frequency)
    feature_frequency = sorted(feature_frequency, key=lambda t: t[1], reverse=True)
    return feature_frequency


def getTfidf(cutResult,onlyClusterFlag,is_idf=None):
    # type: (object, object) -> object
    from sklearn.feature_extraction.text import CountVectorizer
    from sklearn.feature_extraction.text import TfidfTransformer
    #CountVectorizer类 得到词频矩阵：索引 词频 特征名
    vectorizer=CountVectorizer(token_pattern=r"(?u)\b[^@]+\b",lowercase=False)
    wordFrequencyMatrix = vectorizer.fit_transform(cutResult)
    if(onlyClusterFlag):
        if is_idf:
            tfidf = TfidfTransformer()
            tfidfMatrix = tfidf.fit_transform(wordFrequencyMatrix)
            return tfidfMatrix
        else:
            return wordFrequencyMatrix
    else:

        #TfidfTransformer类 得到tfidf矩阵
        tfidf = TfidfTransformer()
        tfidfMatrix = tfidf.fit_transform(wordFrequencyMatrix)

        #特征名称 下标对应特征索引
        featureName = vectorizer.get_feature_names()
        weightArray = tfidfMatrix.toarray()
        #求featureName权重和
        weightSum = weightArray.sum(axis=0)
        #[0,1]归一化
        from sklearn.preprocessing import MinMaxScaler
        weight = MinMaxScaler().fit_transform(weightSum.reshape(-1, 1)).round(decimals=3)[:,0]
        #拉链操作
        featureAndweight = zip(featureName, weight)
        #过滤
        filterResult = filter(lambda (x, y): y > 0, featureAndweight)
        #weightDict
        weightDict=dict((name, str(value)) for name, value in filterResult)
        #权重降序排序 这里不做排序，因为传到java端还是乱序
        #Dict降序排序 featureAndweight.sort(key=lambda tup: tup[1], reverse=True)
        # sorted(weightDict.items(), key=lambda n:n[1],reverse=True)
        return weightDict


def getFreqPosWeight(cutRF, posMap):
    from sklearn.feature_extraction.text import CountVectorizer
    #特征 索引
    vectorizer=CountVectorizer(token_pattern=r"(?u)\b[^@]+\b",lowercase=False)
    #词频矩阵 每个title中每个词出现的次数
    wordFrequencyMatrix = vectorizer.fit_transform(cutRF)
    # 统计词频
    wordFreqSum = wordFrequencyMatrix.toarray().sum(axis=0)
    #特征
    featureName = vectorizer.get_feature_names()
    #TFIDF矩阵
    from sklearn.feature_extraction.text import TfidfTransformer
    tfidf = TfidfTransformer()
    tfidfMatrix = tfidf.fit_transform(wordFrequencyMatrix)
    #权重大小
    weightSum = tfidfMatrix.toarray().sum(axis=0)
    # [0,1]归一化
    from sklearn.preprocessing import MinMaxScaler
    weight = MinMaxScaler().fit_transform(weightSum.reshape(-1, 1)).round(decimals=3)[:,0]
    # 拉链操作
    featureAndweight = zip(featureName, weight)
    # 词频
    freqTuple = zip(featureName,wordFreqSum)
    freqDict = dict(freqTuple)
    # 过滤
    filterResult = filter(lambda (x, y): y > 0, featureAndweight)
    # for f in featureAndweight:
    #     print f[0],":",f[1]
    # weightDict
    weightDict={}
    for name, value in filterResult:
        #词性
        pos=posMap.get(name)
        #词频
        #freq=""
        #for ff in zip(featureName,wordFreqSum):
            #if name==ff[0]:
                #freq=str(ff[1])
        freq = freqDict[name]
        #权重
        wei=str(value)
        r=wei+"^A"+str(pos)+"^A"+str(freq)
        if pos!=None:
            weightDict.setdefault(name,r)
    # for k in weightDict.keys():
    #     print k,":",weightDict[k]
    return weightDict


def construct_matrix(word_weight_lists):
    """
    构建矩阵, 用于DBScan算法的输入
    :param word_weight_lists:
    :return:
    """
    ind_ptr = [0]
    indices = []
    data = []
    vocabulary = {}
    for word_weight in word_weight_lists:
        for term_weight in word_weight:
            term = term_weight[0]
            weight = term_weight[1]
            index = vocabulary.setdefault(term, len(vocabulary))
            indices.append(index)
            data.append(weight)
        ind_ptr.append(len(indices))

    return csr_matrix((data, indices, ind_ptr), dtype=np.float64)