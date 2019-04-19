#!/usr/bin/python
# -*- coding: utf-8 -*-
import json
import os
import sys

import MySQLdb
from DBUtils.PooledDB import PooledDB
from MySQLdb.cursors import DictCursor

from utils.logger import logger

reload(sys)
sys.setdefaultencoding('utf-8')


class BaseMysql(object):
    """
    MYSQL数据库对象，负责产生数据库连接 , 此类中的连接采用连接池实现获取连接对象：conn = Mysql.getConn()
            释放连接对象;conn.close()或del conn

    python不考虑多线程情况.
    """
    # 连接池对象
    __pool = None

    # 配置对象
    p_dir = os.path.dirname(os.path.abspath(__file__))
    g_dir = os.path.dirname(p_dir)
    gg_dir = os.path.dirname(g_dir)
    config_path = os.path.join(gg_dir, 'config', 'db.conf')

    with open(config_path, 'r') as f:
        conf = json.load(f)

    host = conf['host']
    port = conf['port']
    user = conf['user']
    passwd = conf['passwd']
    db = conf['db']
    charset = conf['charset']

    @staticmethod
    def __get_pool():
        """
        @summary: 静态方法，创建连接池
        @return MySQLdb.connection
        """
        if BaseMysql.__pool is None:
            __pool = PooledDB(creator=MySQLdb, mincached=1, maxcached=20,
                              host=BaseMysql.host,
                              port=BaseMysql.port,
                              user=BaseMysql.user,
                              passwd=BaseMysql.passwd,
                              db=BaseMysql.db,
                              use_unicode=False,
                              charset=BaseMysql.charset,
                              cursorclass=DictCursor,
                              setsession=['SET AUTOCOMMIT=1'])
        return __pool

    @staticmethod
    def get_conn():
        """
        @summary: 静态方法，从连接池中取出连接
        @return MySQLdb.connection
        """
        return BaseMysql.__get_pool().connection()

    @staticmethod
    def fetch_one(sql, param=None):
        """
        @summary: 执行查询，并取出第一条
        @param sql:查询ＳＱＬ，如果有查询条件，请只指定条件列表，并将条件值使用参数[param]传递进来
        @param param: 可选参数，条件列表值（元组/列表）
        @return: result list/boolean 查询到的结果集
        """
        _conn, _cursor = None, None
        try:
            _conn = BaseMysql.get_conn()
            _cursor = _conn.cursor()

            logger.debug('fetch_one, sql: ' + sql)
            if param is None:
                count = _cursor.execute(sql)
            else:
                count = _cursor.execute(sql, param)

            if count > 0:
                result = _cursor.fetchone()
            else:
                result = None
        except MySQLdb.Error, e:
            raise e
        finally:
            BaseMysql.dispose(_cursor, _conn)
        return result

    @staticmethod
    def fetch_all(sql, param=None):
        """
        @summary: 执行查询，并取出所有结果集
        @param sql:查询ＳＱＬ，如果有查询条件，请只指定条件列表，并将条件值使用参数[param]传递进来
        @param param: 可选参数，条件列表值（元组/列表）
        @return: result list(字典对象)/boolean 查询到的结果集
        """
        _conn, _cursor = None, None
        try:
            _conn = BaseMysql.get_conn()
            _cursor = _conn.cursor()

            logger.debug('fetch_all, sql: ' + sql)
            if param is None:
                count = _cursor.execute(sql)
            else:
                count = _cursor.execute(sql, param)
            logger.debug('fetch_all, count: ' + str(count))

            if count > 0:
                result = _cursor.fetchall()
            else:
                result = []
        except MySQLdb.Error, e:
            raise e
        finally:
            BaseMysql.dispose(_cursor, _conn)
        return result

    @staticmethod
    def fetch_many(sql, num, param=None):
        """
        @summary: 执行查询，并取出num条结果
        @param sql:查询ＳＱＬ，如果有查询条件，请只指定条件列表，并将条件值使用参数[param]传递进来
        @param num:取得的结果条数
        @param param: 可选参数，条件列表值（元组/列表）
        @return: result list/boolean 查询到的结果集
        """
        _conn, _cursor = None, None
        try:
            _conn = BaseMysql.get_conn()
            _cursor = _conn.cursor()

            logger.debug('fetch_many, sql: ' + sql)
            if param is None:
                count = _cursor.execute(sql)
            else:
                count = _cursor.execute(sql, param)
            logger.debug('fetch_many, count: ' + str(count))

            if count > 0:
                result = _cursor.fetchmany(num)
            else:
                result = []
        except MySQLdb.Error, e:
            raise e
        finally:
            BaseMysql.dispose(_cursor, _conn)
        return result

    # 针对读操作返回结果集
    def select(self, table, cond_dict='', order=''):
        """
        @summary: 执行条件查询，并取出所有结果集
        @cond_dict:{'name':'xiaoming'...}
        @order:'order by id desc'
        @return:  result ({"col":"val","":""},{})
        """
        consql = ' '
        if cond_dict != '':
            for k, v in cond_dict.items():
                consql = consql + k + '=' + v + ' and'
        consql = consql + ' 1=1 '
        sql = 'select * from %s where ' % table
        sql = sql + consql + order
        return self.fetch_all(sql)

    # 插入一条数据, 并且返回自动生成的id
    @staticmethod
    def insert_get_id(sql, arg=None):
        _id, _conn, _cursor = None, None, None
        try:
            _conn = BaseMysql.get_conn()
            _cursor = _conn.cursor()

            logger.debug('insert_get_id, sql: ' + sql)
            if arg is None:
                _cursor.execute(sql)
            else:
                _cursor.execute(sql, arg)
            _id = _cursor.lastrowid
            BaseMysql.commit(_conn)
            return _id
        except MySQLdb.Error, e:
            BaseMysql.rollback(_conn)
            raise e
        finally:
            BaseMysql.dispose(_cursor, _conn)

    # 针对更新,删除,事务等操作失败时回滚
    @staticmethod
    def execute_with_transaction(sql, arg=None):
        _conn, _cursor = None, None
        try:
            _conn = BaseMysql.get_conn()
            _cursor = _conn.cursor()

            logger.debug('execute_with_transaction, sql: ' + sql)
            if arg is None:
                _cursor.execute(sql)
            else:
                _cursor.execute(sql, arg)
            BaseMysql.commit(_conn)
        except MySQLdb.Error, e:
            BaseMysql.rollback(_conn)
            raise e
        finally:
            BaseMysql.dispose(_cursor, _conn)

    def insert(self, table, attrs, value):
        """
        @summary: 向数据表插入一条记录, 并且返回指定的
        @param attrs = [] :要插入的属性
        @param value = [] :要插入的数据值
        """
        attrs_sql = '(' + ','.join(attrs) + ')'
        value_str = BaseMysql.transfer_content(value)
        values_sql = ' values(' + value_str + ')'
        sql = 'insert into %s' % table
        sql = sql + attrs_sql + values_sql
        self.execute_with_transaction(sql)

    def insert(self, table, attrs, value):
        """
        @summary: 向数据表插入一条记录
        @param attrs = [] :要插入的属性
        @param value = [] :要插入的数据值
        """
        attrs_sql = '(' + ','.join(attrs) + ')'
        value_str = BaseMysql.transfer_content(value)
        values_sql = ' values(' + value_str + ')'
        sql = 'insert into %s' % table
        sql = sql + attrs_sql + values_sql
        self.execute_with_transaction(sql)

    def insert_dict(self, table, attrs):
        """
        @summary: 向数据表插入一条记录
        @param attrs = {"colNmae:value"} :要插入的属性：数据值
        """
        attrs_sql = '(' + ','.join(attrs.keys()) + ')'
        value_str = BaseMysql.transfer_content(attrs.values())  # ','.join(attrs.values())
        values_sql = ' values(' + value_str + ')'
        sql = 'insert into %s' % table
        sql = sql + attrs_sql + values_sql
        self.execute_with_transaction(sql)

    # 将list转为字符串
    @staticmethod
    def transfer_content(self, content):
        if content is None:
            return None
        else:
            Strtmp = ""
            for col in content:
                if Strtmp == "":
                    Strtmp = "\"" + col + "\""
                else:
                    Strtmp += "," + "\"" + col + "\""
            return Strtmp

    def update(self, sql, param=None):
        """
        @summary: 更新数据表记录
        @param sql: ＳＱＬ格式及条件，使用(%s,%s)
        @param param: 要更新的  值 tuple/list
        @return: count 受影响的行数
        """
        return self.execute_with_transaction(sql, param)

    def delete(self, sql, param=None):
        """
        @summary: 删除数据表记录
        @param sql: ＳＱＬ格式及条件，使用(%s,%s)
        @param param: 要删除的条件 值 tuple/list
        @return: count 受影响的行数
        """
        return self.execute_with_transaction(sql, param)

    # 针对更新,删除,事务等操作失败时回滚
    @staticmethod
    def execute_many_with_transaction(sql, values):
        """
        @summary: 向数据表插入多条记录
        @param sql:要插入的ＳＱＬ格式
        @param values:要插入的记录数据tuple(tuple)/list[list]
        """
        _conn, _cursor = None, None
        try:
            _conn = BaseMysql.get_conn()
            _cursor = _conn.cursor()

            logger.debug('execute_many_with_transaction:' + sql)
            _cursor.executemany(sql, values)
            BaseMysql.commit(_conn)
        except MySQLdb.Error, e:
            BaseMysql.rollback(_conn)
            raise e
        finally:
            BaseMysql.dispose(_cursor, _conn)

    def insert_many(self, table, attrs, values):
        """
        @summary: 向数据表插入多条数据
        @param attrs = [id,name,...]  :要插入的属性
        @param values = [[1,'jack'],[2,'rose']] :要插入的数据值
        """
        values_sql = ['%s' for v in attrs]
        attrs_sql = '(' + ','.join(attrs) + ')'
        values_sql = ' values(' + ','.join(values_sql) + ')'
        sql = 'insert into %s' % table
        sql = sql + attrs_sql + values_sql
        self.execute_many_with_transaction(sql, values)

    @staticmethod
    def rollback(conn):
        """
        @summary: 释放连接池资源
        """
        if conn is not None:
            conn.rollback()

    @staticmethod
    def commit(conn):
        """
        @summary: 释放连接池资源
        """
        if conn is not None:
            conn.commit()

    @staticmethod
    def dispose(conn, cursor):
        """
        @summary: 释放连接池资源
        """
        if cursor is not None:
            cursor.close()
        if conn is not None:
            conn.close()