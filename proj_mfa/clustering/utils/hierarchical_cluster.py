#!/usr/bin/env python
# -*- coding: utf-8 -*-

import operator
import random
import scipy.cluster.hierarchy as sch
from entity.ClusterObj import ClusterObj
from logger import logger
from utils import nltk_multipro_new
import unionfind


def hierarchy_cluster(tfidf_matrix):
    # 1. 层次聚类
    # 生成点与点之间的距离矩阵,这里用的欧氏距离:
    disMat = sch.distance.pdist(tfidf_matrix, 'cosine')

    # 进行层次聚类:
    Z = sch.linkage(disMat, method='average')

    # 将层级聚类结果以树状图表示出来并保存为plot_dendrogram.png
    # P=sch.dendrogram(Z)
    # plt.savefig('plot_dendrogram.png')

    # 根据linkage matrix Z得到聚类结果:
    labels = sch.fcluster(Z, t=0.70, criterion='distance')
    return labels


def second_get_return_data(labels, second_corpus):
    label_corpus = zip(labels, second_corpus)

    # 去除-1标签
    filter_label_corpus = filter(lambda (x, y): x != -1, label_corpus)

    # 按label分组,统计每个组出现次数最多的title,统计每个组的时间范围
    purity_group = {}
    for label_corpu in filter_label_corpus:
        label = label_corpu[0]
        first_cluster_id = label_corpu[1][0]
        first_cluster_topic = label_corpu[1][1]

        if label not in purity_group.keys():
            purity_group[label] = {}

        if first_cluster_id not in purity_group[label].keys():
            purity_group[label][first_cluster_id] = []

        purity_group[label][first_cluster_id].append((first_cluster_topic))

    return purity_group


def first_get_return_data(labels, corpus):
    label_corpus = zip(labels, corpus)

    # 去除-1标签
    filter_label_corpus = label_corpus

    # 按label分组, 统计每个组内出现的最长文章
    purity_group = {}
    for line in filter_label_corpus:
        label = line[0]
        id = line[1].messageId
        title = line[1].messageTitle
        publish_time = line[1].messagePublishtime
        site_name = line[1].site_name

        if label not in purity_group.keys():
            purity_group[label] = {}
            purity_group[label]["ids"] = []
            purity_group[label]["titles"] = {}
            purity_group[label]["title_list"] = []
            purity_group[label]["site_names"] = set()
            purity_group[label]["publish_times"] = []

        purity_group[label]["ids"].append(id)
        purity_group[label]["site_names"].add(site_name)
        purity_group[label]["publish_times"].append(publish_time)
        purity_group[label]["title_list"].append(title)

        if title not in purity_group[label]["titles"].keys():
            purity_group[label]["titles"][title] = 1
        else:
            purity_group[label]["titles"][title] += 1

    # 组合title, publish_time 字段
    cluster_result = {}
    for label, value in purity_group.items():
        # ids
        ids = map(str, purity_group[label]["ids"])

        # cluster_topic  对每一title降序排序
        titles = purity_group[label]["titles"]
        sorted_titles = sorted(titles.iteritems(), key=operator.itemgetter(1), reverse=True)
        cluster_topic = sorted_titles[0][0]

        # title_list
        title_list = purity_group[label]["title_list"]

        # publish_times
        publish_times = purity_group[label]["publish_times"]

        # site_names
        site_names = purity_group[label]["site_names"]

        # 构造 cluster_result
        cluster_result[label] = {}
        cluster_result[label]["ids"] = ids
        cluster_result[label]["site_names"] = site_names
        cluster_result[label]["cluster_topic"] = cluster_topic
        cluster_result[label]["publish_times"] = publish_times
        cluster_result[label]["title_list"] = title_list

    return cluster_result


def run_cluster(tfidf_matrix):
    """
    层次聚类
    :param tfidf_matrix:
    :param mObjArray:
    :return:
    """
    label = hierarchy_cluster(tfidf_matrix.toarray())
    return label


def get_result_corpus(corpus):
    """
    当first_cluster_results 为空, 随机选择10条数据作为聚类结果返回.
    :param corpus:
    :return:
    """
    random_corpus = []
    if len(corpus) > 10:
        random_corpus = random.sample(corpus, 10)  # 从list中随机获取10个元素
    else:
        random_corpus = corpus

    cObjArray = []
    for idx, cluster_message_obj in enumerate(random_corpus):
        # clusterId
        clusterId = idx

        # clusterTopic  对每一title降序排序
        clusterTopic = cluster_message_obj.messageTitle

        # clusterPublishtimeRange 对时间排序
        clusterPublishBeginTime = cluster_message_obj.messagePublishtime
        clusterPublishEndTime = cluster_message_obj.messagePublishtime

        # clusterMember
        clusterMember = str(cluster_message_obj.messageId)

        # cluserMemeberCount
        cluserMemeberCount = 1

        # siteCount
        siteCount = 1

        # 构造ClusterObj
        cObj = ClusterObj(clusterId=clusterId, clusterTopic=clusterTopic,
                          clusterPublishBeginTime=clusterPublishBeginTime, clusterPublishEndTime=clusterPublishEndTime,
                          clusterMember=clusterMember, cluserMemeberCount=cluserMemeberCount,
                          siteCount=siteCount)
        cObjArray.append(cObj)
    return cObjArray


def perform_cluster(corpus, num_processes, min_sample):
    first_articles = [(obj.messageTitle, obj.messageContent) for obj in corpus]
    first_cut_results = nltk_multipro_new.multi_cut_words(first_articles, num_processes)
    logger.info('first_cut_results end....')

    # 构建TF-IDF矩阵
    from utils import tfidfWeight
    first_tf_matrix = tfidfWeight.getTfidf(first_cut_results, True)
    logger.info('first_tfidf_matrix end....')

    # 聚类算法
    first_labels = run_cluster(first_tf_matrix)
    first_cluster_results = first_get_return_data(first_labels, corpus)
    logger.info('first_cluster_results end....')

    for label, dict_ in first_cluster_results.items():
        logger.debug('label:%d, cluster_topic: %s, ids: %s' % (label, dict_['title_list'], '-'.join(dict_['ids'])))

    # 如果第一次聚类结果为null
    cluster_results = []
    if len(first_cluster_results) == 0:
        logger.info('first_cluster_results 为空, 随机选择10条数据作为聚类结果....')
        cluster_results = get_result_corpus(corpus)

    else:
        # 二次聚类, 根据topic
        second_corpus = [(label, topic['title_list']) for (label, topic) in first_cluster_results.items() if '。'.join(topic['title_list']).strip() != '']
        second_articles = [('。'.join(article[1]), '') for article in second_corpus]

        second_cut_results = nltk_multipro_new.multi_cut_words(second_articles, num_processes)
        logger.info('second_cut_results end....')

        ziped_second_corpus_cut_results = zip(second_corpus, second_cut_results)
        ziped_second_corpus_cut_results = filter(lambda t: t[1] != '@' > 0, ziped_second_corpus_cut_results)
        second_corpus = [t[0] for t in ziped_second_corpus_cut_results]
        second_cut_results = [t[1] for t in ziped_second_corpus_cut_results]

        # 构建TF-IDF矩阵
        second_tf_matrix = tfidfWeight.getTfidf(second_cut_results, True)
        logger.info('second_tf_matrix end....')

        second_labels = run_cluster(second_tf_matrix)
        second_cluster_results = second_get_return_data(second_labels, second_corpus)
        logger.info('second_cluster_results end....')

        # 合并聚类结果
        first_ids = [[label] for (label, topic) in first_cluster_results.items()]
        logger.info('first_ids: %s', first_ids)

        second_ids = [clusters.keys() for (label, clusters) in second_cluster_results.items() if (len(clusters)) > 1]
        logger.info('second_ids: %s', second_ids)

        first_ids.extend(second_ids)
        u = unionfind.UnionFind(first_ids)
        u.create_tree()
        ids_list = u.get_tree()
        logger.info('ids_list: %s', ids_list)

        cluster_results = return_data(ids_list, first_cluster_results, min_sample)
        logger.info('cluster_results....')

    return cluster_results


def return_data(cluster_ids_list, first_cluster_results, min_sample):
    cObjArray = []
    for idx, cluster_ids in enumerate(cluster_ids_list):
        cluster_topic = ''
        max_ids_count = 0

        publishtimes = []
        ids = []
        sitenames = set()

        for cluster_id in cluster_ids:
            _ids = map(str, first_cluster_results[cluster_id]["ids"])
            _cluster_topic = first_cluster_results[cluster_id]["cluster_topic"]
            _sitenames = first_cluster_results[cluster_id]["site_names"]
            _publishtimes = first_cluster_results[cluster_id]["publish_times"]

            if len(_ids) > max_ids_count:
                max_ids_count = len(_ids)
                cluster_topic = _cluster_topic

            publishtimes.extend(_publishtimes)
            ids.extend(_ids)
            sitenames = sitenames | _sitenames

        # 构建返回结果
        # clusterId
        clusterId = idx

        # clusterTopic  对每一title降序排序
        clusterTopic = cluster_topic

        # clusterPublishtimeRange 对时间排序
        publishtimes.sort()  # 时间升序
        clusterPublishBeginTime = publishtimes[0]
        clusterPublishEndTime = publishtimes[-1]

        # clusterMember
        clusterMember = "^A".join(ids)

        # cluserMemeberCount
        cluserMemeberCount = len(ids)

        # siteCount
        siteCount = len(sitenames)

        # 构造ClusterObj
        if len(ids) >= min_sample:
            cObj = ClusterObj(clusterId=clusterId, clusterTopic=clusterTopic,
                              clusterPublishBeginTime=clusterPublishBeginTime, clusterPublishEndTime=clusterPublishEndTime,
                              clusterMember=clusterMember, cluserMemeberCount=cluserMemeberCount,
                              siteCount=siteCount)
            cObjArray.append(cObj)
    return cObjArray