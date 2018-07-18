# -*- coding:utf-8 -*-
import sys
import glob
#import networkx as nx
#import matplotlib.pyplot as plt
from math import *
import jieba, os
import re
from string import digits
import csv

#from gensim import corpora, models, similarities


stopwords = {}
stoplist = [' ','   ','哈哈哈','你','我','http','https','repost','request','他','她','吧','呵呵','嘻嘻','么','了','  ','的','...','是','哈哈','转发','微博','回复','哼','嗯','哦','http','cn','记者','\r\n','\n','\r']

regex = re.compile(r"[^\u4e00-\u9f5aa-zA-Z0-9]")

stopwords = {}
stw = open("corpus/stopwords.txt",encoding='UTF-8')
for ws in stw:
    ws = ws.replace("\n", "")
    ws = ws.replace("\r", "")
    stopwords[ws] = 1
stw.close()

jieba.load_userdict('corpus/company.txt')
jieba.load_userdict('corpus/user_dict.txt')
jieba.load_userdict('corpus/bank_dict.txt')
    
def etl(s): #remove 标点和特殊字符
    #s=re.sub("[\s+\.\!\/_,$%^*(+\"\')]+|[+——()【】·：■▼〔〕-“”！，。？、~@#￥%……&*（）]+", "",s)
    s = regex.sub('', s)
    remove_digits = str.maketrans('', '', digits)
    res = s.translate(remove_digits)
    return res

    
def handlefile(tfile):
    testfile = open(tfile,'r+',newline=None)
#    testfile = csv.reader(open(tfile,'r+'))
#    testfile.readline()
    line = testfile.readlines()
    raw = ''.join(line).strip('\n')
        

    #raw = line
    #print(line)
    #raw = raw[0]
    if (raw !=""):
        word_list_1 = []
        line = ""     
        word_list = []
        remove_words = []
        #raw = str(raw)
        raw = clearsen(raw)
        #print(raw)
        word_list = filter(lambda x: len(x) > 0, map(etl, jieba.cut(raw, cut_all=False)))       
        #word_list = list(jieba.cut(raw, cut_all = False))
        #print(list(word_list))
        ll  = list(word_list)
        #print(ll)
        for wd in ll:
#                try:
#                    wd.encode('utf-8')
#                except:
#                    continue
            ##if stopwords.has_key(wd.encode('utf-8')):
            if wd in stopwords:
                remove_words.append(wd)
                
        #print(list(remove_words))
#            for wd in remove_words:
#                word_list_1 = filter(lambda a: a !=wd, list(word_list))
        
        for l in ll:
            if not (l in remove_words):
                word_list_1.append(l)

        #print(word_list_1)
        
        for wd in word_list_1:
            line = line + wd +" "
        #line = line +"\n"
        #print(line)
        tagfile.write(line+"\n")


    testfile.close()


def clearsen(sent):
    sent = sent.replace('\r\n','')
    sent = sent.replace('\t','')
    sent = sent.replace('\f','')
    sent = sent.replace("\n", "")
    sent = sent.replace('\r','')
    sent = sent.replace('^l','')
    
   
##    reobj = re.compile('//@(.*?)[:\s]')
##    sent = reobj.sub("", sent)
##    reobj = re.compile("@(.*?)[:\s]")
##    sent = reobj.sub("", sent)
##    reobj = re.compile(r"\[[^\[\]]*?\]")
##    sent = reobj.sub("", sent)
    
    sent = sent.replace("，", ",")
    sent = sent.replace("。", ".")
    sent = sent.replace("！", "!")
    sent = sent.replace("？", "?")
##    reobj = re.compile("//(.*?)[:\s]")
##    sent = reobj.sub("", sent)
    return(sent)


def combf(tfilename,sfilename):
    tfile = open(tfilename,'a+',encoding='UTF-8')       
    sfile = open(sfilename,'r',encoding='UTF-8') 
    for s in sfile:
        tfile.write(s)
    tfile.close()
    sfile.close()
    
    

if __name__=='__main__':
#    reload(sys)  
#    sys.setdefaultencoding('utf-8')
    
#    combf("bank_all_1.txt","o_bank_1_1.txt")
#    combf("bank_all_1.txt","bank_1_1.txt")
#    combf("bank_all_1.txt","0316_1_1.txt")
#    combf("bank_all_1.txt","0428_1_1.txt")
#    combf("bank_all_1.txt","0512_1_1.txt")
#    
#    combf("bank_all_0.txt","o_bank_0_0.txt")
#    combf("bank_all_0.txt","bank_0_0.txt")
#    combf("bank_all_0.txt","0316_0_0.txt")
#    combf("bank_all_0.txt","0428_0_0.txt")
#    combf("bank_all_0.txt","0512_0_0.txt")
  
#    stw=open("../stopwords.txt",encoding='UTF-8')
#    for ws in stw:
#        ws = ws.replace("\n", "")
#        ws = ws.replace("\r", "")
#        stopwords[ws]=1
#    stw.close()
    
##    txt_filenames = "data1o/1895250515.txt"
##    print txt_filenames
    
    #jieba.initialize()
#    jieba.load_userdict('C:/han/work/dict/company.txt')  
#    jieba.load_userdict('C:/han/work/dict/user_dict.txt')
#    jieba.load_userdict('C:/han/work/dict/bank_dict.txt')
    #jieba.load_userdict('neg_words.txt')
#    jieba.load_userdict('C:/han/work/dict/chinesenames.txt')
    #txt_filenames = glob.glob('*.txt')
#    tagfile = open("0613_p.txt",'w',encoding='UTF-8')    
#    txt_filenames = glob.glob('0604-0608保监会误判为负面的数据/*.txt')
    #txt_filenames = glob.glob('i_0_0.txt')

    tagfile = open("0613_n.txt",'w',encoding='UTF-8')    
    txt_filenames = glob.glob('0604-0608保监会负面/*.txt')
    
    for filename in txt_filenames:
        print ("handling file: "+filename)
        handlefile(filename)

   
    


#    txt_filenames = 'b_p.txt'
#    tagfile = open("b_p_1.txt",'w',encoding='UTF-8')       
#    handlefile(txt_filenames)
#    tagfile.close()     
    
#    txt_filenames = 'test_n.txt'
#    tagfile = open("test_n_1.txt",'w',encoding='UTF-8')       
#    handlefile(txt_filenames)
    tagfile.close()    
#    for filename in txt_filenames:
#        print ("handling file: "+filename)
#        handlefile(filename)

##    tagfile.close()

##        
##    all_stems = sum(train_set, [])
##    stems_once = set(stem for stem in set(all_stems) if all_stems.count(stem) == 1)
##    texts = [[stem for stem in text if stem not in stems_once] for text in train_set]
##    train_set = texts
    
##    print "creating dictionary..."
##    dic = corpora.Dictionary(train_set)
##    stop_ids = [dic.token2id[stopword] for stopword in stoplist if stopword in dic.token2id]
##    once_ids = [tokenid for tokenid, docfreq in dic.dfs.iteritems() if docfreq == 1]
##    dic.filter_tokens(stop_ids+once_ids)
##    dic.compactify()
##    
##    corpus = [dic.doc2bow(text) for text in train_set]    
##    
##    print "creating TFIDF model..."
##    tfidf = models.TfidfModel(corpus)
##    corpus_tfidf = tfidf[corpus]
##    print "creating LDA model..."
##    lda = models.LdaModel(corpus_tfidf, id2word = dic, num_topics = 10)
##    corpus_lda = lda[corpus_tfidf]
##
##
##    for i in range(0, 10):
##         print lda.print_topic(i)



## -*- coding:utf-8 -*-
#import sys
#import glob
##import networkx as nx
##import matplotlib.pyplot as plt
#from math import *
#import jieba, os
#import re
##from gensim import corpora, models, similarities
#
#
#stopwords = {}
#stoplist = [' ','   ','哈哈哈','你','我','他','她','吧','呵呵','嘻嘻','么','了','  ','的','...','是','哈哈','转发','微博','回复','哼','嗯','哦','http','cn','记者','\r\n','\n','\r']
#
#regex = re.compile(ur"[^\u4e00-\u9f5aa-zA-Z0-9]")
#
###tagfile = open("0301bu_0_0.txt",'a')
#    
#def etl(s): #remove 标点和特殊字符
#    s = regex.sub('', s)
#    return s
#
#    
#def handlefile(tfile):
#    testfile = open(tfile,'r+')
#
#    for line in testfile:
#        line = line.split("\t")
#        raw = line[1]
#        
###        if (len(line)>=2) and (len(line[1])>2):
###            raw = line[1]
###        else:
###            raw = line[0]
#            
#        if (raw !=""):
#            line = ""
#            word_list = []
#            remove_words = []
#            #raw = str(raw)
#            raw = clearsen(raw)
#            word_list = filter(lambda x: len(x) > 0, map(etl, jieba.cut(raw, cut_all=True)))       
#            #word_list = list(jieba.cut(raw, cut_all = False))
#            for wd in word_list:
#                try:
#                    wd.encode('utf-8')
#                except:
#                    continue
#                if stopwords.has_key(wd.encode('utf-8')):
#                    remove_words.append(wd)
#                    
#            #print str(word_list)
#            for wd in remove_words:
#                word_list = filter(lambda a: a !=wd, word_list)
#            for wd in word_list:
#                line = line + wd +" "
#            line = line +"\n"
#            #print line
#            tagfile.write(line.encode("utf-8"))
#
#    testfile.close()
#
#
#def clearsen(sent):
#    sent = sent.replace("\n", "")
#    sent = sent.replace('\r','')
#    sent = sent.replace('\r\n','')
#    reobj = re.compile('//@(.*?)[:\s]')
#    sent = reobj.sub("", sent)
#    reobj = re.compile("@(.*?)[:\s]")
#    sent = reobj.sub("", sent)
#    reobj = re.compile(r"\[[^\[\]]*?\]")
#    sent = reobj.sub("", sent)
#    
#    sent = sent.replace("，", ",")
#    sent = sent.replace("。", ".")
#    sent = sent.replace("！", "!")
#    sent = sent.replace("？", "?")
#    reobj = re.compile("//(.*?)[:\s]")
#    sent = reobj.sub("", sent)
#    return(sent)
#
#
#if __name__=='__main__':
##    reload(sys)  
##    sys.setdefaultencoding('utf-8')
#
###    f = open("test_1_1.txt","r+")
#    tagfile = open("0301_bu_1_0.txt",'w')
###    i = 0
###    for content in f:
###        if res[i]:
###            tagfile.write(content.encode("utf-8"))
###        i = i+1
###    f.close()
###    tagfile.close()
#
#    stw=open("stopwords.txt")
#    for ws in stw:
#        ws = ws.replace("\n", "")
#        ws = ws.replace("\r", "")
#        stopwords[ws]=1
#    stw.close()
#    
###    txt_filenames = "data1o/1895250515.txt"
###    print txt_filenames
#    
#    jieba.initialize()
#    #txt_filenames = glob.glob('*.txt')
#    #txt_filenames = glob.glob('*.txt')
#    #txt_filenames = glob.glob('test_1.txt')
#    txt_filenames = '0301bu_1.txt'
#    
#    handlefile(txt_filenames)
#    
#    tagfile.close()
#    
###    for filename in txt_filenames:
###        print "handling file: "+filename
###        handlefile(filename)
###
###    tagfile.close()
###        
###    all_stems = sum(train_set, [])
###    stems_once = set(stem for stem in set(all_stems) if all_stems.count(stem) == 1)
###    texts = [[stem for stem in text if stem not in stems_once] for text in train_set]
###    train_set = texts
#    
###    print "creating dictionary..."
###    dic = corpora.Dictionary(train_set)
###    stop_ids = [dic.token2id[stopword] for stopword in stoplist if stopword in dic.token2id]
###    once_ids = [tokenid for tokenid, docfreq in dic.dfs.iteritems() if docfreq == 1]
###    dic.filter_tokens(stop_ids+once_ids)
###    dic.compactify()
###    
###    corpus = [dic.doc2bow(text) for text in train_set]    
###    
###    print "creating TFIDF model..."
###    tfidf = models.TfidfModel(corpus)
###    corpus_tfidf = tfidf[corpus]
###    print "creating LDA model..."
###    lda = models.LdaModel(corpus_tfidf, id2word = dic, num_topics = 10)
###    corpus_lda = lda[corpus_tfidf]
###
###
###    for i in range(0, 10):
###         print lda.print_topic(i)
#
