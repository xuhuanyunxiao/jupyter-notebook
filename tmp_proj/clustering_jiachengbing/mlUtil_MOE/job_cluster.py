#!/usr/bin/env python
# -*- coding: utf-8 -*-

from cluster.dbscan import dbscan_twice_cluster
from cluster.hierarch import hierarchical_cluster
from dao.mysql.base_data_view import BaseDataView
from dao.mysql.cluster_job_log import ClusterJobLog
from dao.mysql.cluster_result import *
from dao.mysql.mer_cluster_result import MergerClusterResult
from utils.logger import logger


class BaseClusterJob:
    def __init__(self, is_manual, get_group_id, language_type, week_fag, save_group_id):
        self.is_manual = is_manual
        self.get_group_id = get_group_id
        self.language_type = language_type
        self.week_fag = week_fag
        self.save_group_id = save_group_id

        self.cluster_type = 2
        self.manual_id = 0
        self.subtopic_id = 0

    def run(self, _start_time, _end_time):
        """
         只计算聚类
         """
        # 记录job开始日志
        cluster_job_log = ClusterJobLog()
        job_id = cluster_job_log.save_auto_job(self.is_manual, self.get_group_id, self.language_type, self.save_group_id, self.week_fag)

        # 开始执行
        # exe_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # 从mysql中读取数据
        corpus = []
        base_data_view = BaseDataView()
        if self.is_manual == 2:  # 涉华
            corpus = base_data_view.get_involved_china_corpus(_start_time, _end_time, self.language_type,
                                                              self.get_group_id)
        if self.is_manual == 0:
            corpus = base_data_view.get_corpus(_start_time, _end_time, self.language_type, self.get_group_id)

        corpus_length = len(corpus)

        if corpus_length == 0:
            logger.info('returning run, because len(lise_size) == 0, {start_time: %s, end_time: %s}.' % (
                _start_time, _end_time))

            #  更新job日志
            cluster_job_log.update_job_log(job_id, 0)
            return

        # 聚类
        if self.week_fag == 1:  # 周数据太多, 层次聚类 O(n^3), 太慢; 更换为 dbscan聚类
            cluster_results = dbscan_twice_cluster.perform_cluster(self.is_manual, self.cluster_type,
                                                                   self.manual_id, self.subtopic_id,
                                                                   self.language_type, corpus,
                                                                   self.save_group_id)
            cluster_dao = ClusterResultWeek()
        else:
            if self.language_type == 1:  # 英文聚类
                if self.is_manual == 2:  # 涉华
                    min_sample = 1
                else:
                    min_sample = 2
                cluster_results = hierarchical_cluster.perform_cluster(self.is_manual, self.cluster_type,
                                                                       self.manual_id, self.subtopic_id,
                                                                       self.language_type, corpus,
                                                                       min_sample, self.save_group_id)
                cluster_dao = MergerClusterResult()

            else:  # 中文采用DBScan聚类算法
                cluster_results = dbscan_twice_cluster.perform_cluster(self.is_manual, self.cluster_type,
                                                                       self.manual_id, self.subtopic_id,
                                                                       self.language_type, corpus,
                                                                       self.save_group_id)
                cluster_dao = ClusterResult()

        # 将结果保存到mysql中
        exe_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        logger.info('time to mysql: %s; cluster_results. cluster num: %s' % (exe_time,
                                                                             len(cluster_results)))
        cluster_dao.save_cluster_results(cluster_results)

        # 清空上一批数据
        cluster_dao.delete_cluster_results(exe_time, self.is_manual, self.cluster_type,
                                           self.manual_id, self.subtopic_id,
                                           self.save_group_id)

        # 更新job日志
        cluster_job_log.update_job_log(job_id, len(cluster_results))

        logger.info('end run.')


class ChineseClusterJob01(BaseClusterJob):
    def __init__(self):
        BaseClusterJob.__init__(self, 0, '(1, 5, 13)', 0, 0, 1)


class EnglishClusterJob02(BaseClusterJob):
    def __init__(self):
        BaseClusterJob.__init__(self, 0, '(7, 16)', 1, 0, 2)


class ChineseClusterJob03(BaseClusterJob):
    def __init__(self):
        BaseClusterJob.__init__(self, 0, '(2, 3, 4, 11)', 0, 0, 3)


class EnglishClusterJob04(BaseClusterJob):
    def __init__(self):
        BaseClusterJob.__init__(self, 0, '(15)', 1, 0, 4)


class EnglishClusterJob05(BaseClusterJob):
    def __init__(self):
        BaseClusterJob.__init__(self, 0, '(16)', 1, 0, 5)


class EnglishClusterWeekJob02(BaseClusterJob):
    def __init__(self):
        BaseClusterJob.__init__(self, 0, '(16)', 1, 1, 2)


class InvolvedChinaJob02(BaseClusterJob):
    def __init__(self):
        BaseClusterJob.__init__(self, 2, '(7, 16)', 1, 0, 2)
