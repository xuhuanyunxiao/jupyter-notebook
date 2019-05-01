#!/usr/bin/env python
# -*- coding: utf-8 -*-

from cluster.feature import jieba_multipro
from cluster.feature import tfidfWeight
from utils.logger import logger
import uuid


# dbscanlabel
def dbscanCluster(tfidfMatrix, size):
    from sklearn.cluster import DBSCAN

    # 根据数据大小, 选择不同的参数
    # if size > 20000:
    #     _eps = 0.4
    #     _min_samples = 3
    # elif size > 15000:
    #     _eps = 0.45
    #     _min_samples = 3
    # elif size > 10000:
    #     _eps = 0.5
    #     _min_samples = 3
    # elif size > 5000:
    #     _eps = 0.55
    #     _min_samples = 3
    # elif size > 2000:
    #     _eps = 0.6
    #     _min_samples = 3
    # elif size > 200:
    #     _eps = 0.65
    #     _min_samples = 2
    # elif size > 150:
    #     _eps = 0.9
    #     _min_samples = 2
    # elif size > 100:
    #     _eps = 0.95
    #     _min_samples = 2
    # elif size > 50:
    #     _eps = 1.0
    #     _min_samples = 2
    # else:
    #     _eps = 1.05
    #     _min_samples = 2

    _eps = 0.5
    _min_samples = 2

    dbscan = DBSCAN(eps=_eps, min_samples=_min_samples, metric='cosine')
    dbscan.fit_predict(tfidfMatrix)
    return dbscan.labels_


def getReturnData(label, messageObjList):
    # title和MessageObj 拉链操作
    labelZipMessageObjList = zip(label, messageObjList)
    # 去除-1标签
    noImpurity = filter(lambda (x, y): x != -1, labelZipMessageObjList)

    # 按label分组,统计每个组出现次数最多的title,统计每个组的时间范围
    noImpurityGroup = {}
    for line in noImpurity:
        label = line[0]
        id = line[1].messageId
        title = line[1].messageTitle
        content = line[1].messageContent
        content_length = len(content)
        publish_time = line[1].messagePublishtime
        site_name = line[1].site_name

        # 如果不存在, 初始化
        if label not in noImpurityGroup.keys():
            noImpurityGroup[label] = {}
            noImpurityGroup[label]["id"] = []
            # 关注title  出现次数
            noImpurityGroup[label]["title"] = {}
            # 关注publishtime  最大最小
            noImpurityGroup[label]["publishtime"] = []
            # 关注site_name
            noImpurityGroup[label]["sitename"] = set()
            # 获得不同站点中, length最长的文章
            noImpurityGroup[label]["mlcpersite"] = {}

            noImpurityGroup[label]["id"].append(id)
            noImpurityGroup[label]["title"][title] = 1
            noImpurityGroup[label]["publishtime"].append(publish_time)
            noImpurityGroup[label]["sitename"].add(site_name)
            noImpurityGroup[label]["mlcpersite"][site_name] = {'content': content, 'maxlength': content_length,
                                                               'id': id}
        else:
            noImpurityGroup[label]["id"].append(id)
            if title not in noImpurityGroup[label]["title"].keys():
                noImpurityGroup[label]["title"][title] = 1
            else:
                noImpurityGroup[label]["title"][title] += 1
            noImpurityGroup[label]["publishtime"].append(publish_time)
            noImpurityGroup[label]["sitename"].add(site_name)
            if site_name not in noImpurityGroup[label]["mlcpersite"].keys():
                noImpurityGroup[label]["mlcpersite"][site_name] = {'content': content, 'maxlength': content_length,
                                                                   'id': id}
            else:
                old_mlc = noImpurityGroup[label]["mlcpersite"][site_name]
                if old_mlc['maxlength'] < content_length:
                    noImpurityGroup[label]["mlcpersite"][site_name] = {'content': content, 'maxlength': content_length,
                                                                       'id': id}

    # 分组内部 title降序排序 publisttime比较大小 构造ClusterObj
    import operator
    from entity.ClusterObj import ClusterObj
    cObjArray = []
    for (label, value) in noImpurityGroup.items():
        # clusterId
        clusterId = label

        # clusterTopic  对每一title降序排序
        titleGroup = noImpurityGroup[label]["title"]
        sortedTitleGroup = sorted(titleGroup.iteritems(), key=operator.itemgetter(1), reverse=True)
        clusterTopic = sortedTitleGroup[0][0]

        # clusterPublishtimeRange 对时间排序
        clusterPublishtime = noImpurityGroup[label]["publishtime"]
        clusterPublishtime.sort()  # 时间升序
        clusterPublishBeginTime = clusterPublishtime[0]
        clusterPublishEndTime = clusterPublishtime[-1]

        # clusterMember
        cluster_group = map(str, noImpurityGroup[label]["id"])
        clusterMember = "^A".join(cluster_group)

        # cluserMemeberCount
        cluserMemeberCount = len(cluster_group)

        # siteCount
        siteCount = len(noImpurityGroup[label]["sitename"])

        # 构造ClusterObj
        cObj = ClusterObj(clusterId=clusterId, clusterTopic=clusterTopic,
                          clusterPublishBeginTime=clusterPublishBeginTime, clusterPublishEndTime=clusterPublishEndTime,
                          clusterMember=clusterMember, cluserMemeberCount=cluserMemeberCount,
                          siteCount=siteCount)
        cObjArray.append(cObj)
    return cObjArray


# 根据label分组，写到文件
def dbscanLabelZipSententsToTxt(label, mObjArray, targetPath):
    import codecs
    targetFile = codecs.open(targetPath, "w", "utf-8")
    distinctLabel = set(label)
    sententsZiplabel = zip(label, mObjArray)
    for l in distinctLabel:
        targetFile.write(str(l))
        targetFile.write("\n")
        for content in sententsZiplabel:
            if content[0] == l:
                mtitle = unicode(content[1].messageTitle, encoding="utf-8")
                mid = unicode(str(content[1].messageId), encoding="utf-8")
                mpublishtime = unicode(content[1].messagePublishtime, encoding="utf-8")
                targetFile.write(mid + "==" + mpublishtime + "==" + mtitle + "\n")
        targetFile.write("=======================")
        targetFile.write("\n")


def runAlgAndGetReturn(mObjArray, tfidfMatrix):
    label = dbscanCluster(tfidfMatrix, len(mObjArray))
    cObjArray = getReturnData(label, mObjArray)
    # 写到文件
    # targetPath="E:\PycharmProjects\\newsTitleCluster\\result\\r1.txt"
    # dbscanLabelZipSententsToTxt(label,mObjArray,targetPath)
    return cObjArray


########################## 增加'topic message Id' ##########################
def runAlgAndGetReturnWithId(mObjArray, tfidfMatrix):
    label = dbscanCluster(tfidfMatrix, len(mObjArray))
    cObjArray = getReturnDataWithId(label, mObjArray)
    # 写到文件
    # targetPath="E:\PycharmProjects\\newsTitleCluster\\result\\r1.txt"
    # dbscanLabelZipSententsToTxt(label,mObjArray,targetPath)
    return cObjArray


def getReturnDataWithId(label, messageObjList):
    # title和MessageObj 拉链操作
    labelZipMessageObjList = zip(label, messageObjList)
    # 去除-1标签
    noImpurity = filter(lambda (x, y): x != -1, labelZipMessageObjList)
    # 按label分组,统计每个组出现次数最多的title,统计每个组的时间范围
    noImpurityGroup = {}
    for line in noImpurity:
        label = line[0]
        if label not in noImpurityGroup.keys():
            noImpurityGroup[label] = {}
            noImpurityGroup[label]["id"] = []
            # 关注title  出现次数
            noImpurityGroup[label]["title"] = {}
            # 关注publishtime  最大最小
            noImpurityGroup[label]["publishtime"] = []
            noImpurityGroup[label]["id"].append(line[1].messageId)
            noImpurityGroup[label]["title"][line[1].messageTitle] = [line[1].messageId, 1]
            noImpurityGroup[label]["publishtime"].append(line[1].messagePublishtime)
        else:
            noImpurityGroup[label]["id"].append(line[1].messageId)
            noImpurityGroup[label]["publishtime"].append(line[1].messagePublishtime)
            thisTitle = line[1].messageTitle
            if thisTitle not in noImpurityGroup[label]["title"].keys():
                noImpurityGroup[label]["title"][thisTitle] = [line[1].messageId, 1]
            else:
                noImpurityGroup[label]["title"][thisTitle][1] += 1

    # 分组内部 title降序排序 publisttime比较大小 构造ClusterObj
    cObjArray = []
    for (label, value) in noImpurityGroup.items():
        # clusterId
        clusterId = label
        # clusterTopic  对每一title降序排序
        titleGroup = noImpurityGroup[label]["title"]
        sortedTitleGroup = sorted(titleGroup.iteritems(), key=lambda x: x[1][1], reverse=True)
        clusterTopic = sortedTitleGroup[0][0]
        clusterMessageId = str(sortedTitleGroup[0][1][0])
        # clusterPublishtimeRange 对时间排序
        clusterPublishtime = noImpurityGroup[label]["publishtime"]
        clusterPublishtime.sort()  # 时间升序
        clusterPublishtimeRange = clusterPublishtime[0] + "^A" + clusterPublishtime[-1]
        # clusterMember
        clusterMember = "^A".join(map(str, noImpurityGroup[label]["id"]))
        # 构造ClusterObj
        cObj = {"clusterId": clusterId, "clusterTopic": clusterTopic,
                "clusterPublishtimeRange": clusterPublishtimeRange, "clusterMember": clusterMember,
                "clusterMessageId": clusterMessageId}
        cObjArray.append(cObj)
    return cObjArray


def perform_cluster(corpus, num_processes, language_type, save_group_id):
    # 分词,过滤停用词
    articles = [(obj.messageTitle, '') for obj in corpus]
    cut_result = jieba_multipro.multi_cut_words_for_cluster(articles, num_processes)
    logger.info('multi_cut_words_for_cluster....')

    # TF-IDF向量
    tfidf_matrix = tfidfWeight.getTfidf(cut_result, True)
    logger.info('construct_matrix....')

    # DBScan聚类算法
    return runAlgAndGetReturn(corpus, tfidf_matrix)
