#!/usr/bin/python
# -*- coding: utf-8 -*-

import langid

from db_mysql import BaseMysql
from entity import ClusterMessageObj

group_id_dict = {
    1: ([1, 5, 13], 0),
    2: ([7, 16], 1),
    3: ([2, 3, 4, 11], 0),
    4: ([15], 1),
    5: ([16], 1)
}


class BaseDataView(BaseMysql):
    def __init__(self):
        super(BaseDataView, self).__init__()
        self.table_name = 'base_data_view'

    def get_involved_china_corpus(self, start_time, end_time, language_type, group_id):
        """
        获得聚类语料
        :param start_time:
        :param end_time:
        :param group_id:
        :return:
        """
        sql = """
        SELECT id, title, content, publishtime, site_name 
        FROM base_data_view 
        WHERE publishtime >= '%s' AND publishtime < '%s' 
        AND language_type = %s 
        AND group_id IN %s 
        AND involved_china = 1 
        group by titlehash """ % (start_time, end_time, language_type, group_id)

        records = self.fetch_all(sql)

        data = BaseDataView.parse_corpus_records(records, language_type)
        return data

    def get_summary_corpus(self, start_time, end_time):
        """
       获得划线模型语料
       :param start_time:
       :param end_time:
       :return:
       """
        sql = """
            SELECT bd.id, bd.publishtime, bd.site_name, nar.abstract  
            FROM news_abstract_result nar, base_data bd 
            WHERE nar.bd_id = bd.id 
            AND bd.publishtime >= '%s' AND bd.publishtime < '%s' 
            AND nar.language_type = 1 
            AND nar.is_lined = 1""" % (start_time, end_time)

        records = self.fetch_all(sql)

        data = []
        for row in records:
            id = row['id']

            abstract = row['abstract']
            abstract = abstract.encode('utf-8')

            publish_time = row['publishtime'].strftime("%Y-%m-%d %H:%M:%S").decode('utf-8')
            site_name = row['site_name']
            site_name = site_name.encode('utf-8')

            cluster_obj = ClusterMessageObj(id, abstract, publish_time, '', site_name)
            data.append(cluster_obj)
        return data

    def get_corpus(self, start_time, end_time, language_type, group_id):
        """
        获得聚类语料
        :param start_time:
        :param end_time:
        :param group_id:
        :return:
        """
        sql = """
        SELECT id, title, content, publishtime, site_name 
        FROM base_data_view 
        WHERE publishtime >= '%s' AND publishtime < '%s' 
        AND language_type = %s 
        AND group_id IN %s 
        group by titlehash """ % (start_time, end_time, language_type, group_id)

        records = self.fetch_all(sql)

        data = BaseDataView.parse_corpus_records(records, language_type)
        return data

    @staticmethod
    def parse_corpus_records(records, language_type=None):
        data = []
        for row in records:
            id = row['id']

            title = row['title']
            title = title.encode('utf-8')

            content = row['content']
            content = content.encode('utf-8')

            publish_time = row['publishtime'].strftime("%Y-%m-%d %H:%M:%S").decode('utf-8')
            site_name = row['site_name']
            site_name = site_name.encode('utf-8')

            cluster_obj = ClusterMessageObj(id, title, publish_time, content, site_name)

            # 进行语言过滤
            if language_type is not None:
                if BaseDataView.is_valid_language(language_type, content):
                    data.append(cluster_obj)
            else:
                data.append(cluster_obj)
        return data

    def get_corpus_by_ids(self, ids, language_type):
        ids = [str(id) for id in ids]
        ids_str = ','.join(ids)
        ids_str = '(' + ids_str + ')'

        sql = """
        SELECT id, title, content, publishtime, site_name 
        FROM base_data_view 
        WHERE id IN %s
        """ % (ids_str,)

        records = self.fetch_all(sql)

        data = BaseDataView.parse_corpus_records(records, language_type)
        return data

    @staticmethod
    def is_valid_language(language_type, content):
        validate = False

        try:
            language_flag = langid.classify(content)[0]

            if language_flag == 'en' and language_type == 1:
                validate = True

            if language_flag == 'zh' and language_type == 0:
                validate = True

        except Exception, e:
            validate = True

        return validate


if __name__ == '__main__':
    a = BaseDataView()

    import datetime
    now = datetime.datetime.now()
    end_dt = datetime.datetime.combine(now.date(), datetime.time(now.time().hour, 00, 00))
    start_dt = end_dt - datetime.timedelta(days=1)
    end_time = end_dt.strftime('%Y-%m-%d %H:%M:%S')
    start_time = start_dt.strftime('%Y-%m-%d %H:%M:%S')

    print(a.get_corpus(start_time, end_time, 0, '(1, 5, 13)'))
