#!/usr/bin/env python
# -*- coding: utf-8 -*-
from hbase import Hbase
from hbase.ttypes import *
from thrift.transport import TSocket
import jsonpickle


def get_cluster(rowkey):
    """
    从hbase中表中, 获得cluster集合
    :param rowkey:
    :return:
    """
    client = client_conn()
    result = client.getRow('cluster_es', rowkey)
    if len(result) > 0:
        columns = result[0].columns
        full_cluster_str = columns.get('0:full_cluster').value
        full_cluster = jsonpickle.decode(full_cluster_str)
        return full_cluster
    else:
        return None


def put_cluster(rowkey, full_cluster, old_cluster=None, new_cluster=None, query_string=None):
    """
    向hbase中表中, 插入指定的数据
    :param rowkey:
    :param old_cluster:
    :param new_cluster:
    :param full_cluster:
    :return:
    """
    client = client_conn()
    full_cluster_str = jsonpickle.encode(full_cluster)
    mutation_full = [Mutation(column="0:full_cluster", value=full_cluster_str)]
    client.mutateRow('cluster_es', rowkey, mutation_full)

    # 如果old_cluster不为null, 则插入
    if old_cluster is not None:
        old_cluster_str = jsonpickle.encode(old_cluster)
        mutation_old = [Mutation(column="0:old_cluster", value=old_cluster_str)]
        client.mutateRow('cluster_es', rowkey, mutation_old)

    # 如果new_cluster不为null, 则插入
    if new_cluster is not None:
        new_cluster_str = jsonpickle.encode(new_cluster)
        mutation_new = [Mutation(column="0:new_cluster", value=new_cluster_str)]
        client.mutateRow('cluster_es', rowkey, mutation_new)

    # 如果query_string不为null, 则插入
    if query_string is not None:
        query_string_encode = jsonpickle.encode(query_string)
        mutation_query = [Mutation(column="0:query_string", value=query_string_encode)]
        client.mutateRow('cluster_es', rowkey, mutation_query)


def client_conn():
    # server端地址和端口,web是HMaster也就是thriftServer主机名,9090是thriftServer默认端口
    transport = TSocket.TSocket("saas5", 9090)
    # 可以设置超时
    transport.setTimeout(5000)
    # 设置传输方式（TFramedTransport或TBufferedTransport）
    trans = TTransport.TBufferedTransport(transport)
    # 设置传输协议
    protocol = TBinaryProtocol.TBinaryProtocol(trans)
    # 确定客户端
    client = Hbase.Client(protocol)
    # 打开连接
    transport.open()
    return client


if __name__ == "__main__":
    client = client_conn()
    rowkey = '550e8400-e29b-41d4-a716-446655440000'

    # 插入数据
    # full_cluster = []
    # cluster11 = ClusterObj(clusterId=0, clusterTopic='中国首个高空超长超重弧形观景天桥起吊', clusterSummary='中国首个高空超长超重弧形观景天桥起吊',
    #                        clusterTendency='0', clusterPublishtimeRange='2017-02-22 11:11:11^A2017-03-22 11:11:11',
    #                        clusterMember='211^A212^A213^A214^A215')
    # full_cluster.append(cluster11)
    #
    # cluster12 = ClusterObj(clusterId=0, clusterTopic='中国首个高空超长超重弧形观景天桥起吊', clusterSummary='中国首个高空超长超重弧形观景天桥起吊',
    #                        clusterTendency='0', clusterPublishtimeRange='2017-02-22 11:11:11^A2017-03-22 11:11:11',
    #                        clusterMember='211^A212^A213^A214^A215')
    # full_cluster.append(cluster12)
    #
    # put_cluster(rowkey, full_cluster=full_cluster)

    # 获取数据
    client = client_conn()
    result = client.getRow('cluster_es', rowkey)
    if len(result) > 0:
        columns = result[0].columns
        print columns.get('0:full_cluster').value
        print columns.get('0:new_cluster').value
        print columns.get('0:old_cluster').value
        print columns.get('0:query_string').value
