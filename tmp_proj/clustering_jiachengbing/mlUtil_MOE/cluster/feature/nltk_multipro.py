#!/usr/bin/env python
# -*- coding: utf-8 -*-

import string
import time
from multiprocessing import Pool

import nltk
from nltk import corpus
from nltk.stem.porter import *
from nltk.stem.wordnet import WordNetLemmatizer

from dao.mysql.system_word_aggregation import SystemWordAggregation
from utils import logger


def cut_words(contents, dicts):
    """
    对英文文本列表, 进行切词
    :param text:
    :param is_stem:
    :return:
    """
    tokens_list = []
    for content in contents:
        try:
            tokens = cut_word(content, dicts)
        except Exception as e:
            tokens = []

        tokens_list.append('@'.join(tokens))
    return tokens_list


def cut_word(text, dicts):
    """
    对单个英文, 进行切词
    :param text:
    :param is_stem:
    :return:
    """
    tokens = get_tokens(text, dicts)

    posed_tokens = filter_tokens(tokens)

    lemmatized_tokens = lemmatize_tokens(posed_tokens)  # 词形

    return lemmatized_tokens


def has_numbers(uchar):
    """
    判断一个字符串是否含有数字
    """
    return any(char.isdigit() for char in uchar)


def is_valid(word):
    """
    :param s:
    :return:
    """
    # 去掉无意义的term
    if len(word) < 2:
        return False

    # 去掉有数字的term
    # if has_numbers(word):
    #     return False

    return True


def clear_title(title):
    """
   过滤内容的中的特殊字符
   :param title:
   :return:
   """
    title = title.replace('\n', ' ')
    title = title.replace('\r', ' ')
    title = title.replace('\r\n', ' ')

    title = title.lower().strip()

    return title


def clear_content(content):
    """
    获取文章的钱3段内容
    :param content:
    :return:
    """
    # paragraphs = content.split('\n')
    # return "\n".join([clear_sen(paragraph) for paragraph in paragraphs[:3]])
    content = content.lower().strip()

    return content


def etl(s):  # remove 标点和特殊字符
    regex = re.compile(ur"[^a-zA-Z0-9]")
    s = regex.sub('', s)
    return s


def run(articles, dicts):
    # 分词
    # TODO 暂时处理
    contents = [clear_title(article[0] + article[1]) for article in articles]
    cut_result = cut_words(contents, dicts)

    return cut_result


def cut_tasks(articles, num_tasks):
    """
    切分任务
    :param articles:
    :param num_tasks:
    :return:
    """
    start_time = time.time()
    logger.logger.info("start cut_tasks ....")
    task_list = []
    num_articles = len(articles)
    num_per_task = num_articles / num_tasks
    for x in range(num_tasks):
        start_split = x * num_per_task
        end_split = (x + 1) * num_per_task

        if x == num_tasks - 1:
            end_split = num_articles
        task_list.append(articles[start_split:end_split])
    logger.logger.info("end cut_tasks ...., %ds" % (time.time() - start_time))
    return task_list


def pre_process():
    """
    多进程, 预处理
    :return:
    """
    # 从mysql中添加, 自定义词典
    custom_dic = SystemWordAggregation()
    dicts = custom_dic.get_dicts_en()

    return dicts,


def multi_cut_words(articles, num_processes):
    """
    多线程, 进行切词
    :param articles:
    :param num_processes:
    :return:
    """
    # 获得任务列表
    task_list = cut_tasks(articles, num_processes)

    # 多线程处理
    attach = pre_process()
    cut_result = multi_process(num_processes, task_list, run, attach)
    return cut_result


def multi_process(processes, task_list, run, attach):
    """
    多线程, 处理任务
    :param processes: 任务个数
    :param task_list: 任务列表
    :param run:
    :param attach:
    :return:
    """
    start_time = time.time()
    logger.logger.info("start multi_process ....")
    pool = Pool(processes=processes)

    results = []
    for task in task_list:
        args = (task,) + attach
        ret = pool.apply_async(run, args=args)
        results.append(ret)

    pool.close()
    pool.join()

    cut_result = []
    for x in results:
        cut_result.extend(x.get())
    logger.logger.info("end multi_process ...., %ds" % (time.time() - start_time))
    return cut_result


def get_tokens(text, dicts):
    """
    tokenize, 将自定义词, 转换为 'word@word@word' 格式
    :param text:
    :return:
    """
    # 转化英文自定义词典
    for dict in dicts:
        word = dict[1]
        word = word.lower().strip()
        text = text.replace(word, '^B'.join(word.split(" ")))

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
    # 过滤特殊字符
    tokens = filter(lambda x: len(x) > 0, map(etl, tokens))

    # 过滤标题, 停用词
    filtered = []
    for item in tokens:
        if item not in stopwords and item not in punctuations:
            filtered.append(item)

    # 只取名词, 动词, 形容词
    ret = []
    token_poses = nltk.pos_tag(filtered)
    for t in token_poses:
        word = t[0]
        pos_word = t[1]

        if pos_word.startswith('N') \
                or pos_word.startswith('V'):
            word = word.lower()
            ret.append((word, pos_word))

    return ret


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


def lemmatize_tokens(posed_tokens, lemmatizer=WordNetLemmatizer()):
    """
    词形还原
    :param tokens:
    :param lemmatizer:
    :return:
    """
    lemmatized = []
    for word, pos in posed_tokens:
        item = word
        if pos.startswith('NN'):  # 名词
            lemmatized.append(lemmatizer.lemmatize(item, 'n').lower().encode('utf-8'))
        elif pos.startswith('VB'):  # 动词
            lemmatized.append(lemmatizer.lemmatize(item, 'v').lower().encode('utf-8'))
        elif pos.startswith('JJ'):  # 形容词
            lemmatized.append(lemmatizer.lemmatize(item, 'a').lower().encode('utf-8'))
        else:
            lemmatized.append(item.lower().encode('utf-8'))

    return lemmatized


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
    articles = [('Malaysia says US apples are safe for consumption after social media scare',
                 'KUALA LUMPUR - Malaysian authorities clarified on Wednesday (Jan 24) that two brands of American apples banned for listeriosis bacteria contamination in 2015 are now safe for consumption, batting away reports circulating in social media and mobile messaging apps.'),
                ('Senate Faults Cost Variations of $16bn Egina Oil Project, Begins Probe',
                 'The Senate yesterday said the local content elements and cost variations of the $16 billion Egina offshore oil project is faulty, full of irregularities and ordered immediate probe to audit it.'),
                ('Man arrested for threatening to attack CNN headquarters over ‘fake news’',
                 'US authorities have arrested a man who allegedly made several calls to CNN s Atlanta headquarters, threatening to shoot and kill employees over what he said was “fake news”, according to a federal affidavit.'),
                ('Beijing‘s struggle against pollution will be tough, take time: Mayor',
                 'BEIJING (REUTERS) - Beijing s battle against air pollution will take time and be very tough to win despite recent improvements, the acting mayor of China s capital said on Wednesday (Jan 24).'),
                ('Scientists discover a piece of America in Australia',
                 'Researchers have discovered rocks in Queensland that bear striking similarities to those found in North America, suggesting that a chunk of Australia was actually part of America 1.7 billion years ago.')]
    num_processes = 2
    print multi_cut_words(articles, num_processes)
    # print clear_sen("new videos show clearest account of alton sterling\\'s killing")
