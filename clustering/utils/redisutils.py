#!/usr/bin/python
# -*- coding: UTF-8 -*-
import redis

# redis key
redis_str_runningAppNum = "mlutil_2.1_runningAppNum"


def incr():
    """
    原子性++, 指定的Key
    :return:
    """
    red = redis.Redis(host='10.24.193.40', password='wiseweb2017', port=6379, db=2)
    red.incr(redis_str_runningAppNum)


def decr():
    """
    原子性--, 指定的Key
    :return:
    """
    red = redis.Redis(host='10.24.193.40', password='wiseweb2017', port=6379, db=2)
    red.decr(redis_str_runningAppNum)


def get():
    """
    获得当前, 可运行应用程序的, 节点数
    """
    totalNodes = 3
    red = redis.Redis(host='10.24.193.40', password='wiseweb2017', port=6379, db=2)
    runingAppNum = red.get(redis_str_runningAppNum)
    return totalNodes - int(runingAppNum)
