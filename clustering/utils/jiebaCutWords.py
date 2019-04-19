#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import re
import jieba
import sys
import jieba.analyse
import jieba.posseg as pseg
from utils import dicutils
import codecs

# 从文本中中添加, 自定义词典
user_dict_path = os.getcwd() + "/dict/userdict.txt"
jieba.load_userdict(user_dict_path)

# 从mysql中添加, 自定义词典
dicts = dicutils.getdics_mysql()
for dic in dicts:
    jieba.add_word(dic[1].encode('utf-8'))

# 停用词语料
stopwords = {}
stopwords_path = os.getcwd() + "/dict/stopWords.txt"
stw = codecs.open(stopwords_path, encoding="utf-8")
for ws in stw.readlines():
    ws = ws.replace("\n", "")
    ws = ws.replace("\r", "")
    ws = ws.strip()
    stopwords[ws] = 1
stw.close()


def onlyTitle(mObjs):
    titleList = []
    for mObj in mObjs:
        title = mObj.messageTitle.strip()
        if len(title) > 0:
            titleList.append(title)
    return titleList


def titleId(mObjs):
    titleList = []
    idList = []
    for mObj in mObjs:
        title = mObj.messageTitle.strip()
        id = mObj.messageId
        if len(title) > 0:
            titleList.append(title)
            idList.append(id)
    return (titleList, idList)


def titleContent(mObjs):
    titleContentList = []
    for mObj in mObjs:
        title = mObj.messageTitle
        content = mObj.messageContent
        titleContentStr = title + " " + content
        titleContentList.append(titleContentStr)
    return titleContentList


def clear_title(title):
    return clear_sen(title)


def clear_content(content):
    """
    获取文章的钱3段内容
    :param content:
    :return:
    """
    # paragraphs = content.split('\n')
    # return "\n".join([clear_sen(paragraph) for paragraph in paragraphs[:3]])
    return clear_sen(content)


def clear_sen(sent):
    """
    过滤内容的中的特殊字符
    :param sent:
    :return:
    """
    regex = u'[’!"#$%&\'()*+,-./:;<=>?@，。?★、…【】《》？“”‘’！[\\]^_`{|}~]+'
    sent = re.sub(regex, '', sent)
    return sent


def is_valid(word):
    """
    remove 标点和特殊字符
    :param s:
    :return:
    """
    # 去掉无意义的term
    if len(word) < 2:
        return False

    # 去掉有数字的term
    if has_numbers(word):
        return False

    # 去掉全是英文的term
    if not (is_chinese(word) or is_english(word)):
        return False

    return True


def compute_keywords(title, content, topN=None, withWeight=True):
    """
    计算一个文章的TF, IDF
    :param title:
    :param content:
    :return:
    """
    # allow_pos = ('nr', 'n', 'ns', 'nt', 'nz', 'v', 'l', 'a')
    allow_pos = ('nr', 'n', 'ns', 'nt', 'nz')
    title_keywords = jieba.analyse.extract_tags(title, topK=sys.maxint, withWeight=True, allowPOS=allow_pos)
    content_keywords = jieba.analyse.extract_tags(content, topK=topN, withWeight=True, allowPOS=allow_pos)

    # 文章的权重扩大5倍
    keywords = []
    keywords.extend([(tag, 5 * weight) for (tag, weight) in title_keywords])
    keywords.extend(content_keywords)

    # 获取keywords
    if topN is not None:
        keywords = sorted(keywords, cmp=lambda x, y: cmp(x[1], y[1]), reverse=True)
        keywords = keywords[:topN]

    # 是否需要权重值
    if not withWeight:
        keywords = [tag for tag, weight in keywords]
    return keywords


def cut_words_for_cluster(articles):
    """
    对文章列表进行分词, 用于聚类
    """
    word_weight_list = []
    for title, content in articles:
        # 对文章进行分词
        # title = clear_title(title)
        # content = clear_content(content)
        word_weights = compute_keywords(title, content, withWeight=True, topN=20)

        # 停用词
        # word_weight_list = []
        # for word_weight in word_weights:
        #     word = word_weight[0]
        #     if is_valid(word) and not stopwords.has_key(word):
        #         word_weight_list.append(word_weight)

        word_weight_list.append(word_weights)
    return word_weight_list


def cut_words_with_pos(contents):
    """
    带词性分词
    """
    cut_result = []
    pos_map = {}

    for content in contents:
        word_list = []
        word_pairs = pseg.cut(content.encode("utf-8"))
        for word_pair in word_pairs:
            word = word_pair.word
            flag = word_pair.flag
            if is_valid(word) and not stopwords.has_key(word):
                word_list.append(word)
                pos_map.setdefault(word, flag)

        word_list_str = "@".join(word_list)
        cut_result.append(word_list_str)
    return cut_result, pos_map


def cut_words(contents):
    """
    对内容进行切词
    :param contents:
    :return:
    """
    cut_result = []
    for content in contents:
        # 文本分析模式
        word_list = []
        words = jieba.cut(content)
        for word in words:
            if is_valid(word) and not stopwords.has_key(word):
                word_list.append(word)
        words_list_str = "@".join(word_list)
        cut_result.append(words_list_str)
    return cut_result


def has_numbers(uchar):
    """
    判断一个字符串是否含有数字
    """
    return any(char.isdigit() for char in uchar)


def is_chinese(uchar):
    """判断一个unicode是否全是汉字"""
    if uchar >= u'\u4e00' and uchar <= u'\u9fa5':
        return True
    else:
        return False


def is_english(uchar):
    """判断一个unicode是否全是英文字母(含空格)"""
    if (uchar >= u'\u0041' and uchar <= u'\u005a') or (uchar >= u'\u0061' and uchar <= u'\u007a'):
        return True
    else:
        return False
