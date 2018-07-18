# encoding = utf-8
import sys
import jieba.analyse
import re  # 正则库

# 导入分词库
jieba.load_userdict("corpus/user_dict.txt")  # 需修改为centos 路径

# 加入停止词典
stopwords_path = "corpus/stopwordict.txt"
stopword_dict = open(stopwords_path, encoding="utf-8").readlines()
stopwordict = []  # 去掉空格的停止词库
for i in stopword_dict:
    stopwordict.append(i.strip())

# 加入主体词库
org_dict_path = "corpus/org.txt"
orgdict = open(org_dict_path, encoding="utf-8").readlines()
org_dict = []  # 去掉空格的主题词库
for i in orgdict:
    org_dict.append(i.strip())

# 加入负面词库
negative_dict_path = "corpus/negative_words.txt"
negativedict = open(negative_dict_path, encoding="utf-8").readlines()

# 消歧 词库 简单 
innegativedict = ['纯属', '系', '服务', '创新', '规范', '限制', '受限', '退出', '强制退出', '开启', '上新', '完成', '提速', '首例', '新产品', '创新产品']


# 创建分析对象 文本矩阵化 处理 以及文本 词频-词距-词密 的计算
class text_Matrix():
    def __init__(self, arg):
        self.arg = arg

    # 切段落 段落内去停止词
    def cut4paragraph(paragraph_data):
        # print("文本", paragraph_data)
        paragraph = []
        if paragraph_data != None:
            spilt_pattern = "([\u4e00-\u9fa5]*\\\\n)"
            spilt_paragraph = re.compile(spilt_pattern)  # 构造匹配切分模式
            thef = re.split(spilt_paragraph, paragraph_data)  #
            for i in thef:
                i = i.strip()
                i = i.replace('\\', '').replace('r', '')
                if len(i) == 0:
                    continue
                else:
                    if len(i) == 1:
                        continue
                    else:
                        # paragraph.append(list(i)) # 每段返回时以list列表返回的
                        paragraph.append(i)  # 每段返回时以str字符串类型返回
        # 对文本段落 分句
        # for item in paragraph:

        yield tuple(paragraph)

    # 切句子  paragraph是generator
    def cut4sentences(paragraph):
        sentences = []  #
        spilt_pattern_sentence = "。|？|！|：|；"
        split_sentence = re.compile(spilt_pattern_sentence)  #
        if paragraph != None:
            for pre_paragraph in paragraph:
                print("pre_paragraph : ", type(pre_paragraph), pre_paragraph)
                for i_s in pre_paragraph:
                    i_sentences = re.split(split_sentence, i_s)  # .strip()

                    for i in i_sentences:
                        i = i.strip()
                        if len(i) == 0:
                            continue
                        else:
                            sentences.append(i)
        yield tuple(sentences)
