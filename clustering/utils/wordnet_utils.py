#!/usr/bin/env python
# -*- coding: utf-8 -*-
import nltk
from nltk import word_tokenize, pos_tag
from nltk.corpus import wordnet as wn
from logger import logger
from entity import ClusterObj
import time

STOP = set(nltk.corpus.stopwords.words("english"))


class Sentence:
    def __init__(self, sentence):
        self.raw = sentence
        normalized_sentence = sentence.replace("‘", "'").replace("’", "'")
        self.tokens = [t.lower() for t in nltk.word_tokenize(normalized_sentence)]
        self.tokens_without_stop = [t for t in self.tokens if t not in STOP]


def penn_to_wn(tag):
    """ Convert between a Penn Treebank tag to a simplified Wordnet tag """
    if tag.startswith('N'):
        return 'n'

    if tag.startswith('V'):
        return 'v'

    if tag.startswith('J'):
        return 'a'

    if tag.startswith('R'):
        return 'r'

    return None


def tagged_to_synset(word, tag):
    wn_tag = penn_to_wn(tag)
    if wn_tag is None:
        return None

    try:
        return wn.synsets(word, wn_tag)[0]
    except:
        return None


def symmetric_sentence_similarity(sentence1, sentence2):
    """ compute the symmetric sentence similarity using Wordnet """
    return (sentence_similarity(sentence1, sentence2) + sentence_similarity(sentence2, sentence1)) / 2


def sentence_similarity(sentence1, sentence2):
    """ compute the sentence similarity using Wordnet """
    # Tokenize and tag
    sentence1 = pos_tag(word_tokenize(sentence1))
    sentence2 = pos_tag(word_tokenize(sentence2))

    # Get the synsets for the tagged words
    synsets1 = [tagged_to_synset(*tagged_word) for tagged_word in sentence1]
    synsets2 = [tagged_to_synset(*tagged_word) for tagged_word in sentence2]

    # Filter out the Nones
    synsets1 = [ss for ss in synsets1 if ss]
    synsets2 = [ss for ss in synsets2 if ss]

    score, count = 0.0, 0

    # For each word in the first sentence
    for synset in synsets1:
        # Get the similarity value of the most similar word in the other sentence
        scores = [float(synset.path_similarity(ss) or 0) for ss in synsets2]
        # print(scores)

        if len(scores) == 0:
            best_score = 0
        else:
            best_score = max(scores)

        # Check that the similarity could have been computed
        if best_score is not None:
            score += best_score
            count += 1

    # Average the values
    if count == 0:
        score = 0
    else:
        score /= count
    return score


def get_clusters(topic_list, corpus):
    """
    获得指定topic的簇列表
    :param topic_list:  topic_list
    :param corpus: 语料
    :return:
    """
    start_time = time.time()
    logger.debug("start get_clusters, {topic_list: %s, corpus: %s}" % (len(topic_list), len(corpus)))

    cluster_dict = {}  # 簇map, cluster_id  -> [obj, obj]

    for obj in corpus:
        id = obj.messageId
        title = obj.messageTitle
        publishtime = obj.messagePublishtime
        site_name = obj.site_name

        # data_tuple = (group_id, topic_id, subject_id, topic_name, topic_words)
        for topic in topic_list:
            # group_id = topic[0]
            topic_id = topic[1]
            subject_id = topic[2]
            topic_name = topic[3]
            topic_words = topic[4]

            topic_words = topic_words.split('+')
            cluster_topic = ' '.join(topic_words)

            similarity = symmetric_sentence_similarity(title, cluster_topic)
            if similarity > 0.6:
                if not cluster_dict.has_key((topic_id, subject_id, topic_name)):
                    cluster_dict[(topic_id, subject_id, topic_name)] = []

                cluster_dict[(topic_id, subject_id, topic_name)].append((id, title, publishtime, site_name))

    # parse to ClusterObj,  so that save it
    cluster_result = []
    for key, value in cluster_dict.items():
        cluster_id = key[0]
        subject_id = key[1]
        cluster_topic = key[2]

        publish_times = [member[2] for member in value]
        publish_times.sort()
        publish_begin_time = publish_times[0]
        public_end_time = publish_times[-1]

        member_ids = [member[0] for member in value]
        member_ids_str = '^A'.join([str(id) for id in member_ids])

        member_count = len(member_ids)

        site_count = len(set([member[3] for member in value]))

        # 构造ClusterObj
        cluster_obj = ClusterObj(clusterId=cluster_id, clusterTopic=cluster_topic,
                          clusterPublishBeginTime=publish_begin_time, clusterPublishEndTime=public_end_time,
                          clusterMember=member_ids_str, cluserMemeberCount=member_count,
                          siteCount=site_count, is_manual=1, manual_id=subject_id, subtopic_id=cluster_id)

        cluster_result.append(cluster_obj)

    logger.debug("end get_clusters, {cluster_result: %s, cost_time: %ss}" % (len(cluster_result), time.time() - start_time))
    return cluster_result


if __name__ == '__main__':

    sentences = [
        # "Dogs are awesome.",
        # "Some gorgeous creatures are felines.",
        # "Dolphins are swimming mammals.",
        # "Cats are beautiful animals.",
        # "the secret of parliament hill centr block",
        "Brilliant Bale breaks Liverpool hearts as Real Madrid win Champions League"
    ]

    focus_sentence = "Real Madrid beat Liverpool to win Champions League"

    for sentence in sentences:
        print("SymmetricSimilarity(\"%s\", \"%s\") = %s" % (
            focus_sentence, sentence, symmetric_sentence_similarity(focus_sentence, sentence)))
        print("SymmetricSimilarity(\"%s\", \"%s\") = %s" % (
            sentence, focus_sentence, symmetric_sentence_similarity(sentence, focus_sentence)))
        print
