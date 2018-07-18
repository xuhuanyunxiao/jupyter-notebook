#!/usr/bin/env python
# -*- coding: utf-8 -*-
import re
import jieba
import jieba.posseg as pseg
import dict_dbutils

# 情感极性词
f = open('corpus/a_level_SP0320.txt', encoding='UTF-8')
sp_dict = {}
while True:
    info = f.readline()
    if not info:
        break
    info = info.split('\t')
    word = info[0]
    value = float(info[1].strip())
    sp_dict[word] = value

# mysql 加载实体词典
dictionarys = dict_dbutils.get_dicts()
for dictionary in dictionarys:
    jieba.add_word(dictionary, 100, "cpn")

# 加载其他自定义词典
jieba.load_userdict('corpus/userdict.txt')


def wus_next(s, pos):
    """
    功能：	计算下一步状态，运算符
    输入：	当前状态(string)，词性(pos)
    输出：	新的状态(string)，运算符(string)
    :param s:
    :param pos:
    :return:
    """

    if s == 's0':
        dict_ = {'n': ['s1', '+'], 'v': ['s2', '+'], 'a': ['s3', '*'],
                 'qt': ['s1', '+'], 'adv': ['s3', '*'], 'neg': ['s4', '*'],
                 'zz': ['s0', '0'], 'dj': ['s0', '2*'], 'bd': ['sn', 'stop']}
        return dict_[pos]
    if s == 's1':
        if pos == 'bd':
            return ['sn', 'stop']
        else:
            return ['s0', '+']
    if s == 's2':
        dict_ = {'n': ['s0', '+'], 'a': ['s0', '+'], 'adv': ['s5', '+'], 'bd': ['sn', 'stop']}
        try:
            return dict_[pos]
        except:
            return ['s2', 'pass']
    if s == 's3':
        dict_ = {'n': ['s0', '+'], 'v': ['s2', '+'], 'a': ['s3', '*'], 'adv': ['s3', '*'], 'bd': ['sn', 'stop']}
        try:
            return dict_[pos]
        except:
            return ['s3', 'pass']
    if s == 's4':
        dict_ = {'n': ['s0', '+'], 'v': ['s2', '+'], 'qt': ['s0', '+'], 'neg': ['s4', '*'], 'bd': ['sn', 'stop']}
        try:
            return dict_[pos]
        except:
            return ['s4', 'pass']
    if s == 's5':
        dict_ = {'a': ['s0', '+'], 'bd': ['sn', 'stop']}
        try:
            return dict_[pos]
        except:
            return ['s5', 'pass']
    return


def evaluator(pre_result, symbol, pos, value):
    """
    功能：	计算当前部分句子的情感极值
    输入：	当前状态(string)，当前极值(float)，当前词的极值(float)
    输出：	新的极值(float)
    :param pre_result:
    :param symbol:
    :param value:
    :return:
    """
    if pos == 'bd':
        return pre_result
    if symbol == '+':
        return pre_result + value
    if symbol == '*':
        return pre_result * value
    if symbol == '2*':
        return 2 * pre_result * value
    if symbol == '0':
        return 0
    if symbol == 'pass':
        return pre_result
    return


def translator(info):
    """
    注释：	由于jieba分词的词性标注样式较多，故将其词性标注归纳为转折词（zz），	副词（adv），
                否定词（neg），名词（n），动词（v），形容词（a），标点（db）和其他（qt）。
    功能：	翻译词性标注
    输入：	jieba词信息列表(list)
    输出：	词信息列表

    :param info:
    :return:
    """
    if 'zz' in info[1] or 'adv' in info[1] or 'neg' in info[1] or 'bd' in info[1]:
        return info
    else:
        if 'n' in info[1]:
            return [info[0], 'n', info[2]]
        else:
            if 'v' in info[1]:
                return [info[0], 'v', info[2]]
            elif 'a' in info[1]:
                return [info[0], 'a', info[2]]
            elif info[0] == "。":
                return [info[0], 'bd', info[2]]
            else:
                return [info[0], 'qt', info[2]]
    return


def start_evaluate(sentences):
    """
    功能：	程序入口，运算，书写结果
    输入：	数据集路径（string），情感字典路径（string）
    输出：	无
    :param sentences:
    :return:
    """
    org_list = []
    for sentence in sentences:
        if sentence.strip() == "":
            continue

        # 获得词列表
        words_chain = []
        cpns = []
        sentence = sentence.strip() + '。'
        words = filter(lambda word_pos: len(word_pos.word) > 0, map(clear_word, pseg.cut(sentence)))

        for word_pos in words:
            word = word_pos.word
            pos = word_pos.flag
            if pos == 'cpn':  # 公司主体
                try:
                    cpns.append(dictionarys[word])  # (id, classify_id, node_id, org_name)
                except:
                    continue
            try:
                if pos != 'ns' and pos != 't':  # 排除时间词, 以及地名
                    words_chain.append([word, pos, sp_dict[word]])
            except:
                continue

        sentiment_words = []
        # 负面极性词
        neg_words = []
        for element in words_chain:
            if element[2] < -1.0:
                neg_words.append(element[0])
        sentiment_words.extend(neg_words)

        # 负面极性词
        pos_words = []
        for element in words_chain:
            if element[2] > 1.0:
                pos_words.append(element[0])
        sentiment_words.extend(pos_words)

        # 计算正负面
        pre_result = 0
        symbol = '+'
        status = 's0'
        for word in words_chain:
            word = translator(word)  # 词性转化

            pre_result = evaluator(pre_result, symbol, word[1], word[2])  # 计算情感极值

            status, symbol = wus_next(status, word[1])  # 获得下一个状态, 以及操作符

            if symbol == 'stop':
                break

        if pre_result < 0:
            pre_result = -1
        else:
            pre_result = 0

        if len(cpns) > 0:
            for cpn in cpns:
                if cpn[1] == 9 or cpn[1] == 13 or cpn[3] == '保监局' \
                        or cpn[3] == '保监会' or cpn[3] == '银保监会':
                    pre_result = 0
                dict_ = {"id": cpn[0], "classify_id": cpn[1], "node_id": cpn[2], "name": cpn[3],
                         "sentiment_word": ','.join(sentiment_words), "tendency": pre_result}
                org_list.append(dict_)
    return org_list


def clear_article(content):
    content = content.replace("\n", "")
    content = content.replace('\r', '')
    content = content.replace('\r\n', '')
    return content


def clear_word(word_pos):  # remove 标点和特殊字符
    regex = re.compile(r"[^\u4e00-\u9f5aa-zA-Z0-9。]")
    word = regex.sub('', word_pos.word)
    word_pos.word = word
    return word_pos


def evaluate_article(content):
    content = clear_article(content)
    cut_regex = r'。'
    sentences = re.split(cut_regex, content)

    org_list = start_evaluate(sentences)

    # 句子中, 只要出现负面, 整个篇章为负
    tendency = 0
    for org in org_list:
        if org['tendency'] == -1:
            tendency = -1

    return tendency, org_list


def process_articles(contents):
    ret = []
    for content in contents:
        org_list = evaluate_article(content)
        ret.append(org_list)
    return ret


if __name__ == '__main__':
    contents = ["""
    确定保监会中国银行不再关注中国人寿此人吗摘,要不按规定投保机动车第三者责任险
    """]
    print(process_articles(contents))
