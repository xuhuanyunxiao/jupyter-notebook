#!/usr/bin/python
# -*- coding: utf-8 -*-

from datetime import datetime
import json
import socket
from db_mysql import BaseMysql


class SystemTimerLog(BaseMysql):
    # 定义静态job的名称, 以及编号
    timer_job_infos = {

        # 自动
        101: ('自动聚类 - 国内新闻', '整点开始,每隔1小时,执行一次', 100),
        102: ('自动聚类 - 境外媒体', '整点开始,每隔1小时,执行一次', 100),
        103: ('自动聚类 - 国内网民', '整点开始,每隔1小时,执行一次', 100),
        104: ('自动聚类 - 国外网民', '整点开始,每隔1小时,执行一次', 100),
        105: ('自动聚类 - 重点外媒', '整点开始,每隔1小时,执行一次', 100),

        # 自动 - 涉华聚类
        202: ('自动聚类 - 涉华', '整点开始,每隔1小时,执行一次', 202),

        # 自动 - 周聚类
        302: ('自动聚类 - 周', '每周四23:00:00, 执行一次', 302),

        # 人工聚类
        401: ('%s', '%s, 执行一次', 401),

        # 划线模型聚类
        402: ('自动聚类 - 划线模型', '[7:30am,5:30pm]执行一次', 402),
    }

    def __init__(self):
        super(SystemTimerLog, self).__init__()
        self.table_name = 'system_timer_log'

    def save_manual_cluster_log(self, manual_id, subject_name, involved_china, monitor_type, begin_time, end_time, exec_time):
        name_type = 401

        infos = SystemTimerLog.timer_job_infos[name_type]
        name = infos[0] % (subject_name, )
        rule = infos[1] % (exec_time, )
        parent_name_type = infos[2]  # 没有子任务

        begin_time = begin_time.strftime('%Y-%m-%d %H:%M:%S')
        end_time = end_time.strftime('%Y-%m-%d %H:%M:%S')

        detail_map = {'clusterType': involved_china,
                      'monitorType': monitor_type,
                      'dataBeginTime': begin_time,
                      'dataEndTime': end_time,
                      'schedulerTime': exec_time}
        detail = json.dumps(detail_map, ensure_ascii=False, sort_keys=True, indent=4)
        detail = '任务信息: \n' + detail

        return self._save_log(name, rule, name_type, parent_name_type, detail)

    def update_manual_cluster_log(self, id, involved_china, exec_begin_time=None, input_size=None, output_size=None, exception=None):
        exec_end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        detail_map = {}
        if exception is None:
            state = 0
            detail_map['execBeginTime'] = exec_begin_time
            detail_map['execEndTime'] = exec_end_time
            detail_map['inputSize'] = input_size
            detail_map['outputSize'] = output_size
        else:
            state = 1
            detail_map['exceptionInfo'] = repr(exception)

        detail = json.dumps(detail_map, ensure_ascii=False, sort_keys=True, indent=4)

        if involved_china == 1: # 涉华
            detail = '\n涉华任务信息: \n' + detail
        if involved_china == 2: # 自动
            detail = '\n自动任务信息: \n' + detail

        self.update_log(id, detail, state)

    def save_auto_cluster_log(self, save_group_id, week_fag, is_manual):
        if week_fag == 1:  # 周聚类
            name_type = 300 + save_group_id
        else:  # 小时聚类
            if is_manual == 2:  # 涉华
                name_type = 200 + save_group_id
            else:  # 自动
                name_type = 100 + save_group_id

        infos = SystemTimerLog.timer_job_infos[name_type]
        return self._save_log(infos[0], infos[1], name_type, infos[2])

    def save_summary_cluster_log(self):
        name_type = 402
        infos = SystemTimerLog.timer_job_infos[name_type]
        return self._save_log(infos[0], infos[1], name_type, infos[2])

    def update_auto_cluster_log(self, id, input_size=0, output_size=0, exception=None):
        detail_map = {}
        if exception is None:
            state = 0
            detail_map['inputSize'] = input_size
            detail_map['outputSize'] = output_size
        else:
            state = 1
            detail_map['exceptionInfo'] = repr(exception)

        detail_map['hostname'] = socket.gethostname()

        detail = json.dumps(detail_map, ensure_ascii=False, sort_keys=True, indent=4)
        self.update_log(id, detail, state)

    # 插入一条数据, 并且返回自动生成的id
    def _save_log(self, name, rule, name_type, parent_name_type, detail=None):
        # begin_time
        begin_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        if detail is None:
            sql = """
             INSERT INTO system_timer_log
            (name, rule, begin_time, name_type, parent_name_type) 
            VALUES (%s, %s, %s, %s, %s)
            """
            arg = (name, rule, begin_time, name_type, parent_name_type)
        else:
            sql = """
             INSERT INTO system_timer_log
            (name, rule, begin_time, name_type, detail, parent_name_type) 
            VALUES (%s, %s, %s, %s, %s, %s)
            """
            arg = (name, rule, begin_time, name_type, detail, parent_name_type)

        return self.insert_get_id(sql, arg=arg)

    def update_processing_log(self, id, desc):
        sql = """
            UPDATE system_timer_log 
            SET detail = CONCAT(detail, %s) 
            WHERE id = %s
            """

        self.execute_with_transaction(sql, arg=(desc, id))

    def update_log(self, id, detail, state):
        # end_time
        end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        sql = """
            UPDATE system_timer_log 
            SET detail = CONCAT(CASE WHEN detail IS NULL THEN '' ELSE detail END, %s), state = %s, end_time = %s 
            WHERE id = %s
            """

        self.execute_with_transaction(sql, arg=(detail, state, end_time, id))


if __name__ == '__main__':
    sys = SystemTimerLog()
    # print sys.save_auto_cluster_log(2, 0, 1)

    sys.update_auto_cluster_log(21, 10000, 100)

    # e = Exception('integer division or modulo by zero.')
    # sys.update_auto_cluster_log(21, exception=e)



