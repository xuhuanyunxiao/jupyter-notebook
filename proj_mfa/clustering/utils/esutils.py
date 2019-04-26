#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json

import requests

from entity import ClusterMessageObj, ClusterObj
from utils import jiebaCutWords
from utils import tfidfWeight
from logger import logger
from datetime import datetime


def ids(cObjArray):
    # 根据id获取数据
    retList = []
    start_time = datetime.now()
    logger.info('starting ids, {start_time: %s}' % (start_time.strftime('%Y-%m-%d %H:%M:%S')))
    for cObj in cObjArray:
        uri = "http://saas1:5000/enterprise_saas_platform/saas_platform/id=" + cObj[
            "clusterMessageId"] + "/display=id&summary&tendency"
        totalResp = requests.get(uri)
        jsonObj = json.loads(totalResp.text)
        summary = jsonObj["doc"][0]["summary"]
        tendency = jsonObj["doc"][0]["tendency"]
        retList.append(ClusterObj(int(cObj["clusterId"]), cObj["clusterTopic"], summary, tendency,
                                     cObj["clusterPublishtimeRange"], cObj["clusterMember"]))
    # 返回数据
    logger.info('end ids: {cObjArray_length: %d, lost_seconds: %ds}'
                % (len(cObjArray), (datetime.now()-start_time).seconds))
    return retList


def query_string(querystring):
    # 请求uri前缀
    cMList = []
    prefix_req_uri = "http://saas1:5000/enterprise_saas_platform/saas_platform/" + querystring + "/"
    suffix_uri_total = "display=id/1/1"
    start_time = datetime.now()
    logger.info('starting query_string, {prefix_req_uri: %s}'
                % (prefix_req_uri, start_time.strftime('%Y-%m-%d %H:%M:%S')))

    # 获得总数
    totalUri = prefix_req_uri + suffix_uri_total
    totalResp = requests.get(totalUri)
    total = json.loads(totalResp.text)["total"]

    # 每次请求条数
    pageNum = 100

    # 遍历, 获得数据
    display_uri_data = "display=id&title&pubtime/"
    for idx in range(0, total, pageNum):
        page_uri_data = str(idx) + "/" + str(pageNum)
        dataUri = prefix_req_uri + display_uri_data + page_uri_data
        dataResp = requests.get(dataUri)

        # 遍历数据, 保存到list列表中
        for mObj in json.loads(dataResp.text)["doc"]:
            id = mObj["id"]
            title = mObj["title"]
            publishtime = mObj["pubtime"]
            cMList.append(ClusterMessageObj(messageId=id, messageTitle=title, messagePublishtime=publishtime))
    # 返回数据
    logger.info('end query_string: {prefix_req_uri: %s, total: %d, lost_seconds: %ds}'
                % (prefix_req_uri, total, (datetime.now()-start_time).seconds))
    return cMList


def perform_cluster_id(cMList):
    """
    聚类, 并返回topic所属文章的id
    """
    start_time = datetime.now()
    logger.info('starting perform_cluster_id, {start_time: %s}' % (start_time.strftime('%Y-%m-%d %H:%M:%S')))
    titleList = jiebaCutWords.onlyTitle(cMList)
    cutResult = jiebaCutWords.cut_words_for_cluster(titleList)
    tfidfMatrix = tfidfWeight.getTfidf(cutResult, True)

    # DBScan聚类算法
    from utils import dbscanCluster
    cObjArray = dbscanCluster.runAlgAndGetReturnWithId(cMList, tfidfMatrix)

    # 返回数据
    logger.info('end perform_cluster_id: {cMList_length: %d, lost_seconds: %ds}'
                % (len(cMList), (datetime.now()-start_time).seconds))
    return cObjArray


def perform_cluster_es(querystring):
    cMList = query_string(querystring)

    # 调用方法, 进行聚类
    cObjArray = perform_cluster_id(cMList)

    # 构造返回对象
    retList = ids(cObjArray)
    return retList
