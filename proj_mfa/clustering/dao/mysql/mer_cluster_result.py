#!/usr/bin/python
# -*- coding: utf-8 -*-

from datetime import datetime
from db_mysql import BaseMysql
from sub_cluster_result import SubClusterResult


class MergerClusterResult(BaseMysql):
    def __init__(self):
        super(MergerClusterResult, self).__init__()
        self.table_name = 'cluster_result'

    def save_cluster_results(self, merger_cluster_results):
        """
        """
        # 由于mysql服务器, 同聚类服务器时间相差较大, 因此自定义插入时间字段
        create_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # 保存sub_cluster_result
        sub_cluster_results = [sub_cluster_result for merger_cluster_result in merger_cluster_results
                               for sub_cluster_result in merger_cluster_result.sub_cluster_results]
        sub_obj = SubClusterResult()
        sub_obj.save_sub_cluster_results(sub_cluster_results)

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

        self.insert_many(self.table_name, attrs, merger_cluster_results)

    def delete_cluster_results(self, end_time, is_manual, cluster_type, manual_id, subject_id, save_group_id):
        # merge_cluster_result
        sql = """
        DELETE FROM cluster_result 
        WHERE create_time < '%s' 
        AND group_id = '%s' 
        AND is_manual = %s 
        AND manual_id = %s 
        AND subtopic_id = %s 
        AND cluster_type = %s
        """ % (end_time, save_group_id, is_manual, manual_id, subject_id, cluster_type)

        self.delete(sql)

        # sub_cluster_result
        sub_obj = SubClusterResult()
        sub_obj.delete_sub_cluster_results(end_time, is_manual, cluster_type, manual_id, subject_id, save_group_id)


if __name__ == '__main__':
    now = datetime.datetime.now()
    end_dt = datetime.datetime.combine(now.date(), datetime.time(now.time().hour, 00, 00))
    start_dt = end_dt - datetime.timedelta(days=1)
    end_time = end_dt.strftime('%Y-%m-%d %H:%M:%S')
    start_time = start_dt.strftime('%Y-%m-%d %H:%M:%S')
