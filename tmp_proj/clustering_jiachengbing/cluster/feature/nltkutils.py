#!/usr/bin/python
# -*- coding: UTF-8 -*-

import nltk
import string
from nltk.stem.porter import *
from nltk import corpus
from dao.mysql.system_word_aggregation import SystemWordAggregation


# 从mysql中添加, 自定义词典
custom_dic = SystemWordAggregation()
dicts = custom_dic.getdics_eng()


def cut_words_pos(texts, is_stem=False):
    """
    分句, 切词, 过滤, 自定义词处理
    :param texts:
    :return:
    """
    cut_result = []
    pos_map = {}
    for text in texts:
        tokens_pos = nltk.pos_tag(cut_word(text, is_stem))
        chuck = parse_chuck(tokens_pos)
        cut_result.append('@'.join([token[0] for token in chuck]))
        for token in chuck:
            pos_map.setdefault(token[0], token[1])
    return cut_result, pos_map


def cut_words(texts, is_stem=False):
    """
    对英文文本列表, 进行切词
    :param text:
    :param is_stem:
    :return:
    """
    tokens_list = []
    for text in texts:
        tokens_pos = nltk.pos_tag(cut_word(text, is_stem))
        chuck = parse_chuck(tokens_pos)
        tokens_list.append('@'.join([token[0] for token in chuck]))
    return tokens_list


def cut_word(text, is_stem=False):
    """
    对单个英文, 进行切词
    :param text:
    :param is_stem:
    :return:
    """
    tokens = get_tokens(text)
    filtered = filter_tokens(tokens)
    if is_stem:
        filtered = stem_tokens(filtered)
    return filtered


def has_numbers(uchar):
    """
    判断一个字符串是否含有数字
    """
    return any(char.isdigit() for char in uchar)


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

    return True


def get_tokens(text):
    """
    tokenize, 将自定义词, 转换为 'word@word@word' 格式
    :param text:
    :return:
    """
    # 转化英文自定义词典
    for dic in dicts:
        text = text.replace(dic[1], '^B'.join(dic[1].split(" ")))
    
    # NLTK 分词
    tokens = nltk.word_tokenize(text)
    return tokens


def filter_tokens(tokens, stopwords=corpus.stopwords.words('english'), punctuations=string.punctuation):
    """
    过滤标点符号, 以及停用词
    :param tokens:
    :param stopwords:
    :param punctuations:
    :return:
    """
    filtered = []
    for item in tokens:
        if item not in stopwords and item not in punctuations and is_valid(item):
            filtered.append(item)
    return filtered


def stem_tokens(tokens, stemmer=PorterStemmer()):
    """
    提取词干
    :param tokens:
    :param stemmer:
    :return:
    """
    stemmed = []
    for item in tokens:
        stemmed.append(stemmer.stem(item).encode('utf-8'))
    return stemmed


def dec_dict(dict):
    """
    还原 'word@word@word' 格式的词典
    :param dict: {tokens: value, tokens: value, ...}
    :return:
    """
    new_dict = {}
    for key, value in dict.items():
        new_key = ' '.join(key.split('^B'))
        new_dict.setdefault(new_key, value)
    return new_dict


def dec_cluster_objs(cluster_objs):
    """
    还原 'word@word@word' 格式的词典
    :param cluster_objs: [cluster_obj, cluster_obj, ...]
    :return:
    """
    new_cluster_obj = []
    for cluster_obj in cluster_objs:
        new_clusterTopic = ' '.join(cluster_obj.clusterTopic.split('^B'))
        cluster_obj.clusterTopic = new_clusterTopic
        new_cluster_obj.append(cluster_obj)
    return new_cluster_obj


def parse_chuck(tokens):
    # chucked处理
    gram = """NP:
    {<NN>+}
    {<NNP>+}
    """
    cp = nltk.RegexpParser(gram)
    chucked = cp.parse(tokens)

    # 获得分词后的结果
    result_list = get_nodes(chucked)
    return result_list


def get_nodes(parent):
    """
    对tree进行解析, 获得名词, 介词等短语
    :param parent:
    :return:
    """
    list = []
    for node in parent:
        if type(node) is nltk.Tree and node.label() == 'NP':
            in_list = [n[0] for n in node.leaves()]
            word_phrase = ' '.join(in_list)
            list.append((word_phrase, node.label()))
        else:
            list.append((node[0], node[1]))

    # 还原自定义, 词典
    list = [(t[0].replace('^B', ' '), t[1]) for t in list]
    return list


if __name__ == '__main__':
    contents = [
        'Anaconda Cloud is a package management service that makes it easy to find, access, store and share public and private notebooks, environments, and conda and PyPI packages. Cloud also makes it easy to stay current with updates made to the packages and environments you are using.',
        'Middle-aged people in England face a health crisis because of unhealthy lifestyles, experts have warned. Desk jobs, fast food and the daily grind are taking their toll, says Public Health England. Eight in every 10 people aged 40 to 60 in England are overweight, drink too much or get too little exercise, the government body warns. PHE wants people to turn over a new leaf in 2017, and make a pledge to get fit.  Health officials say the "sandwich generation" of people caring for children and ageing parents do not take enough time to look after themselves. We are living longer, but are in poorer health because we store up problems as we age.  The campaigns clinical adviser, Prof Muir Gray, said it was about trying to make people have a different attitude to an "environmental problem". "Modern life is dramatically different to even 30 years ago," Prof Gray told Radio 4s Today programme, "people now drive to work and sit at work." "By taking action in mid-life... you can reduce your risk not only of type 2 diabetes, which is a preventable condition, but you can also reduce your risk of dementia and disability and, being a burden to your family," he added. Many people no longer recognise what a healthy body weight looks like, say the officials  - and obesity, which greatly increases the risk of diabetes, is increasingly considered normal.  The PHE website and app has a quiz that gives users a health score based on their lifestyle habits by asking questions such as, "Which snacks do you eat in a normal day?" and "How much exercise do you get every day?". The questions are simple, but the results are revealing, says Prof Kevin Fenton, director of Health and Wellbeing at PHE.  "The How Are You Quiz will help anyone who wants to take a few minutes to take stock and find out quickly where they can take a little action to make a big difference to their health." More than a million people have taken the quiz so far. Lee Parker is 41 and from Bolton. He did the quiz in March before starting a diet in August.  He says it was his son who provided a much-needed wake-up call. Lees son, who is now eight, told him he loved him "even though you are fat".  This was the final nudge that Lee says he needed.  Weighing in at more than 22 stone, Lee started to diet and exercise and lost just over five stone in 16 weeks.  His partner has joined in and has lost two and a half stone. In April 2017, Lee will be taking part in the Manchester marathon. He says: "You can become very complacent when you are in your forties. You kind of think youve done everything and so you can relax and eat pizzas and Chinese in the week.  "Ive still got another stone to go to my target weight. Its been very, very difficult. Im missing all the cakes and the crisps and the biscuits.... I still have them, I still enjoy them, but I know when to say no and I know how much Ive had." ']
    print cut_words(contents)