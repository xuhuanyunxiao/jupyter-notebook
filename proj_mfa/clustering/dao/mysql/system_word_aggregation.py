#!/usr/bin/python
# -*- coding: utf-8 -*-

from db_mysql import BaseMysql


class SystemWordAggregation(BaseMysql):
    def __init__(self):
        super(SystemWordAggregation, self).__init__()
        self.table_name = 'system_word_aggregation'

    def get_dicts_ch(self):
        dicts = []

        sql = "SELECT id, keywords FROM system_word_aggregation " \
              "WHERE flag = 1 AND language_type = 0 AND type = 4"

        records = self.fetch_all(sql)

        for row in records:
            id = row['id']
            dic = row['keywords']

            # 加入结果
            dicts.append((id, dic))
        return dicts

    def get_dicts_en(self):
        dicts = []

        sql = "SELECT id, keywords FROM system_word_aggregation " \
              "WHERE flag = 1 AND language_type = 1 AND type = 4"

        records = self.fetch_all(sql)

        for row in records:
            id = row['id']
            dic = row['keywords']

            # 加入结果
            dicts.append((id, dic))
        return dicts


if __name__ == "__main__":
    custom_dic = SystemWordAggregation()
    results = custom_dic.get_dicts_en()

    for dic in results:
        print dic[1]
