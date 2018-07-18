#!/usr/bin/python
# -*- coding:utf-8 -*-
#%%
from predict import StatsFeatures
import pre
import predict
import sentiment_analyzer as sa

import logging.config
from datetime import datetime
from flask import Flask, request, jsonify

import jieba

from sklearn.base import BaseEstimator, TransformerMixin
#import joblib

from sklearn import feature_extraction
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_selection import SelectKBest, chi2,mutual_info_classif,f_classif 

from xgboost import XGBClassifier
from sklearn import metrics
from sklearn.pipeline import Pipeline,FeatureUnion

from collections import defaultdict

from sklearn.externals import joblib

#%% 基本设置
app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False

# 日志记录
logging.config.fileConfig("conf/logger.conf")
logger = logging.getLogger("rotating")

# 词典导入
# 自定义词典
jieba.load_userdict("corpus/user_dict.txt")

# 停止词
stopwords_path = "corpus/stopwordict.txt"
stopword_dict = open(stopwords_path, encoding="utf-8").readlines()
stopwordict = []
for word in stopword_dict:
    stopwordict.append(word.strip())

# org and business dict
org_dict_path = "corpus/org.txt"
orgdict = open(org_dict_path, encoding="utf-8").readlines()
org_dict = []
for word in orgdict:
    org_dict.append(word.strip())

# business dict
business_dict_path = "corpus/business.txt"
businessdict = open(business_dict_path, encoding="utf-8").readlines()
business_dict = []
for word in businessdict:
    business_dict.append(word.strip())

# 加入负面词库
negative_dict_path = "corpus/negative_words.txt"
negative_dict = open(negative_dict_path, encoding="utf-8").readlines()
negativedict = []  # 去掉空格的负面词库
for i in negative_dict:
    negativedict.append(i.strip())

# 公司主体词+保监会主体词
companies_path = "corpus/companies_name.txt"
companies_dict = open(companies_path, encoding="utf-8").readlines()
companiesdict = []  # 去掉空格后的公司词库
for i in companies_dict:
    companiesdict.append(i.strip())

# 歧义词词典
innegativedict = ['纯属', '系', '服务', '创新', '规范', '限制', 
                  '受限', '退出', '强制退出', '开启', '上新', 
                  '完成', '提速', '首例', '新产品', '创新产品']

#%% 篇章级正负面预测模型    
chapter_pipeline = joblib.load("model/NP_model_i_2.pkl.z")
#joblib.dump(chapter_pipeline, "model/NP_model_i_2.pkl.z")

#%%
@app.route('/correlation_negative', methods=['POST'])
def correlation_negative():
    """
    相关性, 篇章正负面, 机构标签 -> 正负面
    :return:
    """
    # get parameters
    start_time = datetime.now()
    records = request.json['record']
    logger.info('starting correlation_negative, {list_size: %d}' % (len(records)))

    # 相关性判断
    words_list = pre.handle_contents([record['content'] for record in records])
    result_list = predict.predict_corpus(words_list)
    record_result_list = zip(records, result_list)

    
    ret_list = []
    for record_result in record_result_list:
        id = int(record_result[0]['id'])
        title = record_result[0]['title']
        content = record_result[0]['content']
        content = title + '。' + content
        sec = int(record_result[1])
        tendency = 0
        org_list = []

        if sec == 1:
            # 句子正负面
            tendency, org_list = sa.evaluate_article(content)
            
            # 相关文章, 篇章级正负面
            # 早先设定-----tendency: 正负面字段,     -1: 负面; 0: 正面 (篇章正负面)
            # 模型返回-----positive  -> 1      negetive -> 0
            content = pre.handle_contents([content])
            tendency = chapter_pipeline.predict(content)
            tendency = int(tendency[0]) - 1  # 将模型返回值对应早先设定的值  

        ret_list.append({'id': id, 'sec': sec, 
                         'tendency': tendency, 
                         'org_list': org_list})

    # 返回结果
    logger.info('end correlation_negative: {ret_list: %d, lost_seconds: %ds}' % (
        len(ret_list), (datetime.now() - start_time).seconds))
    ret = {'docs': ret_list}
    return jsonify(ret)

#%%
if __name__ == '__main__':
    from werkzeug.contrib.fixers import ProxyFix
    
    app.wsgi_app = ProxyFix(app.wsgi_app)
    app.run(host='0.0.0.0', port=11000, threaded=True)
