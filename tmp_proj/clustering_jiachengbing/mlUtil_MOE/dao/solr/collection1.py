#!/usr/bin/env python
# -*- coding: utf-8 -*-

from base_solr import BaseSolr
from dao.mysql.base_data_view import group_id_dict


def get_ids_from_solr_involved_china(group_id, topic_words, begin_time, end_time):
    q_list = []
    for topic_word in topic_words.split('+'):
        q_list.append(u'content:"' + topic_word + u'"')
    q = u' AND '.join(q_list)

    involved_list = [u"china", u"chinese", u"china‘s xi", u"wang yi", u"beijing", u"bei jing"]
    involved_list = [u'content:"' + word + u'"' for word in involved_list]
    involved_str = u' OR '.join(involved_list)
    involved_str = u'(' + involved_str + u')'
    q = q + u' AND ' + involved_str

    fq_id_list = []
    get_group_ids = group_id_dict[group_id][0]
    for group_id in get_group_ids:
        fq_id_list.append(u'groupId:' + str(group_id))
    fq_id = u' OR '.join(fq_id_list)
    fq_id = u'(' + fq_id + u')'

    begin_time = begin_time.strftime("%Y-%m-%dT%H:%M:%SZ")
    end_time = end_time.strftime("%Y-%m-%dT%H:%M:%SZ")
    fq_publishtime = u'publishtime:[' + begin_time + u' TO ' + end_time + u']'
    fq = u' AND '.join([fq_id, fq_publishtime])

    fl = u'id'
    start = u'0'
    rows = u'50'
    sort = u'id+desc'
    cursorMark = u'*'

    a = BaseSolr(q=q, fq=fq, fl=fl,
                 start=start,
                 rows=rows,
                 sort=sort, cursorMark=cursorMark)

    # ids = a.search()
    ids = a.cursor_search()
    return ids


def get_ids_from_solr(group_id, topic_words, begin_time, end_time):
    q_list = []
    for topic_word in topic_words.split('+'):
        q_list.append(u'content:"' + topic_word + u'"')
    q = u' AND '.join(q_list)

    fq_id_list = []
    get_group_ids = group_id_dict[group_id][0]
    for group_id in get_group_ids:
        fq_id_list.append(u'groupId:' + str(group_id))
    fq_id = u' OR '.join(fq_id_list)
    fq_id = u'(' + fq_id + u')'

    begin_time = begin_time.strftime("%Y-%m-%dT%H:%M:%SZ")
    end_time = end_time.strftime("%Y-%m-%dT%H:%M:%SZ")
    fq_publishtime = u'publishtime:[' + begin_time + u' TO ' + end_time + u']'
    fq = u' AND '.join([fq_id, fq_publishtime])

    fl = u'id'
    start = u'0'
    rows = u'50'
    sort = u'id+desc'
    cursorMark = u'*'

    a = BaseSolr(q=q, fq=fq, fl=fl,
                 start=start,
                 rows=rows,
                 sort=sort, cursorMark=cursorMark)

    # ids = a.search()
    ids = a.cursor_search()
    return ids
