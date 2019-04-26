#!/usr/bin/python
# -*- coding: utf-8 -*-
import numpy as np

from utils import jiebaCutWords


class sim_hash:
    def __init__(self, content):
        self.simhash = self.simhash(content)

    def __str__(self):
        return str(self.simhash)

    def simhash(self, content):
        cutResult = jiebaCutWords.cut_words_for_cluster(content)

        key_word_list = []
        for words_str in cutResult:
            keyWord = {}
            words = words_str.split('@')
            for word in words:
                if word not in keyWord.keys():
                    keyWord[word] = 1
                else:
                    keyWord[word] += 1
            key_word_list.append(keyWord)

        # 即先按照权重排序，再按照词排序
        simhash_list = []
        for keyWord in key_word_list:
            keyList = []
            for key in keyWord:
                feature = key
                weight = keyWord[feature]
                feature = self.string_hash(feature)
                temp = []
                for i in feature:
                    if (i == '1'):
                        temp.append(weight)
                    else:
                        temp.append(-weight)
                keyList.append(temp)
            list1 = np.sum(np.array(keyList), axis=0)
            if (keyList == []):  # 编码读不出来
                return '00'
            simhash = ''
            for i in list1:
                if (i > 0):
                    simhash = simhash + '1'
                else:
                    simhash = simhash + '0'
            simhash_list.append(simhash)

        return simhash_list

    def string_hash(self, source):
        if source == "":
            return 0
        else:
            x = ord(source[0]) << 7
            m = 1000003
            mask = 2 ** 128 - 1
            for c in source:
                x = ((x * m) ^ ord(c)) & mask
            x ^= len(source)
            if x == -1:
                x = -2
            x = bin(x).replace('0b', '').zfill(64)[-64:]
            return str(x)

        '''
        以下是使用系统自带hash生成，虽然每次相同的会生成的一样，
        不过，对于不同的汉子产生的二进制，在计算海明码的距离会不一样，
        即每次产生的海明距离不一致
        所以不建议使用。
        '''
        # x=str(bin(hash(source)).replace('0b','').replace('-','').zfill(64)[-64:])
        # print(source,x,len(x))
        # return x

    def hamming_dis(self, com):
        t1 = '0b' + self.simhash
        t2 = '0b' + com.simhash
        n = int(t1, 2) ^ int(t2, 2)
        i = 0
        while n:
            n &= (n - 1)
            i += 1
        return i


if __name__ == '__main__':
    a = sim_hash(
        [
            '中消协体验网络订餐:部分外卖肉食生蛆还有毛发',
            '中消协：部分网络订餐存在异物，个别无资质店铺仍正常营业',
            '中消协调查:部分网络订餐存在异物 不提供发票'])
    print a.simhash
