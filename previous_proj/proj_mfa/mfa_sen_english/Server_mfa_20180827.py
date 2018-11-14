#!/usr/bin/env python
# -*- coding: utf-8 -*-

from predict import StatsFeatures
import pre
import predict
#import sentiment_analyzer as sa

from sklearn.externals import joblib
import warnings
warnings.filterwarnings('ignore')

import logging.config
from datetime import datetime
from flask import Flask, request, jsonify

#%% 基本设置
app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False

# 日志记录
logging.config.fileConfig("conf/logger.conf")
logger = logging.getLogger("rotating")

#%% 相关性预测模型
#correlation_pipeline = joblib.load("model/mfa_cor_0809.pkl.z")
#joblib.dump(correlation_pipeline, "model/mfa_cor_0809_2.pkl.z")
correlation_pipeline = joblib.load("model/mfa_cor_0809_2.pkl.z")

@app.route('/judge_correlation_i', methods=['POST'])
def judge_correlation_i():
    """
    判断相关性：二分类模型，判断某条数据（新闻）是否是行业、机构相关
    """
    start_time = datetime.now()
    records = request.json['record']
    logger.info('starting judge_correlation_i, {list_size: %d}' % (len(records)))

    # 预处理
    words_list = pre.handle_contents([record['title'] + '。' + record['content'] \
                                          for record in records])

    # 相关性判断
    # 1是相关，0是不相关
    correlation_res = correlation_pipeline.predict(words_list)

    ret_list = []
    for index, record_result in enumerate(records):
        id = int(record_result['id'])
        cor = int(correlation_res[index])

        ret_list.append({'id': id, 'cor': cor})

    # 返回结果
    logger.info('end judge_correlation_i: {ret_list: %d, lost_seconds: %ds}' % (
        len(ret_list), (datetime.now() - start_time).seconds))
    ret = {'docs': ret_list, 
           'elapsed_time': '%0.2f'%((datetime.now() - start_time).seconds)}

    return jsonify(ret)

#%% 相关性预测模型
#sensitivity_pipeline = joblib.load("model/mfa_sen_0830.pkl.z")
#joblib.dump(sensitivity_pipeline, "model/mfa_sen_0830_2.pkl.z")
sensitivity_pipeline = joblib.load("model/mfa_sen_0830_2.pkl.z")

@app.route('/judge_sensitivity', methods=['POST'])
def judge_sensitivity():
    """
    判断敏感性
    """
    start_time = datetime.now()
    records = request.json['record']
    logger.info('starting judge_sensitivity, {list_size: %d}' % (len(records)))

    # 预处理
    words_list = pre.handle_contents([record['title'] + '。' + record['content'] \
                                          for record in records])

    # 敏感判断
    # 1是敏感，0是不敏感
    sensitivity_res = sensitivity_pipeline.predict(words_list)

    ret_list = []
    for index, record_result in enumerate(records):
        id = int(record_result['id'])
        cor = int(sensitivity_res[index])

        ret_list.append({'id': id, 'cor': cor})

    # 返回结果
    logger.info('end judge_sensitivity: {ret_list: %d, lost_seconds: %ds}' % (
        len(ret_list), (datetime.now() - start_time).seconds))
    ret = {'docs': ret_list, 
           'elapsed_time': '%0.2f'%((datetime.now() - start_time).seconds)}

    return jsonify(ret)


#%%
if __name__ == '__main__':
    from werkzeug.contrib.fixers import ProxyFix
    
    app.wsgi_app = ProxyFix(app.wsgi_app)

    app.run(host='0.0.0.0', port=11000, threaded=True) 







