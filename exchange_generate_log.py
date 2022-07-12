#!/bin/env python3
# -*- coding: utf-8 -*
'''
项目名称:exchange_generate_log.py
Author: yangyang
功能：
Date: 2022-5-7
cron: 10 0-23/4,23 * * *
new Env("极速版生成log");
'''

import json
import requests
from exchange_lib import *


if 'DATABASE_TYPE' in os.environ and \
    'DATABASE_HOST' in os.environ and \
    'DATABASE_PORT' in os.environ and \
    'DATABASE_USER' in os.environ and \
    'DATABASE_PASSWD' in os.environ and \
    'DATABASE_DATABASE' in os.environ:
    database_dict = {
                "type":     os.environ['DATABASE_TYPE'],
                "host":     os.environ['DATABASE_HOST'],        # 数据库主机地址
                "port":     os.environ['DATABASE_PORT'],
                "user":     os.environ['DATABASE_USER'],        # 数据库用户名
                "passwd":   os.environ['DATABASE_PASSWD'],      # 数据库密码
                "database": os.environ['DATABASE_DATABASE']
            }
else:
    database_dict = {
                'type': 'sqlite',
                'name': "filtered_cks.db"
            }


generate_number = getEnvs(os.environ['JDLITE_LOG_NUMBER']) if "JDLITE_LOG_NUMBER" in os.environ else 100
api_url = os.environ['JDLITE_LOG_API'] if "JDLITE_LOG_API" in os.environ else None

logs = getLogs(url=api_url, num=generate_number)
table_name = 'log_' + datetime.datetime.now().strftime("%Y%m%d")
log_sql = SQLProcess(table_name=table_name, database_dict=database_dict, table_type='log')
log_sql.deleteTable()
log_sql.createTable()
log_sql.insertManyLog(logs, times=3)
printT(f"{generate_number} logs has been inserted.")
# log_sql.printLogs()
printT(f"There are {log_sql.logsNumber()} logs in table {table_name}")