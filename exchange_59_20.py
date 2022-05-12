#!/bin/env python3
# -*- coding: utf-8 -*
'''
项目名称:exchange_59_20.py
Author: yangyang
功能：
Date: 2022-5-12
cron: 0 58 9,13,17,21,23 * * *
new Env("京东59减20");
'''

import random
import requests
import re
import sys
import datetime
import multiprocessing
import time
from urllib.parse import quote, unquote
import os
import mysql.connector as mysql
import sqlite3 as sqlite

# 处理ck和log的数据库，分别有两张表
class SQLProcess:

    def __init__(self, table_name, database_dict={
        'type': 'sqlite',
        'name': "filtered_cks.db"
    }, table_type='cookie', default_times=3):
        self.database_dict = database_dict
        self.table_name = self.getTableName(table_name)
        # # 默认为处理ck的表，如果需要处理logs，则table_type为'log'
        self.table_type = table_type
        if self.table_type == 'log':
            self.log_set = set()
        self.default_times = default_times
        print(self.table_name)
        self.createDatebase()
        self.createTable()

    def getTableName(self, name):
        if len(name) > 300:
            name = name[:300]
        if len(name) < 20:
            return name
        # temp = 'table_' + name.replace('=', '').replace('%', '').replace('_', '').split("key")[-1][::10]
        temp = 'table_' + name.replace('=', '').replace('%', '').replace('_', '').replace('.', '')[::10]
        return temp if len(temp) <= 20 else temp[:20]

    def deleteTable(self):
        self.c.execute(f'''
                        DROP TABLE IF EXISTS {self.table_name}
                        ''')
        self.conn.commit()

    def createDatebase(self):
        if 'type' not in self.database_dict:
            print("Error in database configure! Exit...")
            exit()

        if self.database_dict['type'] == 'mysql':
            try:
                start = time.time()
                self.conn = mysql.connect(
                    host=self.database_dict['host'],  # 数据库主机地址
                    port=self.database_dict['port'],
                    user=self.database_dict['user'],  # 数据库用户名
                    passwd=self.database_dict['passwd'],  # 数据库密码
                    database=self.database_dict['database']
                )
                end = time.time()
                # 5秒超时
                if end - start > 5:
                    raise Exception
                print("Connected to remote mysql successfully...")
            except Exception as e:
                print("Try to connecting to remote mysql but timeout occurs...", e)
                self.conn = sqlite.connect("filtered_cks.db")
                print("Connected to local sqlite successfully...")
        else:
            self.conn = sqlite.connect("filtered_cks.db")
            print("Connected to local sqlite successfully...")
        self.c = self.conn.cursor()
        return self.conn

    def createTable(self):
        if self.table_type == 'cookie':
            # 时间戳；ck；日期；优先级；权重（拟运行次数）
            self.c.execute(f'''CREATE TABLE IF NOT EXISTS {self.table_name}
                            (TIMESTAMP REAL PRIMARY KEY NOT NULL, 
                            USER_NAME TEXT NOT NULL, 
                            DATE TEXT NOT NULL, 
                            PRIORITY INT NOT NULL,
                            TIMES INT NOT NULL DEFAULT 0);
                            ''')
            self.conn.commit()
        elif self.table_type == 'log':
            self.c.execute(f'''CREATE TABLE IF NOT EXISTS {self.table_name}
                            (TIMESTAMP REAL PRIMARY KEY NOT NULL, 
                            LOG TEXT NOT NULL,
                            TIMES INT NOT NULL);
                            ''')
            self.conn.commit()

        else:
            print("ERROR in 'table_type'!")
            return

        print(f"Table {self.table_name} has been created.")

    def deleteTable(self):
        self.c.execute(f"DROP TABLE {self.table_name};")
        self.conn.commit()
        print(f"Table {self.table_name} has been deleted.")

    def insertItem(self, user_name, timestamp, year_month_day, priority):
        if self.findUserName(user_name, year_month_day):
            print(f"{getUserName(user_name)} is in Table {self.table_name}. Updating...")
            self.updateItem(user_name, timestamp, year_month_day, priority)
            return
        self.c.execute(f'''INSERT INTO {self.table_name} (USER_NAME, TIMESTAMP, DATE, PRIORITY)
                            VALUES ('{user_name}', {timestamp}, '{year_month_day}', {priority})''')
        self.conn.commit()
        print(f"Item {getUserName(user_name)} has been inserted into Table {self.table_name}.")

    def addTimes(self, user_name, year_month_day=str(datetime.date.today())):
        if not self.findUserName(user_name, year_month_day):
            print(f"Error in updating: No item found...")
            return
        self.c.execute(f'''
                        UPDATE {self.table_name} set 
                        TIMES = TIMES + 1
                        WHERE USER_NAME LIKE '%{getUserName(user_name)}%' AND DATE = '{year_month_day}'
                        ''')
        self.conn.commit()
        print(f"Item {getUserName(user_name)}'s times have been added in Table {self.table_name}.")

    def updateItem(self, user_name, timestamp, year_month_day, priority):
        if not self.findUserName(user_name, year_month_day):
            print(f"Error in updating: No item found...")
            return
        # 时间戳为primary key，不更新，ck动态更新，因为会失效
        # 优先级大于0时可以更新，但只更新权重
        if priority > 0:
            self.c.execute(f'''
                            UPDATE {self.table_name} SET 
                            USER_NAME='{user_name}',
                            DATE='{year_month_day}'
                            WHERE USER_NAME LIKE '%{getUserName(user_name)}%' AND PRIORITY > 0 AND DATE = '{year_month_day}'
                            ''')
            print(
                f"Item {getUserName(user_name)} has been updated for USER_NAME (with cookie). The weight is not updated.")
        else:
            # 小于或者等于0时全部更新
            self.c.execute(f'''
                            UPDATE {self.table_name} SET 
                            USER_NAME='{user_name}',
                            DATE='{year_month_day}',
                            PRIORITY={priority}
                            WHERE USER_NAME LIKE '%{getUserName(user_name)}%' AND PRIORITY > 0 AND DATE = '{year_month_day}'
                            ''')
            print(f"Item {getUserName(user_name)}:{priority} has been updated in Table {self.table_name}.")
        self.conn.commit()

    def updateItem_ALLCK(self, user_name, timestamp, year_month_day, priority):
        if not self.findUserName(user_name, year_month_day):
            print(f"Error in updating: No item found...")
            return

        # 只将数值更新为权重比较高的值和权重小于或等于0的值。
        self.c.execute(f'''
                        SELECT PRIORITY FROM {self.table_name} 
                        WHERE USER_NAME LIKE '%{getUserName(user_name)}%' AND PRIORITY > 0 AND DATE = '{year_month_day}'
                        ''')
        old_priority = int(self.c.fetchone()[0])
        # 更新权重条件：1. 当前权重大于0（未领到券且当前账号不火爆）；2. 在1的基础上，需要更新的权重小于等于0（抢到券或火爆）或权重大于旧权重（更新为更高的权重）
        if old_priority > 0 and (old_priority < priority or priority <= 0):
            # if self.c.fetchone()[0] < priority or priority <= 0:
            self.c.execute(f'''
                            UPDATE {self.table_name} SET 
                            USER_NAME='{user_name}',
                            DATE='{year_month_day}',
                            PRIORITY={priority}
                            WHERE USER_NAME LIKE '%{getUserName(user_name)}%' AND PRIORITY > 0 AND DATE = '{year_month_day}'
                            ''')
            print(f"Item {getUserName(user_name)}:{priority} has been updated in Table {self.table_name}.")
        else:
            # 权重更小，且权重大于0，则不更新权重，只更新数值。
            self.c.execute(f'''
                UPDATE {self.table_name} SET 
                USER_NAME='{user_name}',
                DATE='{year_month_day}'
                WHERE USER_NAME LIKE '%{getUserName(user_name)}%' AND PRIORITY > 0 AND DATE = '{year_month_day}'
                ''')
            print(
                f"Item {getUserName(user_name)} has been updated for USER_NAME (with cookie). The weight is not updated.")

    def filterUsers(self, user_number, year_month_day=str(datetime.date.today())):
        self.c.execute(f'''
                        SELECT USER_NAME, TIMES FROM {self.table_name} WHERE PRIORITY > -1 AND DATE = '{year_month_day}' ORDER BY PRIORITY DESC;
                        ''')
        p = self.c.fetchall()
        users, times = [], []
        for x in p:
            users.append(x[0])
            times.append(x[1])
        # users, times = [x[0] for x in p], [x[-1] for x in p]
        return users[:min(len(users), user_number)], times[:min(len(times), user_number)]

    # 优先选择前priority_number个用户。超过priority_number时，再逐次捕获
    # 前priority_number个号优先级相同，全部抢完后才执行后面账号，后面先按照之前版本的权重排序，每次获取user_number个ck
    def filterUsersWithPriorityLimited(self, user_number=2, year_month_day=str(datetime.date.today()),
                                       priority_number=4):
        # 为-1的都是优先级较高且抢到的
        self.c.execute(f'''
                        SELECT COUNT(*) FROM {self.table_name} WHERE PRIORITY = -1 AND DATE = '{year_month_day}' ORDER BY PRIORITY DESC;
                        ''')
        had_number = self.c.fetchone()[0]
        # 已经抢到的数量小于预设的数量，需要加载其中尚未抢到的
        if had_number < priority_number:
            user_number = priority_number - had_number
        # 超过priority_number后，根据权重选择user_number个数据进行计算。
        self.c.execute(f'''
                        SELECT USER_NAME, TIMES FROM {self.table_name} WHERE PRIORITY > -1 AND DATE = '{year_month_day}' ORDER BY PRIORITY DESC;
                        ''')
        p = self.c.fetchall()
        users, times = [], []
        for x in p:
            users.append(x[0])
        times.append(x[1])
        # users, times = [x[0] for x in p], [x[-1] for x in p]
        return users[:min(len(users), user_number)], times[:min(len(times), user_number)]

    def findUserName(self, user_name, year_month_day=str(datetime.date.today())):
        p = self.c.execute(f'''
                        SELECT count(*) from {self.table_name} WHERE USER_NAME LIKE '%{getUserName(user_name)}%' AND DATE = '{year_month_day}'
                        ''')
        return self.c.fetchone()[0] != 0

    def logsNumber(self):
        if self.table_type != 'log': return -1
        self.c.execute(f'''
                SELECT COUNT(*) from {self.table_name}
                ''')
        return self.c.fetchone()[0]

    def printAllLogs(self):
        self.printLogs(0x7fffffff)

    def printLogs(self, log_num=10):
        if self.table_type != 'log': return
        self.c.execute(f"SELECT * FROM {self.table_name} LIMIT {log_num}")
        for item in self.c.fetchall():
            print(f"{item[1] if len(item[1]) < 30 else item[1][::50][::-1][:50]}\t{item[2]}")

    def printTodayItems(self):
        self.printAllItems(str(datetime.date.today()))

    def printAllItems(self, year_month_day=None):
        if year_month_day is None:
            print(f"{'user_name'.ljust(17, ' ')}{'date'.ljust(12, ' ')}prio  times")
            self.c.execute(f"SELECT * FROM {self.table_name}")
            for item in self.c.fetchall():
                print(f"{getUserName(item[1]).ljust(17, ' ')}{item[2]}  {str(item[3]).ljust(6, ' ')}{item[4]}")
        else:
            print(f"{'user_name'.ljust(17, ' ')}{'date'.ljust(12, ' ')}prio  times")
            self.c.execute(f"SELECT * FROM {self.table_name} WHERE DATE = '{year_month_day}'")
            for item in self.c.fetchall():
                print(f"{getUserName(item[1]).ljust(17, ' ')}{item[2]}  {str(item[3]).ljust(6, ' ')}{item[4]}")

    def getAllUsers(self, year_month_day=str(datetime.date.today())):
        res = []
        for item in self.c.execute(f"SELECT USER_NAME from {self.table_name} WHERE DATE = '{year_month_day}'"):
            res.append(item[0])
        return res

    def close(self):
        self.conn.close()


def printT(s):
    print("[{0}]: {1}".format(datetime.datetime.now(), s), flush=True)
    # print("[{0}]: {1}".format(datetime.datetime.now(), s))
    sys.stdout.flush()


def getSignAPI(functionId, body):
    sign_api = 'http://jd19.top:1998/newlog?func=getsign'
    Token = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJleHAiOjE2NTM1NDQ2MDksImlhdCI6MTY1MjMzNTAwOSwiaXNzIjoiYmlsaWJpbGkifQ.BeYPUnXcEAMWPNdsPNGUbZ4Ms4HlJSTByqRkkzKaIvA'
    headers = {
        'Accept': '*/*',
        # "accept-encoding": "gzip, deflate, br",
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + Token
    }
    data = {
        'functionId': functionId,
        'body': body
    }
    try:
        res = requests.post(url=sign_api, headers=headers, json=data, timeout=30).json()
        if res['code'] == 200:
            return res['data']
        else:
            print(res['msg'])
            return -1
    except:
        return -1


# 产生随机子串
def randomString(e, flag=False):
    t = "0123456789abcdef"
    if flag: t = t.upper()
    n = [random.choice(t) for _ in range(e)]
    return ''.join(n)


# 59-20券的receiveKey
def getCcFeedInfo(cookie, receive_dict):
    re_body = re.compile(r'body=.*?&')
    body = {
        "categoryId": 118,
        "childActivityUrl": "openapp.jdmobile://virtual?params={\"category\":\"jump\",\"des\":\"couponCenter\"}",
        "eid": randomString(16),
        "globalLat": "",
        "globalLng": "",
        "lat": "",
        "lng": "",
        "monitorRefer": "appClient",
        "monitorSource": "ccfeed_android_index_feed",
        "pageClickKey": "Coupons_GetCenter",
        "pageNum": 1,
        "pageSize": 20,
        "shshshfpb": ""
    }
    res = getSignAPI('getCcFeedInfo', body)  # st sv sign
    if res == -1:
        return -1
    else:
        # print(res)
        params = res['sign']
        functionId = res['fn']
        body = re_body.findall(params)[0]
        params = params.replace(body, '')
        url = f'https://api.m.jd.com?functionId={functionId}&' + params
        # print(url)
        headers = {
            "Host": "api.m.jd.com",
            "cookie": cookie,
            "charset": "UTF-8",
            "user-agent": "okhttp/3.12.1;jdmall;android;version/10.1.4;build/90060;screen/720x1464;os/7.1.2;network/wifi;",
            "accept-encoding": "br,gzip,deflate",
            "cache-control": "no-cache",
            "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
            "content-length": str(len(body)),
        }
        res = requests.post(url=url, headers=headers, data=body, timeout=30).json()
        # print(res)
        if res['code'] == '0':
            # return res['result']['couponList'][0]['receiveKey']
            for coupon in res['result']['couponList']:
                if coupon['title'] != None and '每周可领一次' in coupon['title']:
                    receiveKey = coupon['receiveKey']
                    receive_dict[cookie] = receiveKey
                    return receiveKey
            print('没有找到59-20券的receiveKey')
            receive_dict[cookie] = ""
            return -1
        else:
            print('获取59-20券的receiveKey失败')
            receive_dict[cookie] = ""
            return -1


def getUserName(cookie):
    try:
        r = re.compile(r"pt_pin=(.*?);")  # 指定一个规则：查找pt_pin=与;之前的所有字符,但pt_pin=与;不复制。r"" 的作用是去除转义字符.
        userName = r.findall(cookie)  # 查找pt_pin=与;之前的所有字符，并复制给r，其中pt_pin=与;不复制。
        # print (userName)
        userName = unquote(userName[0])  # r.findall(cookie)赋值是list列表，这个赋值为字符串
        # print(userName)
        return userName
    except Exception as e:
        print(e, "cookie格式有误！")
        exit(2)


# 获取sign
def getReceiveNecklaceCouponSign(receive_key):
    re_body = re.compile(r'body=.*?&')
    body = {"channel": "领券中心",
            "childActivityUrl": "openapp.jdmobile://virtual?params={\"category\":\"jump\",\"des\":\"couponCenter\"}",
            "couponSource": "manual",
            "couponSourceDetail": None,
            "eid": randomString(16),
            "extend": receive_key,
            "lat": "",
            "lng": "",
            "pageClickKey": "Coupons_GetCenter",
            "rcType": "4",
            "riskFlag": 1,
            "shshshfpb": "",
            "source": "couponCenter_app",
            "subChannel": "feeds流"
            }
    # res = get_sign_api('newReceiveRvcCoupon', body) # 领券
    res = getSignAPI('receiveNecklaceCoupon', body)  # 59-20
    if res == -1:
        return ('', '')
    else:
        params = res['sign']
        functionId = res['fn']
        body = re_body.findall(params)[0]
        params = params.replace(body, '')
        url = f'https://api.m.jd.com?functionId={functionId}&' + params
        # return [url, body]
        return (url, body)


def receiveNecklaceCouponWithLoop(cookies, api_dict, loop_times, mask_dict, process_id=0, process_number=1):
    headers = {
        "Host": "api.m.jd.com",
        "cookie": '',
        "charset": "UTF-8",
        "user-agent": "okhttp/3.12.1;jdmall;android;version/10.1.4;build/90060;screen/720x1464;os/7.1.2;network/wifi;",
        "accept-encoding": "br,gzip,deflate",
        "cache-control": "no-cache",
        "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
        "content-length": '',
    }
    for t in range(loop_times):
        for cookie in cookies:
            url, body = api_dict[cookie][process_id][t]
            headers["cookie"] = cookie
            headers["content-length"] = str(len(body))
            prefix_info = f"User: {getUserName(cookie)}, process: {process_id + 1}/{process_number}, loop: {t + 1}/{loop_times}: "
            target_info = ""
            res = requests.post(url=url, headers=headers, data=body).json()
            try:
                if res['code'] == '0' and res['msg'] == '响应成功':
                    if res['result']['optCode'] == '9000':
                        desc = res['result']['desc']
                        quota = res['result']['couponInfoList'][0]['quota']
                        discount = res['result']['couponInfoList'][0]['discount']
                        endTime = res['result']['couponInfoList'][0]['endTime']
                        timeStamp = int(endTime) / 1000
                        timeArray = time.localtime(timeStamp)
                        otherStyleTime = time.strftime("%Y-%m-%d", timeArray)
                        target_info = f'{desc}，满{quota}减{discount}({otherStyleTime}过期)'
                    else:
                        target_info = res['result']['desc']
                else:
                    target_info = res['msg']
                printT(prefix_info + target_info)
            except:
                pass
            if "已经兑换过" in target_info:
                mask_dict[cookie] = -1
            elif "不足" in target_info:
                mask_dict[cookie] = 0
            elif "未登录" in target_info:
                mask_dict[cookie] = -2


def receiveNecklaceCoupon(url, body, cookie, loop_times=1, process_id=0, process_number=1):
    headers = {
        "Host": "api.m.jd.com",
        "cookie": cookie,
        "charset": "UTF-8",
        "user-agent": "okhttp/3.12.1;jdmall;android;version/10.1.4;build/90060;screen/720x1464;os/7.1.2;network/wifi;",
        "accept-encoding": "br,gzip,deflate",
        "cache-control": "no-cache",
        "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
        "content-length": str(len(body)),
    }
    for t in range(loop_times):
        headers["cookie"] = cookie
        prefix_info = f"User: {getUserName(cookie)}, process: {process_id + 1}/{process_number}, loop: {t + 1}/{loop_times}："
        res = requests.post(url=url, headers=headers, data=body).json()
        try:
            if res['code'] == '0' and res['msg'] == '响应成功':
                if res['result']['optCode'] == '9000':
                    desc = res['result']['desc']
                    quota = res['result']['couponInfoList'][0]['quota']
                    discount = res['result']['couponInfoList'][0]['discount']
                    endTime = res['result']['couponInfoList'][0]['endTime']
                    timeStamp = int(endTime) / 1000
                    timeArray = time.localtime(timeStamp)
                    otherStyleTime = time.strftime("%Y-%m-%d", timeArray)
                    printT(prefix_info + f'{desc}，满{quota}减{discount}({otherStyleTime}过期)')
                else:
                    printT(prefix_info + res['result']['desc'])
            else:
                printT(prefix_info + res['msg'])
        except:
            pass


# jd的服务器时间
def jdTime():
    url = 'http://api.m.jd.com/client.action?functionId=queryMaterialProducts&client=wh5'
    headers = {
        "user-agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36'
    }
    try:
        res = requests.get(url=url, headers=headers, timeout=1).json()
        return int(res['currentTime2'])
    except:
        return 0


def exchange(batch_size=4, waiting_delta=0.26, process_number=4):

    is_debug = False

    printT("Starting..." + (" (Debug Mode)" if is_debug else ""))

    # 每个cookie的receiveKey不一样
    cookies = os.environ["JD_COOKIE"].split('&') if "JD_COOKIE" in os.environ else []

    # get cookies from databse
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
    # 存入数据库
    database = SQLProcess("cks_59_20_1" + time.strftime("%Y%W"), database_dict)
    # 插入所有数据，如果存在则更新
    insert_start = time.time()
    today_week_str = time.strftime("%Y-(%W) ")
    for i, ck in enumerate(cookies):
        database.insertItem(ck, time.time(), today_week_str, len(cookies) - i)
    insert_end = time.time()
    print("\nTime for updating/inserting into database：{:.2f}s\n".format(insert_end - insert_start))

    print('\nDatabase before updating：')
    database.printAllItems()

    cookies, visit_times = database.filterUsers(user_number=batch_size, year_month_day=today_week_str)
    cookies = cookies[:min(len(cookies), batch_size)]
    print("\nAccount ready to run：")
    print("\n".join([getUserName(ck) for ck in cookies]), '\n')

    # get receive key
    print()
    printT(f'Generating receive key for {len(cookies)} cookies...')
    receive_key_dict = multiprocessing.Manager().dict()
    pool = multiprocessing.Pool(processes=len(cookies))
    for i in range(len(cookies)):
        pool.apply_async(getCcFeedInfo, args=(cookies[i], receive_key_dict,))
    pool.close()
    pool.join()

    # filter invalid receive key
    filtered_cookies = []
    for key, value in receive_key_dict.items():
        if len(value):
            filtered_cookies.append(key)
    printT(
        f"{len(cookies)} receive keys have been generated. {len(cookies) - len(filtered_cookies)} invalid receive keys have been filtered...")
    cookies = filtered_cookies

    # the api_dict is a dict of item, each of which includes 'url' and 'body'
    loop_time = 1
    # process_number = 4
    api_number_for_each_cookie = loop_time * process_number
    printT(
        f"Generating {len(cookies) * api_number_for_each_cookie} api links ({len(cookies)} cookies, {process_number} processes, and {loop_time} times)...")
    api_dict = {}
    for cookie in cookies:
        # get url and body for each receive with api_number_for each_cookie times
        api_dict[cookie] = []
        for p_id in range(process_number):
            buffer = []
            for t in range(loop_time):
                buffer.append(getReceiveNecklaceCouponSign(receive_key=receive_key_dict[cookie]))
            api_dict[cookie].append(buffer)

    printT('Ready for coupons...')
    jd_timestamp = datetime.datetime.fromtimestamp(jdTime() / 1000)

    printT(f"Server delay (JD server - current server): {(jd_timestamp - datetime.datetime.now()).total_seconds()}s.")
    # Debug: 测试时关闭
    if not is_debug:
        nex_hour = (jd_timestamp + datetime.timedelta(hours=1)).replace(minute=0, second=0, microsecond=0)
    else:
        nex_hour = (jd_timestamp + datetime.timedelta(minutes=1)).replace(second=0, microsecond=0)
    waiting_time = (nex_hour - jd_timestamp).total_seconds()
    printT(f"Waiting {waiting_time}s...")
    # waiting_delta = 0.26
    time.sleep(max(waiting_time - waiting_delta, 0))

    mask_dict = multiprocessing.Manager().dict()
    for ck in cookies:
        mask_dict[ck] = 1
    # receiveNecklaceCouponWithLoop(cookies, api_dict, loop_time, 0, process_number)
    pool = multiprocessing.Pool(processes=process_number)
    for i in range(process_number):
        cookies.insert(0, cookies.pop())
        pool.apply_async(receiveNecklaceCouponWithLoop, args=(cookies.copy(), api_dict, loop_time, mask_dict, i, process_number, ))
        time.sleep(0.03)
    pool.close()
    pool.join()

    # update database
    print()
    # 将为False的ck更新为负值
    for ck, state in mask_dict.items():
        if state <= 0:
            database.insertItem(ck, time.time(), today_week_str, state)
        # else:
            # 当前尚未抢到时，次数+1，state为0时说明不足，不自增
        database.addTimes(ck, today_week_str)

    print()
    # 将为False的ck更新为负值
    for ck, state in mask_dict.items():
        if state == -1:
            print(f"User: {getUserName(ck)} 抢到优惠券")
        elif state == 0:
            print(f"User: {getUserName(ck)} 点点券不足")
        elif state == 0:
            print(f"User: {getUserName(ck)} ck过期")

    print('\nDatabase after updating：')
    database.printAllItems()
    database.close()

    printT("Ending...")


# Debug: 测试时延迟很高
# Each cookie holds only one process.
def exchangeV2(batch_size=4, waiting_delta=0.26):
    is_debug = False

    printT("Starting...")

    # 每个cookie的receiveKey不一样
    cookies = os.environ["JD_COOKIE"].split('&') if "JD_COOKIE" in os.environ else []
    cookies = cookies[:min(len(cookies), batch_size)]

    # get receive key
    printT(f'Generating receive key for {len(cookies)} cookies...')
    receive_key_dict = multiprocessing.Manager().dict()
    pool = multiprocessing.Pool(processes=len(cookies))
    for i in range(len(cookies)):
        pool.apply_async(getCcFeedInfo, args=(cookies[i], receive_key_dict,))
    pool.close()
    pool.join()

    # filter invalid receive key
    filtered_cookies = []
    for key, value in receive_key_dict.items():
        if len(value):
            filtered_cookies.append(key)
    printT(
        f"{len(cookies)} receive keys have been generated. {len(cookies) - len(filtered_cookies)} invalid receive keys have been filtered...")
    cookies = filtered_cookies

    # the api_dict is a dict of item, each of which includes 'url' and 'body'
    loop_time = 2
    process_number = len(cookies)
    printT(
        f"Generating {process_number * loop_time} api links, each cookie is posted by one process with {loop_time} times...")
    api_dict = {}
    for cookie in cookies:
        # get url and body for each receive with api_number_for each_cookie times
        api_dict[cookie] = []
        for t in range(loop_time):
            api_dict[cookie].append(getReceiveNecklaceCouponSign(receive_key=receive_key_dict[cookie]))

    printT('Ready for coupons...')
    jd_timestamp = datetime.datetime.fromtimestamp(jdTime() / 1000)
    printT(f"Server delay (JD server - current server): {(jd_timestamp - datetime.datetime.now()).total_seconds()}s.")
    if not is_debug:
        nex_hour = (jd_timestamp + datetime.timedelta(hours=1)).replace(minute=0, second=0, microsecond=0)
    else:
        nex_hour = (jd_timestamp + datetime.timedelta(minutes=1)).replace(second=0, microsecond=0)
    waiting_time = (nex_hour - jd_timestamp).total_seconds()
    printT(f"Waiting {waiting_time}s...")
    # waiting_delta = 0.26
    time.sleep(max(waiting_time - waiting_delta, 0))

    # receiveNecklaceCouponWithLoop(cookies, api_dict, loop_time, 0, process_number)
    pool = multiprocessing.Pool(processes=process_number)
    random.shuffle(cookies)
    for i in range(process_number):
        # defaulted as loop_times post using 1 api
        url, body = api_dict[cookies[i]][0]
        pool.apply_async(receiveNecklaceCoupon(url, body, cookies[i], loop_times=loop_time, process_id=i,
                                               process_number=process_number))
        time.sleep(0.025)
    pool.close()
    pool.join()

    printT("Ending...")


if __name__ == '__main__':
    # freeze_support()
    # exchangeV2(batch_size=3, waiting_delta=0.23)
    exchange(batch_size=3, waiting_delta=0.23, process_number=4)