#!/usr/bin/env python
# -*- coding: utf-8 -*-

from cluster.hierarch import hierarchical_cluster
from dao.mysql.base_data_view import BaseDataView
from dao.mysql.cluster_job_log import ClusterJobLog
from dao.mysql.base_data_view import group_id_dict
from dao.mysql.mer_cluster_result import MergerClusterResult
from dao.mysql.subject_manual_info import SubjectManualInfo
from dao.solr import collection1
from utils.logger import logger
from datetime import datetime
from sklearn.externals import joblib
from cluster.dbscan import dbscan_twice_cluster
from dao.mysql.cluster_result import *


class ClusterMessageObj(object):
    """
    聚类实体类
    """

    def __init__(self, messageId=0, messageTitle='', messagePublishtime='', messageContent='', site_name=''):
        self.messageId = messageId
        self.messageTitle = messageTitle
        self.messagePublishtime = messagePublishtime
        self.messageContent = messageContent
        self.site_name = site_name

def parse_corpus_records(records, language_type=None):
    data = []
    for row in records:
        id = row['id']

        title = row['title']
        title = title.encode('utf-8')

        content = row['content']
        content = content.encode('utf-8')

        publish_time = row['publishtime'].encode('utf-8') # .strftime("%Y-%m-%d %H:%M:%S")
        site_name = row['site_name']
        site_name = site_name.encode('utf-8')

        cluster_obj = ClusterMessageObj(id, title, publish_time, content, site_name)

        # 进行语言过滤
        if language_type is not None:
            if BaseDataView.is_valid_language(language_type, content):
                data.append(cluster_obj)
        else:
            data.append(cluster_obj)
    return data

import pandas as pd
def save_zh_result(cluster_results, save_file_path):
    create_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    cluster_results = [(c.id, c.cluster_id, c.topic, c.publish_begin_time,
                        c.publish_end_time, c.group_id,
                        c.member, c.language_type, c.member_count,
                        c.site_count, c.is_manual, c.manual_id,
                        c.subtopic_id, create_time, c.cluster_type,
                        c.keyword_id, c.order_id) for c in cluster_results]

    attrs = ["id", "cluster_id", "cluster_topic", "cluster_begin", "cluster_end", "group_id",
             "cluster_member", "language_type", "cluster_member_count", "site_count",
             "is_manual", "manual_id", "subtopic_id", "create_time", "cluster_type",
             "keyword_id", "order_id"]
    data = pd.DataFrame(cluster_results, columns=attrs)
    data.to_excel(save_file_path, index=False)

def save_en_sub_result(sub_cluster_results, sub_save_file_path):
    create_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    cluster_results = [(c.cluster_id, c.topic, c.publish_begin_time,
                        c.publish_end_time, c.member,
                        c.member_count, c.site_count, c.cluster_result_id,
                        c.cluster_type, c.language_type, c.group_id,
                        c.is_manual, c.manual_id, c.subtopic_id, create_time) for c in sub_cluster_results]

    attrs = ["cluster_id", "cluster_topic", "cluster_begin",
             "cluster_end", "cluster_member", "cluster_member_count",
             "site_count", "cluster_result_id", "cluster_type",
             "language_type", "group_id", "is_manual",
             "manual_id", "subtopic_id", "create_time"]
    data = pd.DataFrame(cluster_results, columns=attrs)
    data.to_excel(sub_save_file_path, index=False)

def save_en_result(merger_cluster_results, save_file_path):
    create_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # 保存sub_cluster_result
    sub_cluster_results = [sub_cluster_result for merger_cluster_result in merger_cluster_results
                           for sub_cluster_result in merger_cluster_result.sub_cluster_results]

    sub_save_file_path = save_file_path.replace('.xlsx', '_sub.xlsx')
    save_en_sub_result(sub_cluster_results, sub_save_file_path)

    # 保存merger_cluster_result
    merger_cluster_results = [(c.id, c.cluster_id, c.topic, c.publish_begin_time,
                               c.publish_end_time, c.member_count, c.site_count,
                               c.cluster_type, c.language_type, c.group_id,
                               c.is_manual, c.manual_id, c.subtopic_id,
                               create_time, c.member, c.keyword_id, c.order_id) for c in merger_cluster_results]

    attrs = ["id", "cluster_id", "cluster_topic", "cluster_begin", "cluster_end",
             "cluster_member_count", "site_count",
             "cluster_type", "language_type", "group_id",
             "is_manual", "manual_id", "subtopic_id", "create_time",
             "cluster_member", "keyword_id", "order_id"]

    data = pd.DataFrame(merger_cluster_results, columns=attrs)
    data.to_excel(save_file_path, index=False)

# 调度job
def cluster_job(file_path, language_type):
    """
    只计算聚类
    """

    import json
    with open(file_path, 'r') as json_file: # , encoding='utf-8'
        data = json.load(json_file)
    corpus = parse_corpus_records(data, language_type=None)

    save_file_path = file_path.replace('corpus', 'result').replace('.json', '.xlsx')
    logger.info('file_path: %s; save_file_path: %s' % (file_path, save_file_path))

    is_manual, involved_china, subject_id, subtopic_id = range(4)
    cluster_type, manual_id, min_sample, save_group_id = range(4)
    if len(corpus) > 0:
        if language_type == 0: # 中
            cluster_results = dbscan_twice_cluster.perform_cluster(is_manual, cluster_type,
                                                                   manual_id, subtopic_id,
                                                                   language_type, corpus,
                                                                   save_group_id)
            save_zh_result(cluster_results, save_file_path)

        elif language_type == 1: # 英
            # 层次聚类
            # corpus = corpus[:500]
            cluster_results = hierarchical_cluster.perform_cluster(is_manual, involved_china, subject_id, subtopic_id,
                                                                   language_type, corpus, min_sample, save_group_id)
            save_en_result(cluster_results, save_file_path)


if __name__ == "__main__":
    cluster_job("corpus/corpus_en_7_20190508082141.json", 1) # 英
    # cluster_job("corpus/corpus_zh_7_20190508082141.json", 0) # 中
