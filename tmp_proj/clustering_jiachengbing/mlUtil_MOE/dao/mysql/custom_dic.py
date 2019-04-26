#!/usr/bin/python
# -*- coding: utf-8 -*-

from db_mysql import BaseMysql


class CustomDic(BaseMysql):
    def __init__(self):
        super(CustomDic, self).__init__()
        self.table_name = 'custom_dic'

    def get_dicts_ch(self):
        dicts = []

        sql = "SELECT id, dic FROM custom_dic WHERE delete_flag = 0 AND language_flag = 0"

        records = self.fetch_all(sql)

        for row in records:
            id = row['id']
            dic = row['dic']

            # 加入结果
            dicts.append((id, dic))
        return dicts

    def get_dicts_en(self):
        dicts = []

        sql = "SELECT id, dic FROM custom_dic WHERE delete_flag = 0 AND language_flag = 1"

        records = self.fetch_all(sql)

        for row in records:
            id = row['id']
            dic = row['dic']

            # 加入结果
            dicts.append((id, dic))
        return dicts


if __name__ == "__main__":
    custom_dic = CustomDic()
    results = custom_dic.get_dicts_en()

    for dic in results:
        print dic[1]
