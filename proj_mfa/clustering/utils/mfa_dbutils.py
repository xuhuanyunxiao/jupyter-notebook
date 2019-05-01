#!/usr/bin/env python
# -*- coding: utf-8 -*-
import time
import MySQLdb
from entity import ClusterMessageObj
from utils.logger import logger


def save_cluster_results(cluster_results, group_id, language_type, save_table_name):
    """
    :param cluster_results:
    :param group_id:
    :param language_type: 0: 中文; 1: 英文
    :param save_table_name: 将结果保存到那个表中
    :return:
    """
    start_timestamp = time.time()

    # SQL 查询语句, 内容只取第一段内容
    sql = "insert into " + save_table_name \
          + " (cluster_id, cluster_topic, cluster_begin, cluster_end, group_id, cluster_member, " \
            "language_type, cluster_member_count, site_count, is_manual, manual_id, subtopic_id) " \
            "values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) "
    logger.debug("starting save_cluster_results, {sql: %s}." % sql)

    # 打开数据库连接  内网: 10.30.248.210    外网: 47.93.162.134
    db = MySQLdb.Connection(host='10.30.248.210', user='wisedb', passwd='Wi$eWeb123', db='wjbdb', charset='utf8',
                            port=5720)

    # 使用cursor()方法获取操作游标
    cursor = db.cursor()

    try:
        cluster_results = [(c.clusterId, c.clusterTopic, c.clusterPublishBeginTime,
                            c.clusterPublishEndTime, group_id,
                            c.clusterMember, language_type, c.cluserMemeberCount,
                            c.siteCount, c.is_manual, c.manual_id,
                            c.subtopic_id) for c in cluster_results]

        # 批量插入
        cursor.executemany(sql, cluster_results)
        db.commit()

        logger.debug(
            "ending save_cluster_results, {cost_tims: %ds}" % (time.time() - start_timestamp))
    except Exception as e:
        db.rollback()
        logger.error("Error: save_cluster_results, {Exception: %s}" % e)
    finally:
        # 关闭数据库连接
        cursor.close()
        db.close()


def get_involved_china_corpus(start_time, end_time, language_type, group_id):
    """
    获得聚类语料
    :param start_time:
    :param end_time:
    :param group_id:
    :return:
    """
    data = []
    start_timestamp = time.time()

    # SQL 查询语句, 内容只取第一段内容
    sql = """
    SELECT id, title, content, publishtime, site_name 
    FROM base_data_view 
    WHERE publishtime >= '%s' AND publishtime < '%s' 
    AND language_type = %s 
    AND group_id IN %s 
    AND involved_china = 1 
    group by titlehash """ % (start_time, end_time, language_type, group_id)

    logger.debug(
        "starting get_involved_china_corpus, {sql: %s}." % sql)

    # 打开数据库连接  内网: 10.30.248.210    外网: 47.93.162.134
    # 47.93.162.134
    db = MySQLdb.Connection(host='10.30.248.210', user='wisedb', passwd='Wi$eWeb123', db='wjbdb', charset='utf8',
                            port=5720)

    # 使用cursor()方法获取操作游标
    cursor = db.cursor()

    try:
        # 执行SQL语句
        cursor.execute(sql)

        # 获取所有记录列表
        for row in cursor:
            id = row[0]

            title = row[1]
            try:
                title = title.encode('utf-8')
            except Exception as e:
                logger.debug("Error: title.encode('utf-8'), {exception: %s}" % e)

            content = row[2]
            try:
                content = content.encode('utf-8')
            except Exception as e:
                logger.debug("Error: content.encode('utf-8'), {exception: %s}" % e)

            publish_time = row[3].strftime("%Y-%m-%d %H:%M:%S").decode('utf-8')

            site_name = row[4]
            try:
                site_name = site_name.encode('utf-8')
            except Exception as e:
                logger.debug("Error: site_name.encode('utf-8'), {exception: %s}" % e)

            cluster_obj = ClusterMessageObj(id, title, publish_time, content, site_name)

            # 加入结果
            data.append(cluster_obj)

        logger.debug(
            "ending get_involved_china_corpus, {data length: %s, cost_times: %ds}" % (len(data), time.time() - start_timestamp))
    except Exception as e:
        logger.error("Error: get_involved_china_corpus, {exception: %s}" % e)
    finally:
        # 关闭数据库连接
        cursor.close()
        db.close()
        return data


def get_corpus(start_time, end_time, language_type, group_id):
    """
    获得聚类语料
    :param start_time:
    :param end_time:
    :param group_id:
    :return:
    """
    data = []
    start_timestamp = time.time()

    # SQL 查询语句, 内容只取第一段内容
    sql = """
    SELECT id, title, content, publishtime, site_name 
    FROM base_data_view 
    WHERE publishtime >= '%s' AND publishtime < '%s' 
    AND language_type = %s 
    AND group_id IN %s 
    group by titlehash """ % (start_time, end_time, language_type, group_id)

    logger.debug(
        "starting get_corpus, {sql: %s}." % sql)

    # 打开数据库连接  内网: 10.30.248.210    外网: 47.93.162.134
    db = MySQLdb.Connection(host='10.30.248.210', user='wisedb', passwd='Wi$eWeb123', db='wjbdb', charset='utf8',
                            port=5720)

    # 使用cursor()方法获取操作游标
    cursor = db.cursor()

    try:
        # 执行SQL语句
        cursor.execute(sql)

        # 获取所有记录列表
        for row in cursor:
            id = row[0]

            title = row[1]
            try:
                title = title.decode('utf-8')
            except Exception as e:
                logger.debug("Error: title.decode('utf-8'), {exception: %s}" % e)

            content = row[2]
            try:
                content = content.decode('utf-8')
            except Exception as e:
                logger.debug("Error: content.decode('utf-8'), {exception: %s}" % e)

            publish_time = row[3].strftime("%Y-%m-%d %H:%M:%S").decode('utf-8')

            site_name = row[4]
            try:
                site_name = site_name.decode('utf-8')
            except Exception as e:
                logger.debug("Error: site_name.decode('utf-8'), {exception: %s}" % e)

            cluster_obj = ClusterMessageObj(id, title, publish_time, content, site_name)

            # 加入结果
            data.append(cluster_obj)

        logger.debug(
            "ending get_corpus, {data length: %s, cost_times: %ds}" % (len(data), time.time() - start_timestamp))
    except Exception as e:
        logger.error("Error: get_corpus, {exception: %s}" % e)
    finally:
        # 关闭数据库连接
        cursor.close()
        db.close()
        return data


def delete_cluster_results(end_time, save_group_id):
    """
    清空聚类结果表
    :param end_time:
    :param save_group_id
    :return:
    """
    start_timestamp = time.time()

    # SQL 语句
    sql = """
    DELETE FROM cluster_result 
    WHERE create_time < '%s' AND group_id = '%s'
    """ % (end_time, save_group_id)
    logger.debug("starting delete_cluster_results. {sql: %s}" % sql)

    # 打开数据库连接  内网: 10.30.248.210    外网: 47.93.162.134
    db = MySQLdb.Connection(host='10.30.248.210', user='wisedb', passwd='Wi$eWeb123', db='wjbdb', charset='utf8',
                            port=5720)

    # 使用cursor()方法获取操作游标
    cursor = db.cursor()

    try:

        # 批量插入
        cursor.execute(sql)
        db.commit()

        logger.debug(
            "ending truncate_cluster_results, {cost_times: %ds}" % (time.time() - start_timestamp))
    except Exception as e:
        db.rollback()
        logger.error("Error: delete_cluster_results, {Exception: %s}" % e)
    finally:
        # 关闭数据库连接
        cursor.close()
        db.close()


def get_subject_info(group_id):
    """ 获得subject_info列表信息 """
    topic_list = []
    start_timestamp = time.time()
    local_time = time.localtime(start_timestamp)
    now_time_str = time.strftime('%Y-%m-%d %H:%M:%S', local_time)

    # SQL 查询
    sql = """
    SELECT group_id, sms.id, subject_id, topic_name, topic_words 
    FROM subject_manual_info smf 
    JOIN subject_manual_subtopic sms 
    ON smf.id = sms.subject_id 
    WHERE status = 1 AND enabled = 1 
    AND end_time > '%s' 
    AND group_id = %s
    """ % (now_time_str, group_id)
    logger.debug("starting get_subject_info, {sql: %s}." % sql)

    # 打开数据库连接  内网: 10.30.248.210    外网: 47.93.162.134
    db = MySQLdb.Connection(host='10.30.248.210', user='wisedb', passwd='Wi$eWeb123', db='wjbdb', charset='utf8',
                            port=5720)

    # 使用cursor()方法获取操作游标
    cursor = db.cursor()

    try:
        # 执行SQL语句
        cursor.execute(sql)

        # 获取所有记录列表
        for row in cursor:
            group_id = row[0]
            topic_id = row[1]
            subject_id = row[2]

            topic_name = row[3]
            try:
                topic_name = topic_name.encode('utf-8')
            except Exception as e:
                logger.debug("Error: topic_name.encode('utf-8'), {exception: %s}" % e)

            topic_words = row[4]
            try:
                topic_words = topic_words.encode('utf-8')
            except Exception as e:
                logger.debug("Error: topic_words.encode('utf-8'), {exception: %s}" % e)

            data_tuple = (group_id, topic_id, subject_id, topic_name, topic_words)

            # 加入结果
            topic_list.append(data_tuple)

        logger.debug("ending get_subject_info, {cost_tims: %ds, data length: %s}" % (
        time.time() - start_timestamp, len(topic_list)))
    except Exception as e:
        logger.error("Error: get_subject_info, {exception: %s}" % e)
    finally:
        # 关闭数据库连接
        cursor.close()
        db.close()
        return topic_list


if __name__ == '__main__':
    print get_subject_info(5)
