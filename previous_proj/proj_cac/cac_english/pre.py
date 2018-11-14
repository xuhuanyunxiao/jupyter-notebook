#!/usr/bin/env python
# -*- coding: utf-8 -*-


import nltk
from nltk.stem import WordNetLemmatizer
from string import digits
import re

stopwords = {}
stw = open("corpus/stopwords.txt", encoding='UTF-8')
for ws in stw:
    ws = ws.replace("\n", "")
    ws = ws.replace("\r", "")
    stopwords[ws] = 1
stw.close()

def handle_contents(l_contents):
    lines = []
    for line in l_contents:
        lines.append(handle_content(line))
    return lines    

def handle_content(content):
    content = str(content)
    raw = content.strip()
    line = ""
    if raw != "":       
        # 1 清理字符串
        content = clean_sent(content)

        # 2 分句
        sent_tokenize_list = nltk.sent_tokenize(content)
        
        # 3 清理句子
        clean_sent_list = [clean_sent(sent) for sent in sent_tokenize_list]
        
        # 4 分词 
        # 去掉长度小于3、去掉数字、去掉标点符号/去掉 non-alpha 词
        word_tokenize_list = []
        for sent in clean_sent_list:
            word_t_l = filter(lambda x: len(x) > 3, map(clean_word, nltk.word_tokenize(sent)))
            word_tokenize_list += list(word_t_l)
        
        # 5 清理词
        # 去掉停用词、，小写化
        word_list = [word.lower() for word in word_tokenize_list if word.lower() not in stopwords]
        
        # 6 词形还原
        wnl = WordNetLemmatizer()
        word_list = [wnl.lemmatize(word) for word in word_list]

        line = " ".join(word_list)
    return line

def clean_sent(sent):
    sent = sent.replace("\n", " ").replace('\r',' ').replace('\r\n',' ')
    sent = sent.replace('\t', ' ').replace('\xa0', ' ')
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
    return sent

def clean_word(s):  
    # 去除标点和特殊字符、数字、汉字
    regex = re.compile(r"[^a-zA-Z]")
    s = regex.sub('', s)
    
    # 去除字符串中的数字 s = 'abc123def456ghi789zero0'
    remove_digits = str.maketrans('', '', digits)
    res = s.translate(remove_digits)
    return res












