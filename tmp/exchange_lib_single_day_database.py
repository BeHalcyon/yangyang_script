#!/bin/env python3
# -*- coding: utf-8 -*

import requests
import time,datetime
import requests,re,os,sys,random,json
from urllib.parse import quote, unquote
import threading
import urllib3
import multiprocessing
import random
import sqlite3 as sql
import hashlib 


def printT(s):
    print("[{0}]: {1}".format(datetime.datetime.now(), s), flush=True)
    sys.stdout.flush()

def getEnvs(label):
    try:
        if label == 'True' or label == 'yes' or label == 'true' or label == 'Yes':
            return True
        elif label == 'False' or label == 'no' or label == 'false' or label == 'No':
            return False
    except:
        pass
    try:
        if '.' in label:
            return float(label)
        elif '&' in label:
            return label.split('&')
        elif '@' in label:
            return label.split('@')
        else:
            return int(label)
    except:
        return label

def userAgent():
    
    """
    随机生成一个UA
    :return: jdapp;iPhone;9.4.8;14.3;xxxx;network/wifi;ADID/201EDE7F-5111-49E8-9F0D-CCF9677CD6FE;supportApplePay/0;hasUPPay/0;hasOCPay/0;model/iPhone13,4;addressid/2455696156;supportBestPay/0;appBuild/167629;jdSupportDarkMode/0;Mozilla/5.0 (iPhone; CPU iPhone OS 14_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148;supportJDSHWK/1
    """
    uuid = ''.join (random.sample ('123456789abcdef123456789abcdef123456789abcdef123456789abcdef', 40))
    addressid = ''.join (random.sample ('1234567898647', 10))
    iosVer = ''.join (
        random.sample (["14.5.1", "14.4", "14.3", "14.2", "14.1", "14.0.1", "13.7", "13.1.2", "13.1.1"], 1))
    iosV = iosVer.replace ('.', '_')
    iPhone = ''.join (random.sample (["8", "9", "10", "11", "12", "13"], 1))
    ADID = ''.join (random.sample ('0987654321ABCDEF', 8)) + '-' + ''.join (
        random.sample ('0987654321ABCDEF', 4)) + '-' + ''.join (
        random.sample ('0987654321ABCDEF', 4)) + '-' + ''.join (
        random.sample ('0987654321ABCDEF', 4)) + '-' + ''.join (random.sample ('0987654321ABCDEF', 12))
    return f'jdapp;iPhone;10.0.4;{iosVer};{uuid};network/wifi;ADID/{ADID};supportApplePay/0;hasUPPay/0;hasOCPay/0;model/iPhone{iPhone},1;addressid/{addressid};supportBestPay/0;appBuild/167629;jdSupportDarkMode/0;Mozilla/5.0 (iPhone; CPU iPhone OS {iosV} like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148;supportJDSHWK/1'
 

## 获取通知服务
class msg(object):
    def __init__(self, m=''):
        self.str_msg = m
        self.message()
    def message(self):
        global msg_info
        printT(self.str_msg)
        try:
            msg_info = "{}\n{}".format(msg_info, self.str_msg)
        except:
            msg_info = "{}".format(self.str_msg)
        sys.stdout.flush()           #这代码的作用就是刷新缓冲区。
                                     # 当我们打印一些字符时，并不是调用print函数后就立即打印的。一般会先将字符送到缓冲区，然后再打印。
                                     # 这就存在一个问题，如果你想等时间间隔的打印一些字符，但由于缓冲区没满，不会打印。就需要采取一些手段。如每次打印后强行刷新缓冲区。
    def getsendNotify(self, a=0):
        if a == 0:
            a += 1
        try:
            url = 'https://gitee.com/curtinlv/Public/raw/master/sendNotify.py'
            response = requests.get(url)
            if 'curtinlv' in response.text:
                with open('sendNotify.py', "w+", encoding="utf-8") as f:
                    f.write(response.text)
            else:
                if a < 5:
                    a += 1
                    return self.getsendNotify(a)
                else:
                    pass
        except:
            if a < 5:
                a += 1
                return self.getsendNotify(a)
            else:
                pass
    def main(self):
        global send
        cur_path = os.path.abspath(os.path.dirname(__file__))
        sys.path.append(cur_path)
        if os.path.exists(cur_path + "/sendNotify.py"):
            try:
                from sendNotify import send
            except:
                self.getsendNotify()
                try:
                    from sendNotify import send
                except:
                    printT("加载通知服务失败~")
        else:
            self.getsendNotify()
            try:
                from sendNotify import send
            except:
                printT("加载通知服务失败~")
        ###################

class SQLProcess:

    def __init__(self, table_name, database_name = "./filtered_cks.db"):
        self.database_name = database_name
        self.table_name = self.getTableName(table_name)
        self.createDatebase()
        self.createTable()
        self.deleteTableIfExpired()
    
    def getTableName(self, name):
        return 'table_' + name.replace('=', '').replace('%', '').replace('_', '').split("key")[-1][::10]
    
    def createDatebase(self):
        self.conn = sql.connect(self.database_name)
        self.c = self.conn.cursor()
        return self.conn
        
    def createTable(self):
        self.c.execute(f'''CREATE TABLE IF NOT EXISTS {self.table_name}
                           (USER_NAME TEXT PRIMARY KEY NOT NULL,
                           TIMESTAMP timestamp NOT NULL,
                           DATE TEXT NOT NULL,
                           PRIORITY INT NOT NULL);
                           ''')
        
        self.conn.commit()
        print(f"Table {self.table_name} has been created...")
    
    def deleteTableIfExpired(self):
        p = self.c.execute(f'''
                        SELECT DATE from {self.table_name}
                        ''')
        res = self.c.fetchone()
        if res is not None:
            for item in p:
                # table_date = res[0]
                if item[0] != str(datetime.date.today()):
                    print(f"Item {item} is filtered out...")
                    self.deleteTable()
                    self.createTable()
                    return

    def deleteTable(self):
        self.c.execute(f"DROP TABLE {self.table_name};")
        self.conn.commit()
        print(f"Table {self.table_name} has been deleted...")
        
    def insertItem(self, user_name, timestamp, year_month_day, priority):
        if self.findUserName(user_name):
            print(f"{getUserName(user_name)} is in Table {self.table_name}. Updating...")
            self.updateItem(user_name, timestamp, year_month_day, priority)
            return
        self.c.execute(f'''INSERT INTO {self.table_name} (USER_NAME, TIMESTAMP, DATE, PRIORITY)
                            VALUES ('{user_name}', {timestamp}, '{year_month_day}', {priority})''')
        self.conn.commit()
        print(f"Item {getUserName(user_name)} has been inserted into Table {self.table_name}...")
    
    def updateItem(self, user_name, timestamp, year_month_day, priority):
        self.c.execute(f'''
                        UPDATE {self.table_name} set 
                        TIMESTAMP={timestamp}, 
                        DATE='{year_month_day}',
                        PRIORITY={priority}
                        WHERE USER_NAME='{user_name}' AND PRIORITY > -1
                        ''')
        self.conn.commit()
        print(f"Item {getUserName(user_name)} has been update in Table {self.table_name}...")
    
    def filterUsers(self, user_number):
        p = self.c.execute(f'''
                        SELECT USER_NAME from {self.table_name} WHERE PRIORITY > -1 ORDER BY PRIORITY DESC;
                        ''')
        res = [x[0] for x in p]
        return res[:min(len(res), user_number)]
    
    def getItem(self, user_name):
        if self.findUserName(user_name):
            self.c.execute(f'''
                        SELECT * from {self.table_name} where USER_NAME = '{user_name}'
                        ''')
            return self.c.fetchone()
        else:
            return None
    
    def findUserName(self, user_name):
        p = self.c.execute(f'''
                        SELECT count(*) from {self.table_name} where USER_NAME = '{user_name}'
                        ''')
        return self.c.fetchone()[0] != 0
    
    def printAllItems(self):
        for item in self.c.execute(f"SELECT * from {self.table_name}"):
            print(getUserName(item[0]), item[1], item[2], item[3])
            
    def getAllUsers(self):
        res = []
        for item in self.c.execute(f"SELECT USER_NAME from {self.table_name}"):
            res.append(item[0])
        return res
            
    def close(self):
        self.conn.close()
    

def getUserName(cookie):
    try:
        r = re.compile(r"pt_pin=(.*?);")    #指定一个规则：查找pt_pin=与;之前的所有字符,但pt_pin=与;不复制。r"" 的作用是去除转义字符.
        userName = r.findall(cookie)        #查找pt_pin=与;之前的所有字符，并复制给r，其中pt_pin=与;不复制。
        #print (userName)
        userName = unquote(userName[0])     #r.findall(cookie)赋值是list列表，这个赋值为字符串
        #print(userName)
        return userName
    except Exception as e:
        print(e,"cookie格式有误！")
        exit(2)

def postUrl(request_url):
    response = requests.post(url=request_url['url'], verify=False, headers=request_url['headers'], data=request_url['body'])
    return response.json()


def filterCks(cks, url, body):
    request_url = {
        'url': url,
        'headers': {
            "Accept": "*/*",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "zh-cn",
            "Connection": "keep-alive",
            "Content-Type": "application/x-www-form-urlencoded",
            'origin': 'https://pro.m.jd.com',
            "Referer": "https://pro.m.jd.com/jdlite/active/3H885vA4sQj6ctYzzPVix4iiYN2P/index.html?lng=106.476617&lat=29.502674&sid=fbc43764317f538b90e0f9ab43c8285w&un_area=4_50952_106_0",
            "Cookie": "None",
            "User-Agent": userAgent(),
        },
        'body': body,
    }
    buf_cks = []
    for ck in cks:
        request_url['headers']['Cookie'] = ck
        response = requests.post(url=request_url['url'], verify=False, headers=request_url['headers'], data=request_url['body'])
        result = response.json()
        if 'subCode' in result.keys() and (result['subCode'] == 'A13' or result['subCode'] == 'A28'): # 今日已领取；很抱歉没抢到
            continue
        buf_cks.append(ck)
    return buf_cks


def exchange(process_id, cks, loop_times, url, body, mask_dict):
    flag = False
    request_url = {
        'url': url,
        'headers': {
            "Accept": "*/*",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "zh-cn",
            "Connection": "keep-alive",
            "Content-Type": "application/x-www-form-urlencoded",
            'origin': 'https://pro.m.jd.com',
            "Referer": "https://pro.m.jd.com/jdlite/active/3H885vA4sQj6ctYzzPVix4iiYN2P/index.html?lng=106.476617&lat=29.502674&sid=fbc43764317f538b90e0f9ab43c8285w&un_area=4_50952_106_0",
            "Cookie": "None",
            "User-Agent": userAgent(),
        },
        'body': body,
    }

    # flag_arr = [True]*len(cks)
    for t in range(loop_times):
        # 每次loop的ua一样
        request_url['headers']['User-Agent'] = userAgent()
        for i in range(len(cks)):
            ck = cks[i]
            if not mask_dict[ck]: continue
            request_url['headers']['Cookie'] = ck
            # request_url['headers']['User-Agent'] = userAgent()
            response = requests.post(url=request_url['url'], verify=False, headers=request_url['headers'], data=request_url['body'])
            result = response.json()
            msg(f"进程：{process_id}-执行次数：{t+1}/{loop_times}\n账号：{getUserName(ck)} {result['subCode'] + ' : ' + result['subCodeMsg'] if 'subCodeMsg' in result.keys() else result}")
            # if 'subCode' in result.keys() and (result['subCode'] == 'D2' or result['subCode'] == 'A14' or result['subCode'] == 'A25'): # 当前时间段抢空；今日没了；火爆了
            # # if 'subCode' in result.keys() and (result['subCode'] == 'A14' or result['subCode'] == 'A25'): # 今日没了；火爆了
            #     flag = True
            #     break
            if 'subCode' in result.keys():
                if result['subCode'] == 'D2' or result['subCode'] == 'A14' or result['subCode'] == 'A25': # 当前时间段抢空；今日没了；火爆了
                    # 直接停止该线程
                    msg("停止所有进程...")
                    flag = True
                    break
                if result['subCode'] == 'A1' or result['subCode'] == 'A13' or result['subCode'] == 'A28': # 领取成功；今日已领取；很抱歉没抢到
                    # 停止该号
                    # flag_arr[i] = False
                    mask_dict[ck] = False
                    msg(f"所有进程停止账号：{getUserName(ck)}")

        if flag:
            break

def exchangeCoupons(url='https://api.m.jd.com/client.action?functionId=lite_newBabelAwardCollection&client=wh5&clientVersion=1.0.0', body='None'):

    requests.packages.urllib3.disable_warnings()

    pwd = os.path.dirname(os.path.abspath(__file__)) + os.sep
    path = pwd + "env.sh"

    sid = ''.join (random.sample ('123456789abcdef123456789abcdef123456789abcdef123456789abcdef', 32))
    sid_ck = ''.join (random.sample ('123456789abcdef123456789abcdef123456789abcdef123456789abcdefABCDEFGHIJKLMNOPQRSTUVWXYZ', 43))

    cookies = os.environ["JD_COOKIE"].split('&')

    # 测试
    # cookies = cookies[-7:]

    # 存入数据库
    database = SQLProcess(body)
    # 插入所有数据，如果存在则更新
    for i, ck in enumerate(cookies):
        database.insertItem(ck, time.time(), str(datetime.date.today()), len(cookies) - i)

    print('\n更新前数据库如下：')
    database.printAllItems()

    cookies = database.filterUsers(4)
    print("待抢账号：\n", "\n".join([getUserName(ck) for ck in cookies]), '\n')

    process_number = 8

    # 进程共享数据
    mask_dict = multiprocessing.Manager().dict()
    for ck in cookies:
        mask_dict[ck] = True

    # 打乱数组
    cookies_array = []
    for i in range(process_number):
        random.shuffle(cookies)
        cookies_array.append(cookies.copy())

    msg().main()

    nex_minute = (datetime.datetime.now() + datetime.timedelta(minutes=1)).replace(second=0, microsecond=0)
    waiting_time = (nex_minute - datetime.datetime.now()).total_seconds()
    loop_times = 10 // len(cookies) + 1

    msg(f"等待{waiting_time}s")

    # waiting # 部署时需要去掉注释
    time.sleep(max(waiting_time - 0.22, 0))

    msg("Sub-process(es) start.")
    process_number = 8
    pool = multiprocessing.Pool(processes = process_number)
    for i in range(process_number):
        # random.shuffle(cookies)
        pool.apply_async(exchange, args=(i+1, cookies_array[i], loop_times, url, body, mask_dict, ))

    pool.close()
    pool.join()

    msg("Sub-process(es) done.")

    # 将为False的ck更新为负值
    for ck, state in mask_dict.items():
        if not state:
            database.insertItem(ck, time.time(), str(datetime.date.today()), -1)

    print('\n更新后数据库如下：')
    database.printAllItems()

    database.close()