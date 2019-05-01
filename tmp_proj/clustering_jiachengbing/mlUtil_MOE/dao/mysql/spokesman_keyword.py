#!/usr/bin/python
# -*- coding: utf-8 -*-

from db_mysql import BaseMysql


class SpokesmanKeyword(BaseMysql):
    def __init__(self):
        super(SpokesmanKeyword, self).__init__()
        self.table_name = 'spokesman_keyword'

    def get_words(self):
        """
        获得关键词
        """
        sql = """
        SELECT id, keyword, priority  
        FROM spokesman_keyword 
        WHERE status = 1 
        ORDER BY priority
        """

        records = self.fetch_all(sql)
        return records

