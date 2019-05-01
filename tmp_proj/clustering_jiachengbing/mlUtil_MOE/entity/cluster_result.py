#!/usr/bin/env python
# -*- coding: utf-8 -*-


class SubClusterResult(object):
    def __init__(self, cluster_id, topic, publish_begin_time, publish_end_time,
                 member, member_count, site_count, cluster_result_id, cluster_type,
                 language_type, group_id, is_manual, manual_id, subtopic_id):
        self.cluster_id = cluster_id
        self.topic = topic
        self.publish_begin_time = publish_begin_time
        self.publish_end_time = publish_end_time
        self.member = member
        self.member_count = member_count
        self.site_count = site_count
        self.cluster_result_id = cluster_result_id
        self.cluster_type = cluster_type
        self.language_type = language_type
        self.group_id = group_id
        self.is_manual = is_manual
        self.manual_id = manual_id
        self.subtopic_id = subtopic_id


class MergerClusterResult(object):
    def __init__(self, id, cluster_id, topic, publish_begin_time, publish_end_time,
                 member, member_count, site_count, cluster_type,
                 language_type, group_id, is_manual, manual_id, subtopic_id,
                 sub_cluster_results=[], order_id=-1, keyword_id=-1):
        self.id = id
        self.cluster_id = cluster_id
        self.topic = topic
        self.publish_begin_time = publish_begin_time
        self.publish_end_time = publish_end_time
        self.member = member
        self.member_count = member_count
        self.site_count = site_count
        self.cluster_type = cluster_type
        self.language_type = language_type
        self.group_id = group_id
        self.is_manual = is_manual
        self.manual_id = manual_id
        self.subtopic_id = subtopic_id
        self.sub_cluster_results = sub_cluster_results
        self.order_id = order_id
        self.keyword_id = keyword_id

    def set_sub_clusters(self, sub_cluster_results):
        self.sub_cluster_results = sub_cluster_results
