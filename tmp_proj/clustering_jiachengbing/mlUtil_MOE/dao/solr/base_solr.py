#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import os
import requests
from utils.logger import logger


class BaseSolr(object):
    # 配置对象
    p_dir = os.path.dirname(os.path.abspath(__file__))
    g_dir = os.path.dirname(p_dir)
    gg_dir = os.path.dirname(g_dir)
    config_path = os.path.join(gg_dir, 'config', 'solr.conf')

    with open(config_path, 'r') as f:
        conf = json.load(f)

    ip = conf['ip']
    port = conf['port']
    collection = conf['collection']

    def __init__(self, q, fq=None, fl=None, start=None, rows=None, sort=None, cursorMark=None):
        self.q = q
        self.fq = fq
        self.fl = fl
        self.start = start
        self.rows = rows
        self.sort = sort
        self.cursorMark = cursorMark

    def get_uri(self):
        uri = u'http://%s:%s/solr/%s/select?wt=json&q=%s' \
              % (BaseSolr.ip, BaseSolr.port, BaseSolr.collection, self.q)

        if self.fq:
            uri = u'%s&fq=%s' % (uri, self.fq)

        if self.fl:
            uri = u'%s&fl=%s' % (uri, self.fl)

        if self.start:
            uri = u'%s&start=%s' % (uri, self.start)

        if self.rows:
            uri = u'%s&rows=%s' % (uri, self.rows)

        if self.sort:
            uri = u'%s&sort=%s' % (uri, self.sort)

        if self.cursorMark:
            uri = u'%s&cursorMark=%s' % (uri, self.cursorMark)

        return uri

    def request(self):
        uri = self.get_uri()
        logger.debug('solr request: {uri: %s}' % uri)
        r = requests.get(self.get_uri(), verify=False)

        return r.json()

    def parse_docs(self, docs):
        ret = []

        fields = self.fl.split(',')
        for doc in docs:
            each = ()
            for field in fields:
                each += (doc[field],)
            ret.append(each)

        return ret

    def search(self):
        rep_json = self.request()

        resp_json = rep_json['response']['docs']
        ret = self.parse_docs(resp_json)
        return ret

    def cursor_search(self):
        logger.info('start cursor_search.')
        ret = []

        resp_json = self.request()

        numFound = resp_json['response']['numFound']
        logger.debug('{cursor_search numFound: %s}' % numFound)

        docs = resp_json['response']['docs']

        while len(docs) != 0:
            each = self.parse_docs(docs)
            ret.extend(each)

            self.cursorMark = resp_json['nextCursorMark']
            resp_json = self.request()
            docs = resp_json['response']['docs']

        logger.info('end cursor_search.')
        return ret


if __name__ == '__main__':
    q = u'content:"导演"'
    fq = u'(groupId:1 OR groupId:17) AND publishtime:[2018-05-20T17:33:18Z TO 2018-05-29T17:33:18Z]'
    fl = u'id'
    start = u'0'
    rows = u'50'
    sort = u'id+desc'
    cursorMark = u'*'
    a = BaseSolr(q=q, fq=fq, fl=fl, start=start,
                 rows=rows,
                 sort=sort, cursorMark=cursorMark)

    ids = a.cursor_search()
    print ids
