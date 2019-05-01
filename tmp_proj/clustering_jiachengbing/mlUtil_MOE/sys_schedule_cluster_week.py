#!/usr/bin/env python
# -*- coding: utf-8 -*-

import datetime
from job_cluster import *

# 创建job
cluster_job_02 = EnglishClusterWeekJob02()


# 调度job
def cluster_job():
    now = datetime.datetime.now()
    end_dt = datetime.datetime.combine(now.date(), datetime.time(now.time().hour, 00, 00))
    start_dt = end_dt - datetime.timedelta(days=7)
    end_time = end_dt.strftime('%Y-%m-%d %H:%M:%S')
    start_time = start_dt.strftime('%Y-%m-%d %H:%M:%S')

    # 调度
    cluster_job_02.run(start_time, end_time)


if __name__ == '__main__':
    cluster_job()
