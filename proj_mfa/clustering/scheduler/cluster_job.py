#!/usr/bin/env python
# -*- coding: utf-8 -*-

from cluster.hierarch import hierarchical_cluster
from dao.mysql.base_data_view import BaseDataView
from dao.mysql.SystemTimerLog import SystemTimerLog
from dao.mysql.base_data_view import group_id_dict
from dao.mysql.mer_cluster_result import MergerClusterResult
from dao.mysql.subject_manual_info import SubjectManualInfo
from dao.solr import collection1
from utils.logger import logger
from datetime import datetime


# 调度job
def cluster_job(group_id, subject_id, subject_name, monitor_type, begin_time, end_time, schedule_time, involved_china, save_table_name, log_id=None):
    """
    只计算聚类
    """
    logger.info('starting cluster_job..., {subject_id: %s, save_table_name: %s}' % (subject_id, save_table_name))

    # 记录job开始日志
    sys_log = SystemTimerLog()
    if log_id is None:
        log_id = sys_log.save_manual_cluster_log(subject_id, subject_name, involved_china, monitor_type, begin_time, end_time, schedule_time)

    if involved_china == 0:  # 全部
        cluster_job(group_id, subject_id, subject_name, monitor_type, begin_time, end_time, schedule_time, 1, save_table_name, log_id)
        cluster_job(group_id, subject_id, subject_name, monitor_type, begin_time, end_time, schedule_time, 2, save_table_name, log_id)
        return

    try:
        corpus = []
        cluster_results = []
        exec_begin_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        if monitor_type == 0:  # 全监测
            # 获取语料
            is_manual = 1
            topic_id = 0
            save_group_id = group_id
            language_type = group_id_dict[save_group_id][1]
            group_ids = group_id_dict[save_group_id][0]
            group_ids = [str(id) for id in group_ids]
            get_group_id = '(' + ','.join(group_ids) + ')'
            min_sample = 2

            corpus = []
            base_data_dao = BaseDataView()
            if involved_china == 1:  # 涉华
                corpus = base_data_dao.get_involved_china_corpus(begin_time, end_time, language_type, get_group_id)
                min_sample = 1
            elif involved_china == 2:  # 自动
                corpus = base_data_dao.get_corpus(begin_time, end_time, language_type, get_group_id)

        if monitor_type == 1:  # 关键词监测
            is_manual = 1
            subject_dao = SubjectManualInfo()
            topic_list = subject_dao.get_subject_info_by_subject_id(subject_id)
            topic = topic_list[0]  # 只有一条数据
            topic_id = topic['topic_id']
            topic_words = topic['topic_words']
            save_group_id = topic['group_id']
            language_type = group_id_dict[save_group_id][1]
            min_sample = 2

            if involved_china == 1:  # 涉华
                ids = collection1.get_ids_from_solr_involved_china(save_group_id, topic_words, begin_time, end_time)
                min_sample = 1
            elif involved_china == 2:
                ids = collection1.get_ids_from_solr(save_group_id, topic_words, begin_time, end_time)
            ids = [id[0] for id in ids]

            base_data_dao = BaseDataView()
            corpus = base_data_dao.get_corpus_by_ids(ids, language_type=language_type)

        if len(corpus) > 0:
            # 层次聚类
            cluster_results = hierarchical_cluster.perform_cluster(is_manual, involved_china, subject_id, topic_id, language_type,
                                                                   corpus, min_sample, save_group_id)

            # 将结果保存到mysql中
            cluster_dao = MergerClusterResult()
            cluster_dao.save_cluster_results(cluster_results)

            # 清空上一批数据
            cluster_dao.delete_cluster_results(exec_begin_time, is_manual, involved_china, subject_id, topic_id, save_group_id)

        # job结束, 更新日志
        sys_log.update_manual_cluster_log(log_id, involved_china, exec_begin_time, len(corpus), len(cluster_results))
        logger.info('end run.')
    except Exception as e:
        sys_log.update_manual_cluster_log(log_id, involved_china, exception=e)
        raise e


if __name__ == "__main__":
    end_time = '2018-07-13 17:35:59'
    start_time = '2018-07-13 15:35:00'
    end_dt = datetime.strptime(end_time, '%Y-%m-%d %H:%M:%S')
    start_dt = datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S')

    cluster_job(2, 69, 0, start_dt, end_dt, 0, "cluster_result")
