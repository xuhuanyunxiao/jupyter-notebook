#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pymysql
import logging.config
import time

# 日志记录
logging.config.fileConfig("conf/logger.conf")
logger = logging.getLogger("rotating")


def get_dicts():
    """
    获得自定义词典
    :return:
    """
    data = {}
    start_timestamp = time.time()
    logger.debug("starting get_dicts, {start_time: %s}." % start_timestamp)

    # 打开数据库连接  内网: 10.80.88.73   外网: 47.95.148.133
    try :
        db = pymysql.connect(host='10.80.88.73', user='wisedb', passwd='Wi$eWeb123', 
                             db='pom', charset='utf8', port=5718)
    except :
        db = pymysql.connect(host='47.95.148.133', user='wisedb', passwd='Wi$eWeb123', 
                             db='pom', charset='utf8', port=5718)        

    # 使用cursor()方法获取操作游标
    cursor = db.cursor()

    # SQL 查询语句, 内容只取第一段内容
    sql = """
    select id, name, query_or, classify_id, node_id 
    from wise_class_tree_node_keyword 
    where flag = 0 and classify_id in (9, 7, 13)
    """

    try:
        # 执行SQL语句
        cursor.execute(sql)

        # 获取所有记录列表
        for row in cursor:
            id = row[0]
            name = row[1].strip()
            query_or = row[2].strip()
            classify_id = row[3]
            node_id = row[4]

            org_names = []
            if name != '':
                org_names.append(name)  # 全名
            if query_or != '' and classify_id == 9:
                org_names.extend(query_or.split(' '))  # 简称

            # 加入结果
            for org_name in org_names:
                org_name = org_name.strip()
                if org_name != '':
                    data[org_name] = (id, classify_id, node_id, org_name)

        logger.debug("ending get_dicts, {cost_times: %ds}" % (time.time() - start_timestamp))
    except Exception as e:
        logger.error("Error: get_dicts, {exception: %s}" % e)
    finally:
        # 关闭数据库连接
        cursor.close()
        db.close()
        return data


if __name__ == '__main__':
    print(get_dicts())

    dictionarys = get_dicts()
    for dictionary in dictionarys:
        print(dictionary)

    print(dictionarys['北京保监局'])