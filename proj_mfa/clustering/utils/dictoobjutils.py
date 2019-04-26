#!/usr/bin/env python
# -*- coding: utf-8 -*-
from entity import ClusterMessageObj
from entity import WeightMessageObj
from entity import ClusterObj


def dic_clusterobj(dic):
    msg = ClusterMessageObj()
    msg.__dict__ = dic
    return msg


def dic_weightobj(dic):
    msg = WeightMessageObj()
    msg.__dict__ = dic
    return msg


def dic_cluster_obj(dic):
    msg = ClusterObj()
    msg.__dict__ = dic
    return msg
