#!/usr/bin/env python
# -*- coding: utf-8 -*-

from job_cluster import *

# 创建job
cluster_job_01 = ChineseClusterJob01()
cluster_job_02 = EnglishClusterJob02()
cluster_job_03 = ChineseClusterJob03()
cluster_job_04 = EnglishClusterJob04()
cluster_job_05 = EnglishClusterJob05()

involved_china_job_02 = InvolvedChinaJob02()


# 调度job
def cluster_job():
    import datetime
    now = datetime.datetime.now()
    end_dt = datetime.datetime.combine(now.date(), datetime.time(now.time().hour, 00, 00))
    start_dt = end_dt - datetime.timedelta(days=1)
    end_time = end_dt.strftime('%Y-%m-%d %H:%M:%S')
    start_time = start_dt.strftime('%Y-%m-%d %H:%M:%S')

    # 调度
    # cluster_job_01.run(start_time, end_time)
    #cluster_job_02.run(start_time, end_time)
    #cluster_job_03.run(start_time,  end_time)
    # cluster_job_04.run(start_time, end_time)
    # cluster_job_05.run(start_time, end_time)
    involved_china_job_02.run(start_time, end_time)


if __name__ == '__main__':
    cluster_job()
