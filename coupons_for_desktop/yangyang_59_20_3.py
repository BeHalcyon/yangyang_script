#!/bin/env python3
# -*- coding: utf-8 -*
'''
项目名称:yangyang_59_20_3.py
Author: yangyang
功能：
Date: 2022-5-26
cron: 0 59 9,13,19,23 * * *
new Env("京东59减20(3)");
'''

import datetime
import os
import random
import threading
import time
from urllib import parse
from urllib.parse import unquote
import sqlite3 as sqlite
import json
import re
import requests
import sys


def getUserName(cookie, mask=False):
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


def userAgent():
    """
    随机生成一个UA
    :return: jdapp;iPhone;9.4.8;14.3;xxxx;network/wifi;ADID/201EDE7F-5111-49E8-9F0D-CCF9677CD6FE;supportApplePay/0;hasUPPay/0;hasOCPay/0;model/iPhone13,4;addressid/2455696156;supportBestPay/0;appBuild/167629;jdSupportDarkMode/0;Mozilla/5.0 (iPhone; CPU iPhone OS 14_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148;supportJDSHWK/1
    """
    uuid = ''.join(random.sample('123456789abcdef123456789abcdef123456789abcdef123456789abcdef', 40))
    addressid = ''.join(random.sample('1234567898647', 10))
    iosVer = ''.join(
        random.sample(["14.5.1", "14.4", "14.3", "14.2", "14.1", "14.0.1", "13.7", "13.1.2", "13.1.1"], 1))
    iosV = iosVer.replace('.', '_')
    iPhone = ''.join(random.sample(["8", "9", "10", "11", "12", "13"], 1))
    ADID = ''.join(random.sample('0987654321ABCDEF', 8)) + '-' + ''.join(
        random.sample('0987654321ABCDEF', 4)) + '-' + ''.join(
        random.sample('0987654321ABCDEF', 4)) + '-' + ''.join(
        random.sample('0987654321ABCDEF', 4)) + '-' + ''.join(random.sample('0987654321ABCDEF', 12))
    return f'jdapp;iPhone;10.0.4;{iosVer};{uuid};network/wifi;ADID/{ADID};supportApplePay/0;hasUPPay/0;hasOCPay/0;model/iPhone{iPhone},1;addressid/{addressid};supportBestPay/0;appBuild/167629;jdSupportDarkMode/0;Mozilla/5.0 (iPhone; CPU iPhone OS {iosV} like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148;supportJDSHWK/1'


def printT(s):
    print("[{0}]: {1}".format(datetime.datetime.now(), s), flush=True)
    # print("[{0}]: {1}".format(datetime.datetime.now(), s))
    sys.stdout.flush()





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


def exchangeThread(cookie, request_url, mask_dict, thread_id, thread_number):
    # 当前时间段抢空；；活动结束了
    # process_stop_code_set = set(['D2', 'A15', 'A6'])
    # if datetime.datetime.now().strftime('%H') != '23':
    #     process_stop_code_set.add('A14')  # 今日没了
    ck = cookie

    response = requests.post(url=request_url['url'], verify=False, headers=request_url['headers'],
                             data=request_url['body'])
    result = response.json()
    # print(result)
    if 'result' not in result:
        if 'retMessage' in result:
            result_string = result['retMessage']
        elif 'couponIds' in result:
            result_string = result['couponIds']
        else:
            result_string = "TODO Message."
    else:
        if 'biz_msg' in result['result']['floorResult']:
            result_string = result['result']['floorResult']['biz_msg']
        elif 'couponIds' in result['result']['floorResult']:
            result_string = result['result']['floorResult']['couponIds']
        else:
            result_string = result['result']['floorResult']
        # result_string =  result['result']['floorResult']['biz_msg'] if 'biz_msg' in result['result']['floorResult'] else result['result']['floorResult']
    printT(
        f"Thread: {thread_id}/{thread_number}, user：{getUserName(ck, True)}: {result_string}")

    if "成功" in result_string or "已兑换" in result_string:
        mask_dict[ck] = -1
    elif "不足" in result_string:
        mask_dict[ck] = 0


def exchangeWithoutSignOrLog(
        header='https://api.m.jd.com/client.action?functionId=newBabelAwardCollection&client=wh5&clientVersion=1.0.0',
        body={}, waiting_delta=0.3, sleep_time=0.03, thread_number=4, coupon_type=""):
    requests.packages.urllib3.disable_warnings()

    cookies = os.environ["JD_COOKIE"].split('&') if "JD_COOKIE" in os.environ else []

    if len(cookies) == 0:
        print("All accounts have the coupon today! Exiting...")
        # 当前cookies没有时，就
        return

    database_dict = {
        'type': 'sqlite',
        'name': "filtered_cks.db"
    }
    batch_size = 3
    # 存入数据库
    database = SQLProcess("ck2_59_20_" + time.strftime("%Y%W"), database_dict)
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

    print("\nAccount ready to run：")
    print("\n".join([getUserName(ck) for ck in cookies]), '\n')

    # 每个线程只负责一个ck
    request_url_list = []
    for process_id in range(thread_number):
        buffer_body_string = f"body={parse.quote(json.dumps(body).replace(' ', ''))}"
        request_url_list.append({
            'url': header,
            'headers': {
                "Accept": "*/*",
                "Accept-Encoding": "gzip, deflate",
                "Accept-Language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7",
                "Connection": "keep-alive",
                "Content-Type": "application/x-www-form-urlencoded",
                # 'origin': 'https://h5.m.jd.com',
                'origin': 'https://pro.m.jd.com',
                "Referer": "https://prodev.m.jd.com/jdlite/active/3H885vA4sQj6ctYzzPVix4iiYN2P/index.html?sid=bf6ae253e73f472d5ec294810f46665w&un_area=7_502_35752_35860",
                "Cookie": cookies[process_id % len(cookies)],
                "User-Agent": userAgent(),
            },
            'body': buffer_body_string
        })

    threads = []
    mask_dict = {}
    for ck in cookies:
        mask_dict[ck] = 1

    for i in range(thread_number):
        threads.append(threading.Thread(target=exchangeThread, args=(
            cookies[i % len(cookies)], request_url_list[i], mask_dict, i, thread_number)))

    random.shuffle(threads)

    if datetime.datetime.now().strftime('%H') == '19':
        waiting_delta += 0.1

    printT('Ready for coupons...')

    jd_timestamp = datetime.datetime.fromtimestamp(jdTime() / 1000)
    server_delta = (jd_timestamp - datetime.datetime.now()).total_seconds()
    printT(f"Server delay (JD server - current server): {server_delta}s.")

    nex_time = (jd_timestamp + datetime.timedelta(minutes=1)).replace(second=0, microsecond=0)
    waiting_time = (nex_time - jd_timestamp).total_seconds()
    printT(f"Waiting {waiting_time}s...")
    time.sleep(max(waiting_time - waiting_delta, 0))

    printT("Sub-thread(s) start...")
    for t in threads:
        t.start()
        time.sleep(sleep_time)
    for t in threads:
        t.join()
    printT("Sub-thread(s) done...")

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

    # 将为False的ck更新为负值
    for ck, state in mask_dict.items():
        if state == -1:
            print(f"User: {getUserName(ck)} 抢到优惠券")
            content += f"User: {getUserName(ck)} 抢到优惠券！\n"
        elif state == 0:
            print(f"User: {getUserName(ck)} 点点券不足")
            content += f"User: {getUserName(ck)} 点点券不足！\n"
        elif state == -2:
            print(f"User: {getUserName(ck)} ck过期")
            content += f"User: {getUserName(ck)} ck过期！\n"
        else:
            print(f"User: {getUserName(ck)} 未抢到")
            content += f"User: {getUserName(ck)} 未抢到！\n"


    print('\nDatabase after updating：')
    # database.printAllItems()
    # database.close()
    #
    # printT("Ending...")

    today_information = database.printAllItems(year_month_day=today_week_str)
    content += f"\n\n----------------------\n今日{coupon_type}优惠券账号状态如下：\n" + today_information + "----------------------\n"

    if len(coupon_type):
        sendNotification(summary=summary, content=content)


    database.close()
    printT("Ending...")



def loopForDays(header,
                body,
                second_ahead,
                sleep_time,
                thread_number,
                coupon_type="59-20(3)",
                clock_list=[0, 10, 14, 20, 22]):

    while True:
        # get next start hour
        clock_list.sort()
        clock_list.append(clock_list[0])
        cur_hour = int(datetime.datetime.now().strftime("%H"))
        next_clock = clock_list[0]
        for c in clock_list:
            if c > cur_hour:
                next_clock = c
                break

        next_task_start_time = datetime.datetime.now().replace(hour=(next_clock + 23) % 24, minute=59, second=20,
                                                               microsecond=0)
        waiting_time = (next_task_start_time - datetime.datetime.now()).total_seconds()

        if not ('DEBUG_59_20_3' in os.environ and os.environ['DEBUG_59_20_3'] == 'True'):
            print("\n" + ("Waiting to " + str(next_task_start_time)).center(80, "*") + "\n")
            printT(f"Waiting {waiting_time}s.")
            time.sleep(waiting_time)


            printT(f"Starting coupon in {next_task_start_time}...")

        exchangeWithoutSignOrLog(header=header,
                                 body=body,
                                 waiting_delta=second_ahead,
                                 sleep_time=sleep_time,
                                 thread_number=thread_number,
                                 coupon_type=coupon_type)


if __name__ == "__main__":
    header = "https://api.m.jd.com/client.action?functionId=volley_ExchangeAssetFloorForColor&appid=coupon-activity&client=wh5&area=17_1381_50718_53772&geo=%5Bobject%20Object%5D&t=1653322985601&eu=5663338346331693&fv=9323932366232313"
    body_dict = {
        "batchId": "859658610"
    }

    # TODO
    # Need: Add cookies
    # Delete the following code when using qinglong environment.
    os.environ["JD_COOKIE"] = "&".join(
        [
            # 多号时候添加，少号时删除
            "pt_key=AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA;pt_pin=jd_AAAAAAAAAAAAA;",
            "pt_key=AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA;pt_pin=jd_AAAAAAAAAAAAA;",
            "pt_key=AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA;pt_pin=jd_AAAAAAAAAAAAA;",
            "pt_key=AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA;pt_pin=jd_AAAAAAAAAAAAA;"
        ]
    )

    # TODO
    # Not necessary: Add wxpusher notification if you want
    os.environ["WXPUSHER_APP_TOKEN"] = ""
    os.environ["WXPUSHER_UID"] = ""
    # 调试时设置为True
    os.environ['DEBUG_59_20_3'] = "False"


    # TODO
    # Need: change parameters
    loopForDays(header=header,
                body=body_dict,
                second_ahead=0.40,              # 线程启动的提前秒数；线程的冷冻时间；例如提前0.40s准备启动线程；依赖于设备资源
                sleep_time=0.05,                # 每个线程的等待时间；每次post的等待时间；依赖于网络传输速率；
                thread_number=20,               # 线程数量；post次数；可根据thread_number*sleep_time粗略计算当场运行时间
                coupon_type="59-20(3)",         # 券名（可自定义）
                clock_list=[0, 10, 14, 20, 22]  # 定时任务；例如0点场、10点场...
                )
