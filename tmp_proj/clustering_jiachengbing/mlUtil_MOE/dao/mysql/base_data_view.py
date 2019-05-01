#!/usr/bin/python
# -*- coding: utf-8 -*-

import langid

from db_mysql import BaseMysql
from entity import ClusterMessageObj
from utils.logger import logger
import itertools

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

    def get_keywords_for_sel_clusterdata(self, language_type):
        """
        获取多组关键词，先按一组关键词选择数据作为一类。余下数据用于聚类
        :return:
        """

        sql = """
            SELECT 
                *
            FROM
                wjbdb.tool_sel_clusterdata_by_keywords
            WHERE
                language_type = %s
            ORDER BY rank""" % (language_type)

        logger.info('get_keywords_for_sel_clusterdata: %s' % (str(sql)))
        # 按rank排序
        records = self.fetch_all(sql)
        data = []
        for row in records:
            # keywords = row['keywords']
            # keyword_list = keywords.split('; ')
            # data.append(keyword_list)
            base_keyword = row['base_keyword']
            sel_keyword = row['sel_keyword']
            if sel_keyword:
                keywords = base_keyword + ';' + sel_keyword
            else :
                keywords = base_keyword

            keyword_list = [k.strip() for k in keywords.strip().split(';') if len(k.strip()) > 0]
            keyword_list_1 = [k.strip().split(',') for k in keyword_list]

            expr = '''key_list = list(x for x in itertools.product('''
            for l in keyword_list_1:
                l = [ll.strip() for ll in l]
                expr += str(l) + ','
            expr += '''))'''
            exec(expr)
            data.append([';'.join(keyword_list), key_list])

        return data


if __name__ == '__main__':
    a = BaseDataView()

    import datetime
    now = datetime.datetime.now()
    end_dt = datetime.datetime.combine(now.date(), datetime.time(now.time().hour, 00, 00))
    start_dt = end_dt - datetime.timedelta(days=1)
    end_time = end_dt.strftime('%Y-%m-%d %H:%M:%S')
    start_time = start_dt.strftime('%Y-%m-%d %H:%M:%S')

    print(a.get_corpus(start_time, end_time, 0, '(1, 5, 13)'))
