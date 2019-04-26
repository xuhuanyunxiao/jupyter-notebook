#!/usr/bin/python
# -*- coding: utf-8 -*-

from datetime import datetime
from db_mysql import BaseMysql


class SubClusterResult(BaseMysql):
    def __init__(self):
        super(SubClusterResult, self).__init__()
        self.table_name = 'sub_cluster_result'

    def save_sub_cluster_results(self, sub_cluster_results):
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

        self.insert_many(self.table_name, attrs, cluster_results)

    def delete_sub_cluster_results(self, end_time, is_manual, cluster_type, manual_id, subject_id, save_group_id):
        sql = """
        DELETE FROM sub_cluster_result 
        WHERE create_time < '%s' 
        AND group_id = '%s' 
        AND is_manual = %s 
        AND manual_id = %s 
        AND subtopic_id = %s 
        AND cluster_type = %s
        """ % (end_time, save_group_id, is_manual, manual_id, subject_id, cluster_type)

        self.delete(sql)

    def delete_sub_cluster_results_slor(self, end_time, is_manual, cluster_type, manual_id, save_group_id):
        sql = """
        DELETE FROM sub_cluster_result 
        WHERE create_time < '%s' 
        AND group_id = '%s' 
        AND is_manual = %s 
        AND manual_id = %s 
        AND cluster_type = %s
        """ % (end_time, save_group_id, is_manual, manual_id, cluster_type)

        self.delete(sql)


if __name__ == '__main__':
    now = datetime.datetime.now()
    end_dt = datetime.datetime.combine(now.date(), datetime.time(now.time().hour, 00, 00))
    start_dt = end_dt - datetime.timedelta(days=1)
    end_time = end_dt.strftime('%Y-%m-%d %H:%M:%S')
    start_time = start_dt.strftime('%Y-%m-%d %H:%M:%S')