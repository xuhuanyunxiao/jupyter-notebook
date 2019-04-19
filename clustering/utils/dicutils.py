#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import MySQLdb

reload(sys)
sys.setdefaultencoding("utf-8")


def getdics_mysql():
    dics = []

    # 打开数据库连接  内网: 10.30.248.210    外网: 47.93.162.134
    db = MySQLdb.Connection(host='10.30.248.210', user='wisedb', passwd='Wi$eWeb123', db='wjbdb', charset='utf8',
                            port=5720)

    # 使用cursor()方法获取操作游标
    cursor = db.cursor()

    # SQL 查询语句
    sql = "SELECT id, dic FROM custom_dic WHERE delete_flag = 0 AND language_flag = 0"
    try:
        # 执行SQL语句
        cursor.execute(sql)
        # 获取所有记录列表
        results = cursor.fetchall()
        for row in results:
            id = row[0]
            dic = row[1]

            # 加入结果
            dics.append((id, dic))
    except:
        print "Error: unable to fecth data"

    # 关闭数据库连接
    db.close()
    return dics


def getdics_eng():
    """
    从mysql中, 获取英文词典.
    :return:
    """
    dics = []

    # 打开数据库连接  内网: 10.30.248.210    外网: 47.93.162.134
    db = MySQLdb.Connection(host='10.30.248.210', user='wisedb', passwd='Wi$eWeb123', db='wjbdb', charset='utf8',
                            port=5720)

    # 使用cursor()方法获取操作游标
    cursor = db.cursor()

    # SQL 查询语句
    sql = "SELECT id, dic FROM custom_dic WHERE delete_flag = 0 AND language_flag = 1"
    try:
        # 执行SQL语句
        cursor.execute(sql)
        # 获取所有记录列表
        results = cursor.fetchall()
        for row in results:
            id = row[0]
            dic = row[1]

            # 加入结果
            dics.append((id, dic))
    except:
        print "Error: unable to fecth data"

    # 关闭数据库连接
    db.close()
    return dics


if __name__ == '__main__':
    dics = getdics_eng()
    for dic in dics:
        print dic[1]



    for dic in dics:
        print dic
        print '@'.join(dic[1].split(" "))
        print 'foreign leaders'.replace(dic, '@'.join(dic[1].split(" ")))
