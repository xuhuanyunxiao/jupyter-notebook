#!/usr/bin/env python
# -*- coding: utf-8 -*-


class ClusterMessageObj(object):
    """
    聚类实体类
    """

    def __init__(self, messageId=0, messageTitle='', messagePublishtime='', messageContent='', site_name=''):
        self.messageId = messageId
        self.messageTitle = messageTitle
        self.messagePublishtime = messagePublishtime
        self.messageContent = messageContent
        self.site_name = site_name
