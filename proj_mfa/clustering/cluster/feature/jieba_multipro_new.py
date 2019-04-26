#!/usr/bin/env python
# -*- coding: utf-8 -*-

import codecs
import sys
from multiprocessing import Pool
from utils import dicutils
import jieba
import jieba.analyse
import logger
import time
import re


def get_ratio(title, content):
    title_words = filter(lambda x: len(x) > 0, map(etl, jieba.cut(title)))
    content_words = filter(lambda x: len(x) > 0, map(etl, jieba.cut(content)))
    intersection = [content_words.count(title_word) for title_word in title_words]
    word_count = sum(intersection)
    return float(word_count) / len(content)


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

    # 去掉全是英文的term
    value = re.compile(r'^[A-Za-z0-9]+$')
    result = value.match(word)
    if result is not None:
        return False
    return True


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
    sent = sent.replace('\n', '')
    sent = sent.replace('\r', '')
    sent = sent.replace('\r\n', '')

    reobj = re.compile('//@(.*?)[:\s]')
    sent = reobj.sub("", sent)

    reobj = re.compile("@(.*?)[:\s]")
    sent = reobj.sub("", sent)

    reobj = re.compile(r"\[[^\[\]]*?\]")
    sent = reobj.sub("", sent)

    sent = sent.replace("，", ",")
    sent = sent.replace("。", ".")
    sent = sent.replace("！", "!")
    sent = sent.replace("？", "?")
    reobj = re.compile("//(.*?)[:\s]")
    sent = reobj.sub("", sent)

    reobj = re.compile("((([hH][tT][tT][pP]([sS]?):\\/\\/)|(([wW][wW][wW]\\.)|([wW][aA][pP]\\.)))(([\\.\\-\\w]{3,})(:\\d*)?)([\\/?\\(\\)\\?|\\w|\\-|~|=|\\&|\\%+\\.]+))")
    sent = reobj.sub("", sent)

    regex = u'[’!"#$%&\'()*+,-./:;<=>?@，。?★、…【】《》？“”‘’！[\\]^_`{|}~]+'
    sent = re.sub(regex, '', sent)
    return sent


def etl(s):  # remove 标点和特殊字符
    regex = re.compile(ur"[^\u4e00-\u9f5aa-zA-Z0-9]")
    s = regex.sub('', s)
    return s


def cutwords_with_weight(articles, stopwords, topN):
    """
    对文章列表进行分词, 用于聚类
    """
    word_weights_list = []
    for title, content in articles:
        # 对文章进行分词
        title = clear_title(title)
        content = clear_content(content)
        word_weights = compute_keywords(title, content, topN=topN)

        # 停用词
        word_weight_list = []
        for word_weight in word_weights:
            word = word_weight[0]
            if not stopwords.has_key(word):
                word_weight_list.append(word_weight)
        word_weights_list.append(word_weight_list)
    return word_weights_list


def cutwords_with_weight_simple(articles, stopwords, topK):
    """
    对文章列表进行分词, 用于聚类
    """
    # TODO 暂时处理
    contents = [clear_sen(article[0] + article[1]) for article in articles]
    word_weights_list = []
    allow_pos = ('nr', 'n', 'ns', 'nt', 'nz')
    for content in contents:
        # 对文章进行分词
        keywords = []
        word_weights = jieba.analyse.extract_tags(content, topK=topK, withWeight=True, allowPOS=allow_pos)
        keywords.extend(word_weights)

        # 停用词
        word_weight_list = []
        for word_weight in keywords:
            word = word_weight[0]
            if not stopwords.has_key(word):
                word_weight_list.append(word_weight)
        word_weights_list.append(word_weight_list)
    return word_weights_list


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
    keywords.extend([(tag, 4 * weight) for (tag, weight) in title_keywords])
    keywords.extend(content_keywords)

    # 获取keywords
    if topN is not None:
        keywords = sorted(keywords, cmp=lambda x, y: cmp(x[1], y[1]), reverse=True)
        keywords = keywords[:topN]

    # 是否需要权重值
    if not withWeight:
        keywords = [tag for tag, weight in keywords]
    return keywords


def cutwords(articles, stopwords):
    """
    对内容进行切词
    :param contents:
    :param stopwords:
    :return:
    """
    contents = [clear_sen(article[0] + article[1]) for article in articles]
    cut_result = []
    for content in contents:
        # 文本分析模式
        words_list = []
        # words = filter(lambda x: len(x) > 0, map(etl, jieba.cut(content)))
        words = filter(lambda x: len(x) > 0, map(etl, jieba.cut(content, cut_all=True)))
        for word in words:
            if not stopwords.has_key(word):
                words_list.append(word)

        words_list = "@".join(words_list)
        cut_result.append(words_list)
    return cut_result


def run(articles, user_dict_path, dicts, stopwords, topN):
    # 从文本中中添加, 自定义词典
    jieba.load_userdict(user_dict_path)

    # 从mysql中添加, 自定义词典
    for dic in dicts:
        jieba.add_word(dic[1].encode('utf-8'))

    # 分词
    cut_result = cutwords(articles, stopwords)
    return cut_result


def cut_tasks(articles, num_tasks):
    """
    切分任务
    :param articles:
    :param num_tasks:
    :return:
    """
    start_time = time.time()
    logger.logger.debug("starting cut_tasks, {articles, %d, num_tasks, %d}." % (len(articles), num_tasks))
    task_list = []
    num_articles = len(articles)
    num_per_task = num_articles / num_tasks
    for x in range(num_tasks):
        start_split = x * num_per_task
        end_split = (x + 1) * num_per_task

        if x == num_tasks - 1:
            end_split = num_articles
        task_list.append(articles[start_split:end_split])
    logger.logger.debug("ending cut_tasks, {cost_time: %ds}" % (time.time() - start_time))
    return task_list


def pre_process(len_articles):
    """
    多进程, 预处理
    :return:
    """
    # 从文本中中添加, 自定义词典
    user_dict_path = "dict/userdict.txt"

    # 从mysql中添加, 自定义词典
    dicts = dicutils.getdics_mysql()

    # 停用词语料
    stopwords = {}
    stopwords_path = "dict/stopWords.txt"
    stw = codecs.open(stopwords_path, encoding="utf-8")
    for ws in stw.readlines():
        ws = ws.replace("\n", "")
        ws = ws.replace("\r", "")
        ws = ws.strip()
        stopwords[ws] = 1
    stw.close()

    # 计算TopK
    top_n = 50

    return user_dict_path, dicts, stopwords, top_n


def multi_cut_words_for_cluster(articles, num_processes):
    """
    多线程, 进行切词
    :param articles:
    :return:
    """
    # 获得任务列表
    task_list = cut_tasks(articles, num_processes)

    # 多线程处理
    attach = pre_process(len(articles))
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
    logger.logger.debug("starting multi_process, {processes: %d, task_list: %d }." % (processes, len(task_list)))
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
    logger.logger.debug("ending multi_process, {task_time: %ds}" % (time.time() - start_time))
    return cut_result


if __name__ == '__main__':
    articles = [('南通加大澳門聯繫力度貢獻國', '【本報訊】澳門南通商會第二屆理監事暨澳門南通聯誼會第一屆理監事就職典禮昨晚舉行。會長施春雷表示，當前國家經濟社會發展進入新時代，南通正努力建設上海北大門，做好「跨江融合、接軌上海」的大文章，而澳門正積極融入國家發展大局，建設蘇澳合作園區，促進經濟適度多元發展，澳門與南通的經貿往來、人員往來將會更加緊密。他期望商會和聯誼會能夠建設成聯繫政府與企業、企業與企業、企業與鄉親的橋樑和紐帶，為澳門和南通兩地的經濟發展做出更大貢獻。'),
                ('你所知道的背影（一）　紹　鈞', '新近閱讀了一篇有關艾未未的文章，該文陳述他將赴柏林藝術大學擔任客席教授。另文中也提及，他對於教授藝術的一些觀念，像認為藝術「已經不再只是關乎形式與形狀，而是更關乎於哲學和社會政治觀點。」'),
                ('感謝她盛裝蒞臨我的青春　陳　穎', '我小時候有一個夢想，就是可以穿上灰姑娘的水晶鞋，坐上南瓜車，搖曳着華麗的裙擺來到舞會，成為當刻最耀眼的那個公主。眾所周知，灰姑娘的美麗背後，有一位惡毒的繼母和兩個心地不好的姐姐，她們處處刁難她，每天讓她做粗重的工作。也正因為這個故事，繼母這狠角色已植根在我的腦海中。'),
                ('市民微信亂講嘢或觸內地法律', '【本報訊】政府昨日舉行最後一場《網絡安全法》公開諮詢，郵電局資訊科技發展處處長李廣亮稱，微信、Whatsapp等不屬本地區的軟件，將來法律未必可以規管；司警局電腦法證處處長陳思晶稱，每個人要為自己的言論負責，倘如在微信「亂講嘢」可能觸犯內地網安法。'),
                ('')]
    num_processes = 2
    print multi_cut_words_for_cluster(articles, num_processes)