#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
import os
import sys

# 将父目录添加到环境变量
dir_path = os.path.dirname(os.path.abspath(__file__))
p_dir = os.path.dirname(dir_path)
sys.path.append(p_dir)

from apscheduler.executors.pool import ThreadPoolExecutor, ProcessPoolExecutor
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.schedulers.background import BlockingScheduler
from cluster_job import cluster_job
from dao.mysql.cluster_result import *
from dao.mysql.subject_manual_info import SubjectManualInfo
from utils.logger import logger

# 日志配置
logging.getLogger('apscheduler').setLevel(logging.DEBUG)

# scheduler 配置
mysql_url = 'mysql+mysqldb://' + BaseMysql.user + ':' + BaseMysql.passwd + '@' + BaseMysql.host + ':' + str(
    BaseMysql.port) + '/' + BaseMysql.db
jobstores = {
    'default': SQLAlchemyJobStore(url=mysql_url)
}

executors = {
    # 'default': ThreadPoolExecutor(5)
    'default': ProcessPoolExecutor(5)
}

job_defaults = {
    'coalesce': True,
    'max_instances': 5
}

# 创建调度器
scheduler = BlockingScheduler(jobstores=jobstores, executors=executors, job_defaults=job_defaults)


# 添加job
def manager_meta_job(group_id):
    """
    添加, 删除, 修改job
    该方法中使用了scheduler, 不能被序列化, 只能放到该类中
    """
    logger.debug("starting manager_meta_job...")
    subject_dao = SubjectManualInfo()
    jobs = subject_dao.read_jobs(group_id)

    # 遍历, 处理Job
    for job in jobs:
        process_status = job['process_status']
        group_id = job['group_id']
        subject_id = job['subject_id']
        monitor_type = job['monitor_type']
        begin_time = job['begin_time']
        end_time = job['end_time']
        exec_type = job['exec_type']
        exec_week = job['exec_week']
        exec_time = job['exec_time']
        cluster_type = job['cluster_type']
        logger.debug('{subject_id: %s, process_status: %s}.' % (subject_id, process_status))

        job_id = str(subject_id)
        if process_status == 3:  # delete job
            try:
                scheduler.remove_job(job_id)
            except Exception, e:
                logger.error('remove error, job not exists. {job_id: %s}' % (job_id,))

        if process_status == 1 or process_status == 2:  # add job
            logger.info('Add job. job_id: %s; process_status: %s; exec_time: %s; exec_type: %s; exec_week: %s; monitor_type: %s' % (
                                  job_id, process_status, exec_time, exec_type, exec_week, monitor_type))
            args = (group_id, subject_id, monitor_type, begin_time, end_time, cluster_type, exec_type)
            if exec_type == 0:  # 一次数
                args += ('cluster_result', )
                run_date = datetime.strptime(exec_time, '%Y-%m-%d %H:%M')
                scheduler.add_job(cluster_job, trigger='date', run_date=run_date,
                                  id=job_id, args=args, replace_existing=True)

            elif exec_type == 1:  # 天
                args += ('cluster_result', )
                dt = datetime.strptime(exec_time, '%H:%M')
                scheduler.add_job(cluster_job, trigger='cron', hour=dt.hour, minute=dt.minute,
                                  id=job_id, args=args, replace_existing=True)

            elif exec_type == 2:  # 周
                args += ('cluster_result_week', )
                dt = datetime.strptime(exec_time, '%H:%M')
                scheduler.add_job(cluster_job, trigger='cron', hour=dt.hour, minute=dt.minute,
                                  day_of_week=exec_week,
                                  id=job_id, args=args, replace_existing=True)

            elif exec_type == 3:  # 月
                args += 'cluster_result_month',
                dt = datetime.strptime(exec_time, '%d %H:%M')
                scheduler.add_job(cluster_job, trigger='cron', day=dt.day, hour=dt.hour, minute=dt.minute,
                                  id=job_id, args=args, replace_existing=True)

    # 更新状态
    subject_ids = [(job['subject_id'],) for job in jobs]
    subject_dao.update_process_status(subject_ids)
    logger.debug("end manager_meta_job...")


kwargs = {'group_id': 2}

scheduler.add_job(manager_meta_job, trigger='cron', minute='*/5',
                  id='meta_job', kwargs=kwargs, replace_existing=True)

# 启动调度器
scheduler.start()
