#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json

import jieba
from entity import ClusterObj


def combine_cluster(lcluster, rcluster):
    """
    合并2个聚类对象
    :param lcluster:
    :param rcluster:
    :return: 新的聚类对象
    """
    new_cluster = ClusterObj()
    new_cluster.clusterId = lcluster.clusterId
    new_cluster.clusterTopic = lcluster.clusterTopic if len(lcluster.clusterTopic) > len(
        rcluster.clusterTopic) else rcluster.clusterTopic
    new_cluster.clusterMember = lcluster.clusterMember + '^A' + rcluster.clusterMember
    new_cluster.clusterPublishtimeRange = lcluster.clusterPublishtimeRange.split('^A')[0] + '^A' + \
                                          rcluster.clusterPublishtimeRange.split('^A')[1]
    new_cluster.clusterSummary = lcluster.clusterSummary if len(lcluster.clusterSummary) > len(
        rcluster.clusterSummary) else rcluster.clusterSummary
    new_cluster.clusterTendency = lcluster.clusterTendency
    return new_cluster


def cluster_similar(old_cluster, new_cluster):
    """
    计算2个聚类的相似度, 并且合并
    :param old_cluster:
    :param new_cluster:
    :return: (老, 新, 全)
    """
    from gensim import corpora, models, similarities
    # 词袋模型
    cluster1_documents = [[word for word in jieba.cut(cluster.clusterTopic, cut_all=True)] for cluster in old_cluster]
    cluster1_dictionary = corpora.Dictionary(cluster1_documents)
    cluster1_bows = [cluster1_dictionary.doc2bow(document) for document in cluster1_documents]
    # TFIDF
    cluster1_tfidf = models.TfidfModel(cluster1_bows)
    cluster1_vectors = cluster1_tfidf[cluster1_bows]
    # 相似性
    similarity = similarities.Similarity('Similarity-tfidf-index', cluster1_vectors, num_features=600)

    # 类别2
    cluster2_documents = [[word for word in jieba.cut(cluster.clusterTopic, cut_all=True)] for cluster in new_cluster]
    cluster2_bows = [cluster1_dictionary.doc2bow(document) for document in cluster2_documents]
    cluster2_vectors = cluster1_tfidf[cluster2_bows]
    similarities = similarity[cluster2_vectors]

    # 最终的结果
    full_collection = []
    left_collection = old_cluster
    right_collection = new_cluster

    # 合并2次聚类结果
    for similarity_index in range(len(similarities)):
        similarity = similarities[similarity_index]
        max = similarity.max()
        if max > 0.85:
            argmax = similarity.argmax()
            # 合并
            left_cluster = left_collection[argmax]
            right_cluster = right_collection[similarity_index]
            full_collection.append(combine_cluster(left_cluster, right_cluster))
            # 减去
            left_cluster.delete = True
            left_collection[argmax] = left_cluster
            right_cluster.delete = True
            right_collection[similarity_index] = right_cluster

    # 合并所有的集合
    full_collection.extend([cluster for cluster in left_collection if not hasattr(cluster, 'delete')])
    full_collection.extend([cluster for cluster in right_collection if not hasattr(cluster, 'delete')])

    # 修改clusterId
    for idx, item in enumerate(full_collection):
        item.clusterId = idx

    return full_collection


if __name__ == '__main__':
    # 第一次聚类结果
    old_cluster = []
    cluster11 = ClusterObj(clusterId=0, clusterTopic='农民工领取1400万元欠薪,现金堆满桌', clusterSummary='农民工领取欠薪,现金堆满桌',
                           clusterTendency='0', clusterPublishtimeRange='2017-01-22 11:11:11^A2017-02-22 11:11:11',
                           clusterMember='111^A112^A113^A114^A115')
    cluster12 = ClusterObj(clusterId=1, clusterTopic='中国首个超200米高空超长超重弧形观景天桥起吊',
                           clusterSummary='中国首个超200米高空超长超重弧形观景天桥起吊', clusterTendency='0',
                           clusterPublishtimeRange='2017-01-22 11:11:11^A2017-02-22 11:11:11',
                           clusterMember='121^A122^A123^A124^A125')
    cluster13 = ClusterObj(clusterId=2, clusterTopic='中东部地区将有雨雪天气,局地降温达10℃以上', clusterSummary='中东部地区将有雨雪天气,局地降温达10℃以上',
                           clusterTendency='0', clusterPublishtimeRange='2017-01-22 11:11:11^A2017-02-22 11:11:11',
                           clusterMember='131^A132^A133^A134^A135')
    old_cluster.append(cluster11)
    old_cluster.append(cluster12)
    old_cluster.append(cluster13)

    # 第二次聚类结果
    new_cluster = []
    cluster21 = ClusterObj(clusterId=0, clusterTopic='中国首个高空超长超重弧形观景天桥起吊', clusterSummary='中国首个高空超长超重弧形观景天桥起吊',
                           clusterTendency='0', clusterPublishtimeRange='2017-02-22 11:11:11^A2017-03-22 11:11:11',
                           clusterMember='211^A212^A213^A214^A215')
    cluster22 = ClusterObj(clusterId=0, clusterTopic='农民工领取欠薪,现金堆满桌', clusterSummary='农民工领取1400万元欠薪,现金堆满桌',
                           clusterTendency='0', clusterPublishtimeRange='2017-02-22 11:11:11^A2017-03-22 11:11:11',
                           clusterMember='221^A222^A223^A224^A225')
    cluster23 = ClusterObj(clusterId=0, clusterTopic='越王剑、龙形玉佩等珍宝河南淮阳出土后亮相', clusterSummary='越王剑、龙形玉佩等珍宝河南淮阳出土后亮相',
                           clusterTendency='0', clusterPublishtimeRange='2017-02-22 11:11:11^A2017-03-22 11:11:11',
                           clusterMember='231^A232^A233^A234^A235')
    new_cluster.append(cluster21)
    new_cluster.append(cluster22)
    new_cluster.append(cluster23)

    # 聚类
    full_collection = cluster_similar(old_cluster, new_cluster)
    print json.dumps([cluster.__dict__ for cluster in full_collection], ensure_ascii=False)
