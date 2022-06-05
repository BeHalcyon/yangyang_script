#!/bin/env python3
# -*- coding: utf-8 -*
'''
项目名称:yangyang_59_20_1.py
Author: Fisher
功能：
Date: 2022-5-12
cron: 0 59 9,13,17,21,23 * * *
'''

import time, datetime
import requests, re, json
from urllib.parse import quote, unquote
import threading
import multiprocessing
import random
import sqlite3 as sqlite
import os
import sys


def getUserName(cookie):
    try:
        r = re.compile(r"pt_pin=(.*?);")  # 指定一个规则：查找pt_pin=与;之前的所有字符,但pt_pin=与;不复制。r"" 的作用是去除转义字符.
        userName = r.findall(cookie)  # 查找pt_pin=与;之前的所有字符，并复制给r，其中pt_pin=与;不复制。
        # print (userName)
        userName = unquote(userName[0])  # r.findall(cookie)赋值是list列表，这个赋值为字符串
        # print(userName)
        return userName
    except Exception as e:
        # print(e, "cookie格式有误！")
        r = re.compile(r"pin=(.*?);")  # 指定一个规则：查找pt_pin=与;之前的所有字符,但pt_pin=与;不复制。r"" 的作用是去除转义字符.
        userName = r.findall(cookie)  # 查找pt_pin=与;之前的所有字符，并复制给r，其中pt_pin=与;不复制。
        # print (userName)
        userName = unquote(userName[0])  # r.findall(cookie)赋值是list列表，这个赋值为字符串
        # print(userName)
        return userName


def printT(s):
    print("[{0}]: {1}".format(datetime.datetime.now(), s), flush=True)
    sys.stdout.flush()


def sendNotification(summary, content):
    if "WXPUSHER_APP_TOKEN" in os.environ and "WXPUSHER_UID" in os.environ:
        url = "http://wxpusher.zjiecode.com/api/send/message"
        body = {
            "appToken": os.environ["WXPUSHER_APP_TOKEN"],
            "content": content,
            "summary": summary,
            # "contentType": 1,
            # "topicIds": [
            #     123
            # ],
            "uids": [
                os.environ["WXPUSHER_UID"]
            ],
        }
        try:
            res = requests.post(url, json=body).json()
            if 'code' in res and res['code'] == 1000:
                printT("WxPusher: Message send successfully.")
        except Exception as e:
            printT(f"WxPusher: Message send failed: {e}")
    else:
        printT(f"WxPusher: Message send failed: Please configure environments (WXPUSHER_APP_TOKEN and WXPUSHER_UID).")


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
        # 等于0的也更新
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
        return self.printAllItems(str(datetime.date.today()))

    def printAllItems(self, year_month_day=None):
        res = ""
        if year_month_day is None:
            print(f"{'user_name'.ljust(17, ' ')}{'date'.ljust(12, ' ')}prio  times")
            res += f"{'user_name'.ljust(17, ' ')}{'date'.ljust(12, ' ')}prio  times\n"
            self.c.execute(f"SELECT * FROM {self.table_name}")
            for item in self.c.fetchall():
                print(f"{getUserName(item[1]).ljust(17, ' ')}{item[2]}  {str(item[3]).ljust(6, ' ')}{item[4]}")
                if int(item[3]) == -1:
                    res += f"{getUserName(item[1]).ljust(17, ' ')}{item[2]}  {str(item[3]).ljust(6, ' ')}{item[4]}\n"
        else:
            print(f"{'user_name'.ljust(17, ' ')}{'date'.ljust(12, ' ')}prio  times")
            res += f"{'user_name'.ljust(17, ' ')}{'date'.ljust(12, ' ')}prio  times\n"
            self.c.execute(f"SELECT * FROM {self.table_name} WHERE DATE = '{year_month_day}'")
            for item in self.c.fetchall():
                print(f"{getUserName(item[1]).ljust(17, ' ')}{item[2]}  {str(item[3]).ljust(6, ' ')}{item[4]}")
                res += f"{getUserName(item[1]).ljust(17, ' ')}{item[2]}  {str(item[3]).ljust(6, ' ')}{item[4]}\n"
        return res

    def getAllUsers(self, year_month_day=str(datetime.date.today())):
        res = []
        for item in self.c.execute(f"SELECT USER_NAME from {self.table_name} WHERE DATE = '{year_month_day}'"):
            res.append(item[0])
        return res

    def close(self):
        self.conn.close()


def getSignAPIWithEncrypt(functionId, body, user_agent, pin):
    if "JD_SIGN_API" in os.environ and "JD_SIGN_API_TOKEN" in os.environ:
        url = os.environ['JD_SIGN_API']
        token = os.environ['JD_SIGN_API_TOKEN']
        data = {'functionId': functionId,
                'body': json.dumps(body),
                'user_agent': user_agent,
                'pin': pin,
                'token': token
                }
        try:
            res = requests.post(url, data=data).json()
            if 'body' not in res:
                print("No sign found. Please check the interface.")
                exit()
            return res
        except Exception as e:
            print(e)
            exit()
    else:
        print("Please set environ first!")
        exit()


def randomString(e, flag=False):
    t = "0123456789abcdef"
    if flag: t = t.upper()
    n = [random.choice(t) for _ in range(e)]
    return ''.join(n)


# 59-20券的receiveKey
def getCcFeedInfo(cookie, receive_dict):
    # re_body = re.compile(r'body=.*?&')
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

    # res = getSignAPIWithEncrypt('getCcFeedInfo', body, "", "")
    res = getSignAPIWithEncrypt('getCcFeedInfo', body, "", "")

    if res == -1:
        return -1
    else:
        result = res['body']

        functionId = result['functionId']
        del result['functionId']

        # if 'ep_encrypt_uuid' in result:
        #     del result['ep_encrypt_uuid']

        # rsbody = json.loads(json.dumps(result['body']))
        # url = f'https://api.m.jd.com?functionId={functionId}&body=' + rsbody
        url = f'https://api.m.jd.com?functionId={functionId}'

        headers = {
            "Host": "api.m.jd.com",
            "cookie": cookie,
            "charset": "UTF-8",
            "user-agent": user_agent,
            # "user-agent": "okhttp/3.12.1;jdmall;android;version/10.1.4;build/90060;screen/720x1464;os/7.1.2;network/wifi;",
            "accept-encoding": "br,gzip,deflate",
            "cache-control": "no-cache",
            "content-type": "application/x-www-form-urlencoded;charset=UTF-8",
            "content-length": str(len(result))
        }


        res = requests.post(url=url, headers=headers, data=result, timeout=30).json()

        if res['code'] == '0':
            if 'result' in res and 'couponList' in res['result']:
                for coupon in res['result']['couponList']:
                    if coupon['title'] != None and '每周可领一次' in coupon['title']:
                        receiveKey = coupon['receiveKey']
                        receive_dict[cookie] = receiveKey
                        return receiveKey

            printT(f'User: {getUserName(cookie)}, cannot find the receive key for coupon 59-20!')
            receive_dict[cookie] = ""
            return -1
        else:
            # print('获取59-20券的receiveKey失败')
            printT(f'User: {getUserName(cookie)}, fail to get the receive key for coupon 59-20!')
            receive_dict[cookie] = ""
            return -1


# 获取sign
def getReceiveNecklaceCouponSign(receive_key, cookie):
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

    res = getSignAPIWithEncrypt('receiveNecklaceCoupon', body, user_agent, getUserName(cookie))  # 59-20
    if res == -1:
        return ('', '')
    else:

        url = f"https://api.m.jd.com?functionId={res['body']['functionId']}"
        return (url, res)


def receiveNecklaceCouponThread(cookie, api_para, mask_dict, thread_id=0, thread_number=1):
    url, parameters = api_para

    _headers = parameters['headers']

    headers = {"Host": "api.m.jd.com",
               "cookie": cookie,
               "charset": "UTF-8",
               "user-agent": user_agent,
               "accept-encoding": "br,gzip,deflate",
               "cache-control": "no-cache",
               "content-type": "application/x-www-form-urlencoded;charset=UTF-8;",
               "content-length": "",
               "j-e-h": json.dumps({
                   "hdid": "JM9F1ywUPwflvMIpYPok0tt5k9kW4ArJEU3lfLhxBqw=",
                   "ridx": -1,
                   "ts": int(round(time.time() * 1000)),
                   "cipher": {
                       "user-agent": _headers['jeh_encrypt_user_agent']
                   },
                   "ciphertype": 5,
                   "version": "1.2.0",
                   "appname": "com.jingdong.app.mall"
               }).replace(" ", ""),
               "j-e-c": json.dumps({
                   "hdid": "JM9F1ywUPwflvMIpYPok0tt5k9kW4ArJEU3lfLhxBqw=",
                   "ridx": -1,
                   "ts": int(round(time.time() * 1000)),
                   "cipher": {
                       "pin": _headers['jec_encrypt_pin']
                   },
                   "ciphertype": 5,
                   "version": "1.2.0",
                   "appname": "com.jingdong.app.mall"
               }).replace(" ", "")
               }

    body = parameters['body']
    if "encrypt_uuid" in body:
        body['ep'] = quote(json.dumps({
            "hdid": "JM9F1ywUPwflvMIpYPok0tt5k9kW4ArJEU3lfLhxBqw=",
            "ridx": -1,
            "ts": ts_time,
            "cipher": {
                "area": "D181CNTpCzU3DJTpCzU4DtK=",
                "d_model": "JUu2",
                "wifiBssid": "dW5hbw93bq==",
                "osVersion": "EG==",
                "d_brand": "WQvrb21f",
                "screen": "CJuyCMenCNqm",
                "uuid": body["encrypt_uuid"]
            },
            "ciphertype": 5,
            "version": "1.2.0",
            "appname": "com.jingdong.app.mall"

        }).replace(" ", ""))
        del body['encrypt_uuid']

    headers["content-length"] = str(len(body))
    prefix_info = f"Process: {thread_id + 1}/{thread_number}, User: {getUserName(cookie)}, "
    target_info = ""
    res = requests.post(url=url, headers=headers, data=body).json()

    try:
        if res['code'] == '0' and res['msg'] == '响应成功':
            target_info = res['result']['desc']
        else:
            target_info = res['msg']
        printT(prefix_info + target_info)
    except:
        pass
    if "已经兑换过" in target_info or "太贪心" in target_info:
        mask_dict[cookie] = -1
    elif "不足" in target_info:
        mask_dict[cookie] = 0
    elif "未登录" in target_info:
        # Debug 修改未登录的优先级为0
        mask_dict[cookie] = 0


def jdTime():
    url = 'http://api.m.jd.com/client.action?functionId=queryMaterialProducts&client=wh5'
    headers = {
        "user-agent": user_agent
    }
    try:
        res = requests.get(url=url, headers=headers, timeout=1).json()
        return int(res['currentTime2'])
    except:
        return 0


# 多线程，每个线程负责一个号
def exchangeV4(batch_size=4, waiting_delta=0.26, thread_number=12, sleep_time=0.03, coupon_type="59-20"):
    # TODO DEBUG
    is_debug = 'DEBUG_59_20' in os.environ and os.environ['DEBUG_59_20'] == 'True'

    printT("Starting..." + (" (Debug Mode)" if is_debug else ""))

    # 每个cookie的receiveKey不一样
    cookies = os.environ["JD_COOKIE"].split('&') if "JD_COOKIE" in os.environ else []

    # get cookies from databse
    database_dict = {
        'type': 'sqlite',
        'name': "filtered_cks.db"
    }
    # 存入本地数据库
    database = SQLProcess("ck6_59_20_" + time.strftime("%Y%W"), database_dict)
    # 插入所有数据，如果存在则更新
    insert_start = time.time()
    today_week_str = time.strftime("%Y-(%W) ")
    for i, ck in enumerate(cookies):
        database.insertItem(ck, time.time(), today_week_str, len(cookies) - i)
    insert_end = time.time()
    print("\nTime for updating/inserting into database：{:.2f}s\n".format(insert_end - insert_start))

    print('\nDatabase before updating：')
    database.printAllItems()

    # Debug 部署时修改
    cookies, visit_times = database.filterUsers(user_number=batch_size, year_month_day=today_week_str)
    cookies = cookies[:min(len(cookies), batch_size)]
    random.shuffle(cookies)

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
    if len(cookies) == 0:
        printT("No avaliable cookie. Exiting...")
        return

    # the api_dict is a dict of item, each of which includes 'url' and 'body'

    printT(
        f"Generating {len(cookies)} api links ({len(cookies)} cookies, {thread_number} threads, and {1} times)...")

    thread_api_arrays = []

    for t in range(thread_number):
        thread_api_arrays.append((cookies[t % len(cookies)], getReceiveNecklaceCouponSign(
            receive_key=receive_key_dict[cookies[t % len(cookies)]],
            cookie=cookies[t % len(cookies)])))

    threads = []
    mask_dict = {}
    for ck in cookies:
        mask_dict[ck] = 1
    for i in range(len(thread_api_arrays)):
        cookie, api_para = thread_api_arrays[i]
        threads.append(
            threading.Thread(target=receiveNecklaceCouponThread,
                             args=(cookie, api_para, mask_dict, i, len(thread_api_arrays)))
        )

    printT('Ready for coupons...')
    jd_timestamp = datetime.datetime.fromtimestamp(jdTime() / 1000)
    server_delta = (jd_timestamp - datetime.datetime.now()).total_seconds()
    printT(f"Server delay (JD server - current server): {server_delta}s.")

    if not is_debug:
        nex_hour = (jd_timestamp + datetime.timedelta(hours=1)).replace(minute=0, second=0, microsecond=0)
    else:
        nex_hour = (jd_timestamp + datetime.timedelta(minutes=1)).replace(second=0, microsecond=0)
    waiting_time = (nex_hour - jd_timestamp).total_seconds()
    printT(f"Waiting {waiting_time}s...")
    # waiting_delta = 0.26
    # time.sleep(max(waiting_time - waiting_delta - server_delta, 0))
    time.sleep(max(waiting_time - waiting_delta, 0))

    for t in threads:
        t.start()
        time.sleep(sleep_time)
    for t in threads:
        t.join()

    # update database
    print()
    # 将为False的ck更新为负值
    for ck, state in mask_dict.items():
        if state <= 0:
            database.insertItem(ck, time.time(), today_week_str, state)
        # else:
        # 当前尚未抢到时，次数+1，state为0时说明不足，不自增
        database.addTimes(ck, today_week_str)

    # TODO DEBUG
    # message notification
    summary = f"Coupon ({coupon_type})"
    content = ""
    print()
    # 将为False的ck更新为负值
    for ck, state in mask_dict.items():
        if state == -1:
            print(f"User: {getUserName(ck)} 抢到优惠券")
            content += f"User: {getUserName(ck)} 抢到优惠券！\n"
        elif state == 0:
            print(f"User: {getUserName(ck)} 点点券不足 或 过期")
            content += f"User: {getUserName(ck)} 点点券不足 或 过期！\n"
        elif state == -2:
            print(f"User: {getUserName(ck)} ck过期")
            content += f"User: {getUserName(ck)} ck过期！\n"
        else:
            print(f"User: {getUserName(ck)} 未抢到")
            content += f"User: {getUserName(ck)} 未抢到！\n"

    sendNotification(summary=summary, content=content)

    print('\nDatabase after updating：')
    database.printAllItems()
    database.close()

    printT("Ending...")


def receiveKeyAndNecklaceCoupon(cookie, mask_dict, loop_time=1, sleep_time=0.03, thread_id=0, thread_number=1):
    # get receive key
    cur_index = 0
    receive_key_dict = {}
    while cur_index < 500:
        getCcFeedInfo(cookie, receive_key_dict)
        if len(receive_key_dict[cookie]):
            printT(f"Thread: {thread_id}/{thread_number}: Receive key found. Continuing...")
            break
        else:
            if cur_index % 20 == 0:
                printT(f"Thread: {thread_id}/{thread_number}: No receive key found....")
        cur_index += 1
    if cur_index == 500:
        printT("No avaliable cookie. Exiting...")
        return
    api_para = getReceiveNecklaceCouponSign(receive_key_dict[cookie], cookie)
    for i in range(loop_time):
        receiveNecklaceCouponThread(cookie, api_para, mask_dict, thread_id=thread_id, thread_number=thread_number)
        time.sleep(sleep_time)
    return


# 0点特殊处理
# 多开几个线程，每个线程单独处理一个
# waiting_delta：提前多少秒开始运行
def exchange0Clock(batch_size=4, waiting_delta=0.0, loop_times=1, sleep_time=0.03):
    # TODO DEBUG
    is_debug = 'DEBUG_59_20' in os.environ and os.environ['DEBUG_59_20'] == 'True'

    printT("Starting..." + (" (Debug Mode)" if is_debug else ""))

    cookies = os.environ["JD_COOKIE"].split('&') if "JD_COOKIE" in os.environ else []
    # get cookies from databse
    database_dict = {
        'type': 'sqlite',
        'name': "filtered_cks.db"
    }
    # 存入数据库
    # Debug
    database = SQLProcess("ck6_59_20_" + (datetime.datetime.now() + datetime.timedelta(hours=1)).strftime("%Y%W"),
                          database_dict)
    # 插入所有数据，如果存在则更新
    insert_start = time.time()
    # Debug
    # today_week_str = time.strftime("%Y-(%W) ")
    today_week_str = (datetime.datetime.now() + datetime.timedelta(hours=1)).strftime("%Y-(%W) ")
    for i, ck in enumerate(cookies):
        database.insertItem(ck, time.time(), today_week_str, len(cookies) - i)
    insert_end = time.time()
    print("\nTime for updating/inserting into database：{:.2f}s\n".format(insert_end - insert_start))

    print('\nDatabase before updating：')
    database.printAllItems()

    # Debug 部署时修改
    cookies, visit_times = database.filterUsers(user_number=batch_size, year_month_day=today_week_str)
    # cookies, visit_times = database.filterUsers(user_number=60, year_month_day=today_week_str)
    cookies = cookies[:min(len(cookies), batch_size)]
    random.shuffle(cookies)
    # cookies = cookies[-3:]
    print("\nAccount ready to run：")
    print("\n".join([getUserName(ck) for ck in cookies]), '\n')

    # 如果是23点，需要等待到0点后执行

    jd_timestamp = datetime.datetime.fromtimestamp(jdTime() / 1000)
    server_delta = (jd_timestamp - datetime.datetime.now()).total_seconds()
    printT(f"Server delay (JD server - current server): {server_delta}s.")
    if not is_debug:
        nex_hour = (jd_timestamp + datetime.timedelta(hours=1)).replace(minute=0, second=0, microsecond=0)
    else:
        nex_hour = (jd_timestamp + datetime.timedelta(minutes=1)).replace(second=0, microsecond=0)
    waiting_time = (nex_hour - jd_timestamp).total_seconds()
    printT(f"Waiting to 00:00, waiting {waiting_time}s...")
    time.sleep(max(waiting_time - waiting_delta, 0))

    printT('Ready for coupons...')

    threads = []
    mask_dict = {}
    for ck in cookies:
        mask_dict[ck] = 1

    for i in range(len(cookies)):
        cookie = cookies[i]
        threads.append(
            threading.Thread(target=receiveKeyAndNecklaceCoupon,
                             args=(cookie, mask_dict, loop_times, sleep_time, i, len(cookies)))
        )

    for t in threads:
        t.start()
        time.sleep(sleep_time)
    for t in threads:
        t.join()

    # update database
    print()
    # 将为False的ck更新为负值
    for ck, state in mask_dict.items():
        if state <= 0:
            database.insertItem(ck, time.time(), today_week_str, state)
        # else:
        # 当前尚未抢到时，次数+1，state为0时说明不足，不自增
        database.addTimes(ck, today_week_str)

    # TODO DEBUG
    # message notification
    summary = "Coupon (59 - 20)"
    content = ""

    print()
    # 将为False的ck更新为负值
    for ck, state in mask_dict.items():
        if state == -1:
            print(f"User: {getUserName(ck)} 抢到优惠券")
            content += f"User: {getUserName(ck)} 抢到优惠券！\n"
        elif state == 0:
            print(f"User: {getUserName(ck)} 点点券不足 或 过期")
            content += f"User: {getUserName(ck)} 点点券不足 或 过期！\n"
        elif state == -2:
            print(f"User: {getUserName(ck)} ck过期")
            content += f"User: {getUserName(ck)} ck过期！\n"
        else:
            print(f"User: {getUserName(ck)} 未抢到")
            content += f"User: {getUserName(ck)} 未抢到！\n"

    sendNotification(summary=summary, content=content)

    print('\nDatabase after updating：')
    database.printAllItems()
    database.close()

    printT("Ending...")


def loopForDays(
        second_ahead,
        sleep_time,
        thread_number=12,
        coupon_type="59-20",
        clock_list=[0, 10, 14, 18, 22]):
    global ts_time

    clock_list.sort()
    clock_list.append(clock_list[0])

    # 本地运行环境
    if not ('QINGLONG_ENVIRON' in os.environ and os.environ['QINGLONG_ENVIRON'] == "True"):
        while True:
            # get next start hour
            cur_hour = int(datetime.datetime.now().strftime("%H"))
            next_clock = clock_list[0]
            for c in clock_list:
                if c > cur_hour:
                    next_clock = c
                    break

            # 修复非整点运行的bug
            next_task_start_time = datetime.datetime.now().replace(hour=(next_clock + 23) % 24,
                                                                   minute=59,
                                                                   second=5,
                                                                   microsecond=0)

            waiting_time = (next_task_start_time - datetime.datetime.now()).total_seconds()

            if not ('DEBUG_59_20' in os.environ and os.environ['DEBUG_59_20'] == 'True'):
                print("\n" + ("Waiting to " + str(next_task_start_time)).center(80, "*") + "\n")
                printT(f"Waiting {waiting_time}s.")
                time.sleep(waiting_time)

            ts_time = int(round((datetime.datetime.now() - datetime.timedelta(minutes=5)).timestamp() * 1000))

            printT(f"Starting coupon in {next_task_start_time}...")

            # 修复参数异常的bug
            if next_clock == 0:
                exchange0Clock(batch_size=6, waiting_delta=second_ahead * 2.3, loop_times=1, sleep_time=sleep_time)
            else:
                exchangeV4(batch_size=6, waiting_delta=second_ahead, thread_number=thread_number, sleep_time=sleep_time,
                           coupon_type=coupon_type)


            if 'DEBUG_59_20' in os.environ and os.environ['DEBUG_59_20'] == 'True':
                print()
                printT("Test end. Please set os.environ['DEBUG_59_20'] = \"False\"")
                break

            printT("Waiting 60s...")
            time.sleep(60)
    # 青龙运行环境
    else:
        if datetime.datetime.now().strftime('%H') == '23':
            exchange0Clock(batch_size=6, waiting_delta=second_ahead * 2.3, loop_times=1, sleep_time=sleep_time)
        else:
            exchangeV4(batch_size=6, waiting_delta=second_ahead, thread_number=thread_number, sleep_time=sleep_time,
                       coupon_type=coupon_type)

user_agent = "okhttp/3.12.1;jdmall;android;version/11.0.2;build/97565;"
ts_time = int(round((datetime.datetime.now() - datetime.timedelta(minutes=5)).timestamp() * 1000))

if __name__ == '__main__':
    # TODO
    # Necessary
    # 服务器接口
    # 联系我获取
    os.environ["JD_SIGN_API"] = "xxxxxxxxxxxxxxxxxxxxxx"
    os.environ["JD_SIGN_API_TOKEN"] = "xxxxxxxxxxxxxxxxxxxxxxxx"

    # TODO
    # Not necessary: Add wxpusher notification
    # https://wxpusher.zjiecode.com/admin/login
    os.environ["WXPUSHER_APP_TOKEN"] = ""
    os.environ["WXPUSHER_UID"] = ""

    # TODO
    # 调试时，将False修改为True，会默认当前时刻运行，注意首字母大写
    # 重要：部署时，将True修改为False，会默认整点运行
    os.environ['DEBUG_59_20'] = "True"
    # os.environ['DEBUG_59_20'] = "False"

    # TODO
    # 青龙环境下，需要将该参数修改为True，并设置自动定时任务
    # 本地环境默认为False
    # 命令： task path/to/file/exchange_59_20_desktop.py
    # cron: 0 59 9,13,17,21,23 * * *
    os.environ['QINGLONG_ENVIRON'] = "False"

    # TODO
    # 建议3个号起
    # B站搜抓wskey教程。注意iso抓到的wskey缺少pin字段，需要自行补充。必须包括这些字段。
    # 示例如下。少号时增加，多号时删除，账号越前面，优先级越高
    # 包括字段pin  wskey  whwswswws  unionwsws
    # 前n-1行尾部有','，最后一行尾部没有
    # 青龙环境中需要添加环境适配
    os.environ["JD_COOKIE"] = "&".join([
        'pin=xxxxx;wskey=xxxxxxxxxxxxxxxxxxxx;whwswswws=xxxxxxxxxxxxxxxxxxxxx;unionwsws=xxxxxxxxxxxxxxxxxx;',
        'pin=xxxxx;wskey=xxxxxxxxxxxxxxxxxxxx;whwswswws=xxxxxxxxxxxxxxxxxxxxx;unionwsws=xxxxxxxxxxxxxxxxxx;',
        'pin=xxxxx;wskey=xxxxxxxxxxxxxxxxxxxx;whwswswws=xxxxxxxxxxxxxxxxxxxxx;unionwsws=xxxxxxxxxxxxxxxxxx;',
        'pin=xxxxx;wskey=xxxxxxxxxxxxxxxxxxxx;whwswswws=xxxxxxxxxxxxxxxxxxxxx;unionwsws=xxxxxxxxxxxxxxxxxx;',
        'pin=xxxxx;wskey=xxxxxxxxxxxxxxxxxxxx;whwswswws=xxxxxxxxxxxxxxxxxxxxx;unionwsws=xxxxxxxxxxxxxxxxxx;'
    ])

    # TODO
    # Need: change parameters
    # 运行一次后挂机，到点时自动抢
    # 到clock_list的前1分钟时，会计算sign，随后提前second_ahead秒运行，共运行thread_number个线程，每个线程之间的间隔时间为sleep_time秒

    loopForDays(
        second_ahead=0.35,                      # 线程启动的提前秒数；线程的冷冻时间；例如提前0.40s准备启动线程；依赖于设备资源
        sleep_time=0.07,                        # 每个线程的等待时间；每次post的等待时间；依赖于网络传输速率；少号时建议0.08；多号时建议0.03
        thread_number=12,                       # 线程数量；post次数；可根据thread_number*sleep_time粗略计算当场运行时间；建议不超过15
        coupon_type="59-20",                    # 券名（可自定义），用于wxpusher通知
        clock_list=[0, 10, 14, 18, 22])         # 定时任务；例如0点场、10点场...
