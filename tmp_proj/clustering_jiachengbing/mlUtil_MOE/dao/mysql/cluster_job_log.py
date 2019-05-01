#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import socket
import threading
import uuid
from datetime import datetime
from db_mysql import BaseMysql


class ClusterJobLog(BaseMysql):
    def __init__(self):
        super(ClusterJobLog, self).__init__()
        self.table_name = 'cluster_job_log'

    def save_manual_job(self, save_group_id, subject_id, monitor_type, begin_time,
                        end_time, involved_china, save_table_name):
        is_manual = 1
        return self.save_job_log(is_manual, subject_id, monitor_type, begin_time,
                          end_time, involved_china, save_table_name, None,
                          None, save_group_id, None)

    def save_auto_job(self, is_manual, get_group_id,
                      language_type, save_group_id, week_fag):
        return self.save_job_log(is_manual, None, None, None,
                          None, None, None, get_group_id,
                          language_type, save_group_id, week_fag)

    def save_job_log(self, is_manual, subject_id, monitor_type, begin_time,
                     end_time, involved_china, save_table_name, get_group_id,
                     language_type, save_group_id, week_fag):
        """  job开始, 记录job """

        # job_id
        job_id = str(uuid.uuid1())

        # 主机名
        hostname = socket.gethostname()

        # 线程id
        t = threading.currentThread()
        thread_id = str(t.ident)

        # 进程id
        process_id = str(os.getpid())

        # create_time
        create_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        job_start_time = create_time

        if is_manual == 1:
            sql = """
            INSERT INTO cluster_job_log
            (job_id, hostname, process_id, thread_id, is_manual, subject_id, 
            monitor_type, begin_time, end_time, involved_china, save_table_name, job_start_time) 
            VALUES ('%s', '%s', '%s', '%s', %d, %d, 
            %d, '%s', '%s', %d, '%s', '%s')
            """ % (job_id, hostname, process_id, thread_id, is_manual, subject_id, monitor_type, begin_time,
                   end_time, involved_china, save_table_name, job_start_time)
        else:
            sql = """
            INSERT INTO cluster_job_log
            (job_id, hostname, process_id, thread_id, is_manual, get_group_id, 
            language_type, save_group_id, week_fag, job_start_time) 
            VALUES ('%s', '%s', '%s', '%s', %d, '%s',  
            %d, %d, %d, '%s')
            """ % (job_id, hostname, process_id, thread_id, is_manual, get_group_id, language_type, save_group_id,
                   week_fag, job_start_time)

        self.execute_with_transaction(sql)

        return job_id

    def update_job_log(self, job_id, cluster_member_count):
        """ job完成, 更新job """

        # create_time
        create_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        job_end_time = create_time

        sql = """
            UPDATE cluster_job_log
            SET cluster_member_count=%d, job_end_time='%s' 
            WHERE job_id = '%s'
            """ % (cluster_member_count, job_end_time, job_id)

        self.execute_with_transaction(sql)
