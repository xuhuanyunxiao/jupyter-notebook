#!/usr/bin/env python
# -*- coding: utf-8 -*-

import string
import time
from multiprocessing import Pool

import nltk
from gensim.summarization import keywords
from nltk import corpus
from nltk.stem.porter import *
from nltk.stem.wordnet import WordNetLemmatizer

from dao.mysql.system_word_aggregation import SystemWordAggregation
from utils.logger import logger


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

        # 还原自定义词典
        tokens = [t.replace('^B', ' ') for t in tokens]

        tokens_list.append('@'.join(tokens))
    return tokens_list


def cut_word(text, dicts):
    """
    对单个英文文本, 进行切词
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


def etl(s):  # remove 标点和特殊字符
    regex = re.compile(ur"[^a-zA-Z0-9\^]")
    s = regex.sub('', s)
    return s


def clear_sen(sent):
    """
    过滤内容的中的特殊字符
    :param sent:
    :return:
    """
    sent = sent.replace('\n', '')
    sent = sent.replace('\r', '')
    sent = sent.replace('\r\n', '')

    sent = sent.lower().strip()

    return sent


def run(articles, dicts):
    logger.debug('articles length : %d' % (len(articles)))
    # title分词
    titles = [clear_title(article[0]) for article in articles]
    title_cuts = cut_words(titles, dicts)

    # content摘要
    contents = [article[1] for article in articles]
    content_keywords = [get_keywords(content) for content in contents]
    # content_keywords = [content_keyword * 5 for content_keyword in content_keywords]  # 正文的权重扩大2倍数, 同标题区分

    # 合并
    cut_results = zip(title_cuts, content_keywords)

    results = []
    for cut_result in cut_results:
        title_str = cut_result[0].strip()
        content_str = '@'.join(cut_result[1]).strip()

        if title_str == '' and content_str == '':
            results.append('')
        elif title_str == '' and content_str != '':
            results.append(content_str)
        elif title_str != '' and content_str == '':
            results.append(title_str)
        else:
            results.append('@'.join([title_str, content_str]))

    return results


def get_keywords(content):
    keys = []
    if content.strip() == '':
        return keys

    content = content.lower()
    try:
        keys = keywords(content, words=10, split='\n',
                        pos_filter=('NN', 'NNS', 'NNP', 'NNPS', 'VB', 'VBD', 'VBG', 'VBN'), lemmatize=True)
    except ZeroDivisionError:
        keys = []
    except IndexError as e:
        keys = keywords(content, ratio=1, split='\n',
                        pos_filter=('NN', 'NNS', 'NNP', 'NNPS', 'VB', 'VBD', 'VBG', 'VBN'), lemmatize=True)
    return keys


def cut_tasks(articles, num_tasks):
    """
    切分任务
    :param articles:
    :param num_tasks:
    :return:
    """
    start_time = time.time()
    logger.info("start cut_tasks ....")
    task_list = []
    num_articles = len(articles)
    num_per_task = num_articles / num_tasks
    for x in range(num_tasks):
        start_split = x * num_per_task
        end_split = (x + 1) * num_per_task

        if x == num_tasks - 1:
            end_split = num_articles
        task_list.append(articles[start_split:end_split])
    logger.info("end cut_tasks ...., %ds" % (time.time() - start_time))
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
    logger.info("start multi_process ....")
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
    logger.info("end multi_process ...., %ds" % (time.time() - start_time))
    return cut_result


def get_tokens(text, dicts):
    """
    tokenize, 将自定义词, 转换为 'word@word@word' 格式
    :param text:
    :return:
    """
    # 小写
    text = text.lower()

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
    tokens = filter(lambda x: len(x) > 2, map(etl, tokens))

    # 过滤标点符号, 停用词
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
                or pos_word.startswith('V') \
                or pos_word.startswith('J'):
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
            item = lemmatizer.lemmatize(item, 'n')
        if pos.startswith('VB'):  # 动词
            item = lemmatizer.lemmatize(item, 'v')
        if pos.startswith('JJ'):  # 形容词
            item = lemmatizer.lemmatize(item, 'a')
        lemmatized.append(item.encode('utf-8'))

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
    # articles = [('Malaysia says US apples are safe for consumption after social media scare',
    #              'KUALA LUMPUR - Malaysian authorities clarified on Wednesday (Jan 24) that two brands of American apples banned for listeriosis bacteria contamination in 2015 are now safe for consumption, batting away reports circulating in social media and mobile messaging apps.'),
    #             ('Senate Faults Cost Variations of $16bn Egina Oil Project, Begins Probe',
    #              'The Senate yesterday said the local content elements and cost variations of the $16 billion Egina offshore oil project is faulty, full of irregularities and ordered immediate probe to audit it.'),
    #             ('Man arrested for threatening to attack CNN headquarters over ‘fake news’',
    #              'US authorities have arrested a man who allegedly made several calls to CNN s Atlanta headquarters, threatening to shoot and kill employees over what he said was “fake news”, according to a federal affidavit.'),
    #             ('Beijing‘s struggle against pollution will be tough, take time: Mayor',
    #              'BEIJING (REUTERS) - Beijing s battle against air pollution will take time and be very tough to win despite recent improvements, the acting mayor of China s capital said on Wednesday (Jan 24).'),
    #             ('Scientists discover a piece of America in Australia',
    #              'Researchers have discovered rocks in Queensland that bear striking similarities to those found in North America, suggesting that a chunk of Australia was actually part of America 1.7 billion years ago.')]
    # num_processes = 2
    # print multi_cut_words(articles, num_processes)

    # print clear_sen("new videos show clearest account of alton sterling\\'s killing")

    print get_keywords("""US President Donald Trump admits Trump Jr sought information on Clinton from Russians. US President Donald Trump acknowledged on Sunday that his son met with Russians in 2016 at Trump Tower to get information on his election opponent Hillary Clinton, saying it was “totally legal” and “done all the time in politics.” The Republican president had previously said the meeting was about the adoption of Russian children by Americans. Trump s morning Twitter post was his most direct statement on the purpose of the meeting, though his son and others have said it was to gather damaging information on the Democratic candidate. ALSO READ: Trump invites Putin to visit US In a post on Twitter here, Trump also denied reports in the Washington Post and CNN that he was concerned his eldest son, Donald Trump Jr., could be in legal trouble because of the meeting with the Russians, including a lawyer with Kremlin ties. He repeated that he had not known about the meeting in advance. “Fake News reporting, a complete fabrication, that I am concerned about the meeting my wonderful son, Donald, had in Trump Tower. This was a meeting to get information on an opponent, totally legal and done all the time in politics - and it went nowhere. I did not know about it!” Trump said. Political campaigns routinely pursue opposition research on their opponents, but not with foreign representatives from a country viewed as an adversary. Russian officials were under U.S. sanctions at the time. Know if news is factual and true. Text \'NEWS\' to 22840 and always receive verified news updates. Special Counsel Robert Mueller is examining whether Trump campaign members coordinated with Russia to sway the White House race in his favor. Russian President Vladimir Putin has denied his government interfered. One part of the inquiry has focused on a June 9, 2016, meeting at Trump Tower in New York between Donald Jr., other campaign aides and a group of Russians. Email released by Donald Jr. himself showed he had been keen on the meeting because his father s campaign was being offered potentially damaging information on Clinton. Donald Jr. said later he realized the meeting was primarily aimed at lobbying against the 2012 Magnitsky sanctions law, which led to Moscow denying Americans the right to adopt Russian orphans. ALSO READ: Kim visits China after Trump summit President Trump has repeatedly denied that his campaign worked with Moscow, saying “No Collusion!” Last week, however, he adopted his lawyers tactics and insisted “collusion is not a crime.” While collusion is not a technical legal charge, Mueller could bring conspiracy charges if he finds that any campaign member worked with Russia to break U.S. law. Working with a foreign national with the intent of influencing a U.S. election could violate multiple laws, according to legal experts. CNN reported last month that Michael Cohen, the president s longtime personal lawyer, was willing to tell Mueller that Trump did know about the Trump Tower meeting in advance. Trump s lawyers and the White House have given conflicting accounts about whether Trump was involved in crafting Donald Jr. s response to a New York Times article last summer revealing the Trump Tower meeting with the adoptions rationale. Trump s lawyers acknowledged in a letter to Mueller s team in January 2018 that Trump dictated the response, according to the Times. Trump has stepped up his public attacks on the Mueller probe since the first trial to arise from it began last week in Alexandria, Virginia, involving former Trump campaign chairman Paul Manafort. The federal tax and bank fraud charges Manafort faces are not related to the Trump campaign but Manafort s close relations with Russians and a Kremlin-backed Ukrainian politician are under scrutiny in the trial. Trump s attacks on the special counsel s investigation have been rebuffed by Republican leaders in Congress who have expressed support for Mueller. “The president should be straightforward with the American people about the threat to our election process that Russia, Putin in particular, is engaged in is ongoing,” Representative Ed Royce, chairman of the House Foreign Affairs Committee, said on CNN s “State of the Union” on Sunday. One of the president s personal lawyers said on Sunday that if Trump is subpoenaed by the special counsel, his lawyers will attempt to quash it in court. Any legal battle over whether the president can be compelled to testify could go all the way to the U.S. Supreme Court, the lawyer, Jay Sekulow, said on ABC s “This Week.” US intelligence agencies concluded last year that Russia interfered in the 2016 U.S. election with a campaign of hacking into Democratic Party computer networks and spreading disinformation on social media. American intelligence officials say Russia is targeting the November congressional elections, which will determine whether or not Republicans keep control of both chambers of the U.S. Congress. Would you like to get published on Standard Media websites? You can now email us breaking news, story ideas, human interest articles or interesting videos on:""")

    # print run([("""DNC spokeswoman: 'Insane' for Republicans to be running on Trump agenda""", '')], dicts=[])

    print cut_word("""Trump says his son sought information on Clinton from Russians in 2016""".lower(), dicts=[])
