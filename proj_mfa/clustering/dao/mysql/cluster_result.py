#!/usr/bin/python
# -*- coding: utf-8 -*-

from datetime import datetime
from db_mysql import BaseMysql


class ClusterResult(BaseMysql):
    def __init__(self):
        super(ClusterResult, self).__init__()
        self.table_name = 'cluster_result'

    def save_cluster_results(self, cluster_results):
        """
        :param cluster_results:
        :param group_id:
        :param language_type: 0: 中文; 1: 英文
        :param save_table_name: 将结果保存到那个表中
        :return:
        """
        # 由于mysql服务器, 同聚类服务器时间相差较大, 因此自定义插入时间字段
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

        self.insert_many(self.table_name, attrs, cluster_results)

    def delete_cluster_results(self, end_time, is_manual, cluster_type, manual_id, subject_id, save_group_id):
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

    def get_cluster_results(self):
        dicts = []

        sql = """ SELECT id, group_id, language_type 
        FROM  cluster_result 
        WHERE group_id = 2 
        AND is_manual = 2 
        AND manual_id = 0 
        AND subtopic_id = 0 
        AND cluster_type = 2 """

        records = self.fetch_all(sql)

        for row in records:
            id = row['id']
            dic = row['group_id']

            # 加入结果
            dicts.append((id, dic))
        return dicts


class ClusterResultWeek(ClusterResult):
    def __init__(self):
        super(ClusterResultWeek, self).__init__()
        self.table_name = 'cluster_result_week'


if __name__ == '__main__':
    import datetime
    now = datetime.datetime.now()
    end_dt = datetime.datetime.combine(now.date(), datetime.time(now.time().hour, 00, 00))
    start_dt = end_dt - datetime.timedelta(days=1)
    end_time = end_dt.strftime('%Y-%m-%d %H:%M:%S')
    start_time = start_dt.strftime('%Y-%m-%d %H:%M:%S')

    a = ClusterResult()
    print a.get_cluster_results()
