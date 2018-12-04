#!/usr/bin/env python
# -*- coding: utf-8 -*-

import myclass_circ
import pre_cor_circ

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

#%% 行业分类预测模型
#industry_pipeline = joblib.load("model/cac_industy_1026.pkl.z")
#joblib.dump(industry_pipeline, "model/cac_industy_1026_2.pkl.z")
industry_pipeline = joblib.load("model/moe_cor_1120.pkl.z")

@app.route('/judge_correlation', methods=['POST'])
def judge_correlation():
    """
    判断相关性：二分类模型，判断某条数据（新闻）是否是行业、机构相关
    相关性模型替换成八分类模型
    """
    start_time = datetime.now()
    records = request.json['record']
    logger.info('starting judge_correlation, {list_size: %d}' % (len(records)))

    # 预处理
    words_list = pre_cor_circ.handle_contents([record['title'] + '. ' + record['content'] \
                                          for record in records])

    cor_res = industry_pipeline.predict(words_list)

    ret_list = []
    for index, record_result in enumerate(records):
        id = int(record_result['id'])
        industry = int(cor_res[index])

        ret_list.append({'id': id, 'cor': industry})

    # 返回结果
    logger.info('end judge_correlation: {ret_list: %d, lost_seconds: %ds}' % (
        len(ret_list), (datetime.now() - start_time).seconds))
    ret = {'docs': ret_list, 
           'elapsed_time': '%0.2f'%((datetime.now() - start_time).seconds)}

    return jsonify(ret)

#%%
if __name__ == '__main__':
    from werkzeug.contrib.fixers import ProxyFix
    
    app.wsgi_app = ProxyFix(app.wsgi_app)

    app.run(host='0.0.0.0', port=9001, threaded=True) 







