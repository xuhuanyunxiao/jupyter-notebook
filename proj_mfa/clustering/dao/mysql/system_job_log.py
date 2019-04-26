#!/usr/bin/python
# -*- coding: utf-8 -*-

import socket
from datetime import datetime

import psutil

from db_mysql import BaseMysql


class SystemJobLog(BaseMysql):
    def __init__(self):
        super(SystemJobLog, self).__init__()
        self.table_name = 'system_job_log'

    def save_metrics(self, start_time, subject_id, save_table_name, data_total, end_time):
        """ 将cpu, memory, 数据大小保存到mysql中 """

        # memory
        vm = psutil.virtual_memory()
        vm_total = SystemJobLog.bytes_to_human(vm.total)
        vm_used = SystemJobLog.bytes_to_human(vm.used)
        vm_free = SystemJobLog.bytes_to_human(vm.free)

        # cpu
        ctp = psutil.cpu_times_percent(interval=1)
        cpu_count = psutil.cpu_count()
        cpu_user = ctp.user

        # job名
        job_name = '热点事件, {subject_id: %s, save_table_name: %s}' % (subject_id, save_table_name)

        # 主机名
        hostname = socket.gethostname()

        # zhushi
        annotate = '\t'.join([str(vm), str(ctp)])

        # create_time
        create_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        job_type = 3

        sql = """
        INSERT INTO system_job_log
        (job_name, start_time, end_time, data_total, ip, cpu_available, cpu_useage, 
        memory_total, memory_free, memory_useage, annotate, create_time, job_type) 
        VALUES ('%s', '%s', '%s', %s, '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', %s)
        """ % (job_name, start_time, end_time, data_total, hostname, cpu_count, cpu_user,
               vm_total, vm_free, vm_used, annotate, create_time, job_type)

        self.execute_with_transaction(sql)

    @staticmethod
    def bytes_to_human(n):
        symbols = ('K', 'M', 'G', 'T', 'P', 'E', 'Z', 'Y')
        prefix = {}
        for i, s in enumerate(symbols):
            prefix[s] = 1 << (i + 1) * 10
        for s in reversed(symbols):
            if n >= prefix[s]:
                value = float(n) / prefix[s]
                return '%.1f%s' % (value, s)
        return "%sB" % n
