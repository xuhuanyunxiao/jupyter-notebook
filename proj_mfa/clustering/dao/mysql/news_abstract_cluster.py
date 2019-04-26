#!/usr/bin/python
# -*- coding: utf-8 -*-

from datetime import datetime
from db_mysql import BaseMysql
from sub_cluster_result import SubClusterResult


class MergerClusterResult(BaseMysql):
    def __init__(self):
        super(MergerClusterResult, self).__init__()
        self.table_name = 'news_abstract_cluster'

    def save_abstract_clusters(self, cluster_results):
        """
        保存聚类结果
        :param cluster_results:  聚类结果
        (cluster_id, cluster_topic, cluster_begin, cluster_end, cluster_member,
        create_time, site_count, cluster_member_count, language_type, cluster_type,
        time_type)
        :return:
        """
        # cluster_results = [(c.id, c.cluster_id, c.topic, c.publish_begin_time,
        #                     c.publish_end_time, c.group_id,
        #                     c.member, c.language_type, c.member_count,
        #                     c.site_count, c.is_manual, c.manual_id,
        #                     c.subtopic_id, create_time, c.cluster_type,
        #                     c.keyword_id, c.order_id) for c in cluster_results]
        #
        # attrs = ["id", "cluster_id", "cluster_topic", "cluster_begin", "cluster_end", "group_id",
        #          "cluster_member", "language_type", "cluster_member_count", "site_count",
        #          "is_manual", "manual_id", "subtopic_id", "create_time", "cluster_type",
        #          "keyword_id", "order_id"]
        #
        # self.insert_many(self.table_name, attrs, cluster_results)

        pass


class AbstractCluster(object):
    def __init__(self, cluster_id, cluster_topic, cluster_begin_time, cluster_end_time, cluster_member,
                 create_time, site_count, cluster_member_count, language_type, cluster_type,
                 time_type):
        self.cluster_id = cluster_id
        self.cluster_topic = cluster_topic
        self.cluster_begin = cluster_begin_time
        self.cluster_end = cluster_end_time
