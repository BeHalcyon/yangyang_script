#!/bin/env python3
# -*- coding: utf-8 -*
'''
项目名称:exchange_29_8.py
Author: yangyang
功能：
Date: 2022-3-21
cron: 0 59 8,11,14,16,19 * * *
new Env('极速版29减8(python)');
'''

UserAgent = ''
cookie = ''
account = ''
charge_targe_id = ''
cookies = []
charge_targe_ids = ''

import requests
import time,datetime
import requests,re,os,sys,random,json
from urllib.parse import quote, unquote
import threading
import urllib3
import multiprocessing
import random

requests.packages.urllib3.disable_warnings()
today = datetime.datetime.now().strftime('%Y-%m-%d')
tomorrow=(datetime.datetime.now() + datetime.timedelta(days=1)).strftime('%Y-%m-%d')
nowtime = datetime.datetime.now ().strftime ('%Y-%m-%d %H:%M:%S.%f8')

pwd = os.path.dirname(os.path.abspath(__file__)) + os.sep
path = pwd + "env.sh"


sid = ''.join (random.sample ('123456789abcdef123456789abcdef123456789abcdef123456789abcdef', 32))
sid_ck = ''.join (random.sample ('123456789abcdef123456789abcdef123456789abcdef123456789abcdefABCDEFGHIJKLMNOPQRSTUVWXYZ', 43))

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

cookies1 = []
cookies1 = os.environ["JD_COOKIE"]
cookies = cookies1.split ('&')

def userAgent():
    """
    随机生成一个UA
    :return: jdapp;iPhone;9.4.8;14.3;xxxx;network/wifi;ADID/201EDE7F-5111-49E8-9F0D-CCF9677CD6FE;supportApplePay/0;hasUPPay/0;hasOCPay/0;model/iPhone13,4;addressid/2455696156;supportBestPay/0;appBuild/167629;jdSupportDarkMode/0;Mozilla/5.0 (iPhone; CPU iPhone OS 14_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148;supportJDSHWK/1
    """
    if not UserAgent:
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
    else:
        return UserAgent


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
msg().main()


def setName(cookie):
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

def postUrl(ck, user_name, process_id):
    request_url = {
        'url': "https://api.m.jd.com/client.action?functionId=lite_newBabelAwardCollection&client=wh5&clientVersion=1.0.0",
        'headers': {
            "Accept": "*/*",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "zh-cn",
            "Connection": "keep-alive",
            "Content-Type": "application/x-www-form-urlencoded",
            'origin': 'https://pro.m.jd.com',
            "Referer": "https://pro.m.jd.com/jdlite/active/3H885vA4sQj6ctYzzPVix4iiYN2P/index.html?lng=106.476617&lat=29.502674&sid=fbc43764317f538b90e0f9ab43c8285w&un_area=4_50952_106_0",
            "Cookie": ck,
            # "User-Agent": userAgent(),
        },
        'body': r"body=%7B%22activityId%22%3A%223H885vA4sQj6ctYzzPVix4iiYN2P%22%2C%22scene%22%3A%221%22%2C%22args%22%3A%22key%3D6102ED3D9BC7C8DFF14D1A36FFA89602070B138DF76D200B6FA411359FBAD50B1FD83787E7C9BEF8843A4631ADF6C792_bingo%2CroleId%3D20E136F5EB78E9D323CEA65000B08718_bingo%2CstrengthenKey%3D19F512DCD8EE34ABE9C4FB4A92C2F42A65327F2097264F7157C058E713F98BE4_bingo%22%7D",
    }
    response = requests.post(url=request_url['url'], verify=False, headers=request_url['headers'], data=request_url['body'])
    return response.json()

def exchange(process_id, cks):
    global loop_times
    flag = False
    for t in range(loop_times):
        for ck in cks:
            result = postUrl(ck, setName(ck), process_id)
            msg(f"进程：{process_id}-{t+1}/{loop_times} 账号：{setName(ck)} {result}")
            if result['subCode'] == 'D2':
                flag = True
                break
        if flag:
            break

# 前n个号
# cookies = cookies

nex_minute = (datetime.datetime.now() + datetime.timedelta(minutes=1)).replace(second=0, microsecond=0)
waiting_time = (nex_minute - datetime.datetime.now()).total_seconds()
loop_times = 3

msg(f"等待{waiting_time}s")
# waiting 
import time
time.sleep(waiting_time - 1)
# sleep(nex_minute - datetime.datetime.now())

msg("Sub-process(es) start.")
pool = multiprocessing.Pool(processes = 4)
for i in range(4):
    random.shuffle(cookies)
    pool.apply_async(exchange, (i+1, cookies.copy(), ))

pool.close()
pool.join()
msg("Sub-process(es) done.")
# for ck in cookies[-5:]:
#     exchange(ck, setName(ck))

