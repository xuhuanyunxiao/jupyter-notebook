#!/usr/bin/env python
# -*- coding: utf-8 -*-

import operator
import random
from cluster.feature import jieba_multipro
# from dao.mysql.spokesman_keyword import SpokesmanKeyword
from utils import unionfind
from utils import java_hashcode
from gensim.summarization import keywords
from utils.logger import logger
from sklearn.cluster import DBSCAN
import jieba
from cluster.feature import tfidfWeight, nltk_multipro
from entity.ClusterObj import ClusterObj
from multiprocessing import cpu_count
import uuid
import sys


def get_eps_min(size, save_group_id, is_content):
    # 第二次聚类
    if is_content:
        if size > 20000:
            _eps = 0.7
            _min_samples = 3
        else:
            _eps = 1.0
            _min_samples = 2
    else:
        if size > 20000:
            _eps = 0.7
            _min_samples = 3
        elif size > 10000:
            _eps = 0.8
            _min_samples = 3
        elif size > 5000:
            _eps = 0.9
            _min_samples = 3
        elif size > 2000:
            _eps = 0.95
            _min_samples = 3
        elif size > 200:
            _eps = 1.0
            _min_samples = 3
        else:
            _eps = 1.0
            _min_samples = 2
    return _eps, _min_samples


# 二次聚类
def first_cluster(corpus, vectors, save_group_id, language_type):
    # 第一次聚类
    labels = dbscan_cluster(vectors, len(corpus), save_group_id)

    # 获得结果
    ret = first_return_data(labels, corpus, language_type)
    return ret


def dbscan_cluster(vectors, size, save_group_id, is_content=False):
    _eps, _min_samples = get_eps_min(size, save_group_id, is_content)
    dbscan = DBSCAN(eps=_eps, min_samples=_min_samples)
    dbscan.fit_predict(vectors)
    return dbscan.labels_


def first_return_data(labels, corpus, language_type):
    label_corpus = zip(labels, corpus)

    # 去除-1标签
    # filter_label_corpus = filter(lambda (x, y): x != -1, label_corpus)
    filter_label_corpus = filter(lambda x, y: x != -1, label_corpus)

    # 按label分组, 统计每个组内出现的最长文章
    purity_group = {}
    for line in filter_label_corpus:
        label = line[0]
        id = line[1].messageId
        title = line[1].messageTitle
        content = line[1].messageContent
        publish_time = line[1].messagePublishtime
        site_name = line[1].site_name

        if label not in purity_group.keys():
            purity_group[label] = {}
            purity_group[label]["ids"] = []
            purity_group[label]["titles"] = {}
            purity_group[label]["contents"] = []
            purity_group[label]["site_names"] = set()
            purity_group[label]["publish_times"] = []

        purity_group[label]["ids"].append(id)
        purity_group[label]["site_names"].add(site_name)
        purity_group[label]["publish_times"].append(publish_time)

        # 英文
        if language_type == 1 and len(content) > 100 and title.lower().find('summary') == -1 \
                and title.lower().find('morning') == -1:
            purity_group[label]["contents"].append(content)

        # 中文
        if language_type == 0 and site_name.find('手机') == -1 \
                and title.find('问') == -1 and title.find('答') == -1 and title.find('早报')  == -1 \
                and title.find('快讯') == -1 and title.find('有料') == -1 \
                and title.find('早安') == -1 and title.find('要闻') == -1 \
                and content.find('图集') == -1 and len(content) > 10:
            purity_group[label]["contents"].append(content)

        if title not in purity_group[label]["titles"].keys():
            purity_group[label]["titles"][title] = 1
        else:
            purity_group[label]["titles"][title] += 1

    # 组合title, publish_time 字段
    cluster_result = {}
    for label, value in purity_group.items():
        # cluster_topic  对每一title降序排序
        titles = purity_group[label]["titles"]
        sorted_titles = sorted(titles.iteritems(), key=operator.itemgetter(1), reverse=True)
        cluster_topic = sorted_titles[0][0]

        # contents
        contents = purity_group[label]["contents"]
        key_words_map = {}
        for content in contents:
            words = get_keywords(content, language_type, 50)

            for word in words:
                if key_words_map.has_key(word):
                    key_words_map[word] += 1
                else:
                    key_words_map[word] = 1
        sorted_key_words = sorted(key_words_map.items(), lambda x, y: cmp(x[1], y[1]), reverse=True)
        sorted_key_words = [t[0] for t in sorted_key_words]
        if len(sorted_key_words) > 10:
            key_words = sorted_key_words[:10]
        else:
            key_words = sorted_key_words

        # cluster_message
        cluster_message = '@'.join(key_words)

        # publish_times
        publish_times = purity_group[label]["publish_times"]

        # ids
        ids = map(str, purity_group[label]["ids"])

        # site_names
        site_names = purity_group[label]["site_names"]

        # 构造 cluster_result
        cluster_result[label] = {}
        cluster_result[label]["ids"] = ids
        cluster_result[label]["site_names"] = site_names
        cluster_result[label]["cluster_topic"] = cluster_topic
        cluster_result[label]["publish_times"] = publish_times
        cluster_result[label]["cluster_message"] = cluster_message

    return cluster_result


def second_cluster(second_corpus, vectors, save_group_id):
    # 二次聚类的特殊参数
    labels = dbscan_cluster(vectors, -1, save_group_id, True)

    # 获得结果
    ret = second_return_data(labels, second_corpus)
    return ret


def second_return_data(labels, second_corpus):
    label_corpus = zip(labels, second_corpus)

    # 去除-1标签
    # filter_label_corpus = filter(lambda (x, y): x != -1, label_corpus)
    filter_label_corpus = filter(lambda x, y: x != -1, label_corpus)

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


def return_data(cluster_ids_list, first_cluster_results, is_manual,
                cluster_type, manual_id, subtopic_id, language_type, save_group_id):
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
        # id
        id = get_cluster_result_id()

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
        cObj = ClusterObj(id, clusterId, clusterTopic,
                          clusterPublishBeginTime, clusterPublishEndTime,
                          clusterMember, cluserMemeberCount,
                          siteCount, cluster_type,
                          language_type, save_group_id,
                          is_manual, manual_id, subtopic_id)
        cObjArray.append(cObj)

    # 增加排序
    sort_bywords(cObjArray)

    return cObjArray


def sort_bywords(list):
    """ 根据关键词对类别进行排序 """
    results = SpokesmanKeyword().get_words()

    for cluster in list:
        topic_name = cluster.topic
        keyword_id = -1
        priority = sys.maxint
        for result in results:
            keyword = result['keyword']
            if keyword in topic_name:
                keyword_id = result['id']
                priority = result['priority']
                break
        cluster.keyword_id = keyword_id
        cluster.priority = priority

    # 排序
    list.sort(sort_cmp)

    # 赋值order_id
    for idx, cluster in enumerate(list):
        cluster.order_id = idx + 1


def sort_cmp(a, b):
    if a.priority == b.priority:
        if a.site_count == b.site_count:
            return int(b.member_count - a.member_count)
        else:
            return int(b.site_count - a.site_count)
    else:
        return int(a.priority - b.priority)


def get_num_processes(corpus_length):
    # 计算num_processes
    num_processes = cpu_count() / 4
    if corpus_length > 30000:
        num_processes = cpu_count()
    elif corpus_length > 10000:
        num_processes = cpu_count() / 2
    num_processes = 4

    return num_processes


def perform_cluster(is_manual, cluster_type, manual_id, subtopic_id, language_type,
                    corpus, save_group_id):
    corpus_length = len(corpus)
    if corpus_length == 0:
        logger.info('perform_cluster returning run, because len(corpus) == 0')
        return

    num_processes = get_num_processes(corpus_length)

    # 分词,过滤停用词
    first_articles = [(obj.messageTitle, '') for obj in corpus]

    if language_type == 0:
        first_cut_result = jieba_multipro.multi_cut_words_for_cluster(first_articles, num_processes)
    if language_type == 1:
        first_cut_result = nltk_multipro.multi_cut_words(first_articles, num_processes)

    logger.info('first multi_cut_words_for_cluster....')

    # 构建TF-IDF矩阵
    first_tfidf_matrix = tfidfWeight.getTfidf(first_cut_result, True, True)
    logger.info('first construct_matrix....')

    # DBScan聚类算法
    first_cluster_results = first_cluster(corpus, first_tfidf_matrix, save_group_id, language_type)
    logger.info('first first_cluster....')

    for label, dict_ in first_cluster_results.items():
        logger.debug('label:%d, cluster_topic: %s, ids: %s' % (label, dict_['cluster_topic'], '-'.join(dict_['ids'])))

    # 如果第一次聚类结果为null
    cluster_results = []
    if len(first_cluster_results) == 0:
        logger.info('first_cluster_results 为空, 随机选择10条数据作为聚类结果....')
        cluster_results = get_result_corpus(corpus, is_manual, cluster_type, manual_id, subtopic_id, language_type, save_group_id)
    else:
        # 二次聚类, 根据topic
        second_corpus = [(label, topic['cluster_message']) for (label, topic) in first_cluster_results.items() if topic['cluster_message'] != '']
        second_articles = [article[1] for article in second_corpus]
        for label, message in second_corpus:
            logger.debug('label:%d, message: %s' % (label, message))

        # 如果第二次聚类语料为null, 则直接返回第一次聚类结果
        if len(second_articles) == 0:
            cluster_results = get_result(first_cluster_results, is_manual,
                                         cluster_type, manual_id, subtopic_id, language_type, save_group_id)
        else:
            # 构建TF-IDF矩阵
            second_tfidf_matrix = tfidfWeight.getTfidf(second_articles, True, True)
            logger.info('second construct_matrix....')

            # DBScan聚类算法
            second_cluster_results = second_cluster(second_corpus, second_tfidf_matrix, save_group_id)
            logger.info('second second_cluster....')

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

            cluster_results = return_data(ids_list, first_cluster_results, is_manual,
                                          cluster_type, manual_id, subtopic_id, language_type, save_group_id)
            logger.info('cluster_results....')
    return cluster_results


def get_result(first_cluster_results, is_manual,
               cluster_type, manual_id, subtopic_id, language_type, save_group_id):
    """
    如果第二次聚类语料为null, 则直接返回第一次聚类结果
    :param first_cluster_results:
    :return:
    """
    ids = [[key] for key, cluster_result in first_cluster_results.items()]
    return return_data(ids, first_cluster_results, is_manual,
                       cluster_type, manual_id, subtopic_id, language_type, save_group_id)


def get_result_corpus(corpus, is_manual,
                      cluster_type, manual_id, subtopic_id, language_type, save_group_id):
    """
    当first_cluster_results 为空, 随机选择10条数据作为聚类结果返回.
    :return:
    """
    random_corpus = []
    if len(corpus) > 10:
        random_corpus = random.sample(corpus, 10)  # 从list中随机获取10个元素
    else:
        random_corpus = corpus

    cObjArray = []
    for idx, cluster_message_obj in enumerate(random_corpus):
        # id
        id = get_cluster_result_id()

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
        cObj =  ClusterObj(id, clusterId, clusterTopic,
                           clusterPublishBeginTime, clusterPublishEndTime,
                           clusterMember, cluserMemeberCount,
                           siteCount, cluster_type,
                           language_type, save_group_id,
                           is_manual, manual_id, subtopic_id)
        cObjArray.append(cObj)

    # 增加排序
    sort_bywords(cObjArray)

    return cObjArray


def get_keywords(content, language_type, topN=50):
    word_list = []
    try:
        if language_type == 1:
            words = keywords(content, ratio=0.2, split='\n', pos_filter=None, lemmatize=True)
            word_list = words

        if language_type == 0:
            words = jieba.analyse.extract_tags(content, topK=topN)
            word_list = words
    except Exception as e:
        logger.error('get_keywords error, content: %s, exception: %s' % (content, e))

    return word_list


def get_word_weights(content, topN=50):
    user_dict_path, dicts, stopwords, top_n = jieba_multipro.pre_process(1)
    top_n = topN

    # 从文本中中添加, 自定义词典
    jieba.load_userdict(user_dict_path)

    # 从mysql中添加, 自定义词典
    for dic in dicts:
        jieba.add_word(dic[1].encode('utf-8'))

    word_weights = jieba.analyse.extract_tags(content, topK=top_n, withWeight=True)
    word_weight_list = []
    for word_weight in word_weights:
        word = word_weight[0]
        if not stopwords.has_key(word):
            word_weight_list.append(word_weight)

    return word_weight_list


def get_cluster_result_id():
    """ 获得id """
    name = uuid.uuid1()
    hashcode = java_hashcode.get_hashcode(str(name))
    no_negative_hashcode = abs(hashcode)
    return no_negative_hashcode