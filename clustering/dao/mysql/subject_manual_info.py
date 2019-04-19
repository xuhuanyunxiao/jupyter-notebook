#!/usr/bin/python
# -*- coding: utf-8 -*-

from db_mysql import BaseMysql


class SubjectManualInfo(BaseMysql):
    def __init__(self):
        super(SubjectManualInfo, self).__init__()
        self.table_name = 'subject_manual_info'

    @staticmethod
    def parse_subject_info_records(records):
        topic_list = []
        for row in records:
            group_id = row['group_id']
            topic_id = row['topic_id']
            subject_id = row['subject_id']

            topic_name = row['topic_name']

            topic_words = row['topic_words']

            data_tuple = (group_id, topic_id, subject_id, topic_name, topic_words)

            # 加入结果
            topic_list.append(data_tuple)

        return topic_list

    def get_subject_info_by_group_id(self, group_id):
        """ 获得subject_info列表信息 """
        sql = """
        SELECT group_id, sms.id AS topic_id, subject_id, topic_name, topic_words 
        FROM subject_manual_info smf 
        JOIN subject_manual_subtopic sms 
        ON smf.id = sms.subject_id 
        WHERE status = 1 AND enabled = 1 
        AND group_id = %s
        """ % group_id

        records = self.fetch_all(sql)

        return SubjectManualInfo.parse_subject_info_records(records)

    def get_subject_info_by_subject_id(self, subject_id):
        """ 获得subject_info列表信息 """
        sql = """
        SELECT group_id, sms.id AS topic_id, subject_id, topic_name, topic_words 
        FROM subject_manual_info smf 
        JOIN subject_manual_subtopic sms 
        ON smf.id = sms.subject_id 
        AND subject_id = %s
        """ % subject_id

        records = self.fetch_all(sql)
        return records
        # return SubjectManualInfo.parse_subject_info_records(records)

    def read_jobs(self, group_id):
        """
        Read jobs
        用于调度器获取job
        """
        sql = """
        SELECT group_id, id AS subject_id, subject_name, 
        monitor_type, begin_time, end_time, 
        exec_type, exec_week, exec_time, 
        process_status, cluster_type 
        FROM subject_manual_info  
        WHERE group_id = %s 
        AND process_status != 0 
        AND enabled = 1 
        AND status = 1
        """ % group_id

        records = self.fetch_all(sql)

        return records

        # # 获取数据
        # data = []
        # for row in records:
        #     group_id = row['group_id']
        #     subject_id = row['subject_id']
        #     monitor_type = row['monitor_type']
        #     begin_time = row['begin_time']
        #     end_time = row['end_time']
        #     exec_type = row['exec_type']
        #     exec_week = row['exec_week']
        #     exec_time = row['exec_time']
        #     process_status = row['process_status']
        #
        #     data_tuple = (group_id, subject_id, monitor_type, begin_time, end_time,
        #                   exec_type, exec_week, exec_time, process_status)
        #
        #     # 加入结果
        #     data.append(data_tuple)
        #
        # return data

    def update_process_status(self, subject_ids):
        """ 更新job状态 """

        sql = """
        UPDATE subject_manual_info 
        SET process_status = 0 
        WHERE id = %s
        """

        self.execute_many_with_transaction(sql, subject_ids)


if __name__ == '__main__':
    a = SubjectManualInfo()
    print a.read_jobs(2)
