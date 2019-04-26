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
    """
    # 连接池对象
    __pool = None

    # 配置对象
    p_dir = os.path.dirname(os.path.abspath(__file__))
    g_dir = os.path.dirname(p_dir)
    gg_dir = os.path.dirname(g_dir)
    # config_path = os.path.join(gg_dir, 'config', 'db.conf')
    config_path = os.path.join(gg_dir, 'config', 'db_aliyun.conf')

    with open(config_path, 'r') as f:
        conf = json.load(f)

    host = conf['host']
    port = conf['port']
    user = conf['user']
    passwd = conf['passwd']
    db = conf['db']
    charset = conf['charset']

    def __init__(self):
        # 数据库构造函数，从连接池中取出连接，并生成操作游标
        try:
            self._conn = BaseMysql.__getConn()
            self._cursor = self._conn.cursor()
        except Exception, e:
            error = 'Connect failed! ERROR: %s' % (e)
            logger.error(error)
            sys.exit()

    @staticmethod
    def __getConn():
        """
        @summary: 静态方法，从连接池中取出连接
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
                              cursorclass=DictCursor)
        return __pool.connection()

    def execute(self, sql, param=None):
        try:
            logger.info('execute: ' + sql)
            if param is None:
                count = self._cursor.execute(sql)
            else:
                count = self._cursor.execute(sql, param)
            return count
        except MySQLdb.Error, e:
            error = 'execute failed! ERROR (%s): %s' % (e.args[0], e.args[1])
            logger.error(error)

    def fetch_one(self, sql, param=None):
        """
        @summary: 执行查询，并取出第一条
        @param sql:查询ＳＱＬ，如果有查询条件，请只指定条件列表，并将条件值使用参数[param]传递进来
        @param param: 可选参数，条件列表值（元组/列表）
        @return: result list/boolean 查询到的结果集
        """
        count = self.execute(sql, param)
        if count > 0:
            result = self._cursor.fetchone()
        else:
            result = None
        return result

    def fetch_all(self, sql, param=None):
        """
        @summary: 执行查询，并取出所有结果集
        @param sql:查询ＳＱＬ，如果有查询条件，请只指定条件列表，并将条件值使用参数[param]传递进来
        @param param: 可选参数，条件列表值（元组/列表）
        @return: result list(字典对象)/boolean 查询到的结果集
        """
        count = self.execute(sql, param)
        logger.info('count: ' + str(count))
        if count > 0:
            result = self._cursor.fetchall()
        else:
            result = []
        return result

    def fetch_many(self, sql, num, param=None):
        """
        @summary: 执行查询，并取出num条结果
        @param sql:查询ＳＱＬ，如果有查询条件，请只指定条件列表，并将条件值使用参数[param]传递进来
        @param num:取得的结果条数
        @param param: 可选参数，条件列表值（元组/列表）
        @return: result list/boolean 查询到的结果集
        """
        count = self.execute(sql, param)
        if count > 0:
            result = self._cursor.fetchmany(num)
        else:
            result = []
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

    # 针对更新,删除,事务等操作失败时回滚
    def execute_with_transaction(self, sql='', arg=None):
        try:
            logger.info('__execute_with_transaction: ' + sql)
            if arg is None:
                self._cursor.execute(sql)
            else:
                self._cursor.execute(sql, arg)
            self._conn.commit()
        except MySQLdb.Error, e:
            self._conn.rollback()
            error = '__execute_with_transaction failed! ERROR (%s): %s' % (e.args[0], e.args[1])
            logger.error(error)

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

    # 针对更新,删除,事务等操作失败时回滚
    def execute_many_with_transaction(self, sql, values=None):
        """
        @summary: 向数据表插入多条记录
        @param sql:要插入的ＳＱＬ格式
        @param values:要插入的记录数据tuple(tuple)/list[list]
        """
        try:
            logger.info('execute_many_with_transaction:' + sql)
            if values is None:
                self._cursor.executemany(sql)
            else:
                self._cursor.executemany(sql, values)
            self._conn.commit()
        except MySQLdb.Error, e:
            self._conn.rollback()
            error = 'execute_many_with_transaction failed! ERROR (%s): %s' % (e.args[0], e.args[1])
            logger.error(error)
            sys.exit()

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

    def begin(self):
        """
        @summary: 开启事务
        """
        self._conn.autocommit(0)

    def end(self, option='commit'):
        """
        @summary: 结束事务
        """
        if option == 'commit':
            self._conn.commit()
        else:
            self._conn.rollback()

    def dispose(self, isEnd=1):
        """
        @summary: 释放连接池资源
        """
        if isEnd == 1:
            self.end('commit')
        else:
            self.end('rollback');
        self._cursor.close()
        self._conn.close()
