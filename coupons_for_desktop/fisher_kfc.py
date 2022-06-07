#!/bin/env python3
# -*- coding: utf-8 -*
'''
项目名称:fisher_kfc.py
Author: fisher
功能：残障脚本，请勿使用
Date: 2022-6-6
cron: 20 59 19,23 * * *
new Env("plus_kfc");
'''

# from exchange_lib import *

import requests
import time, datetime
import requests, re, os, sys, random, json
from urllib.parse import quote, unquote
import threading
import urllib3
import multiprocessing
import random
import sqlite3 as sqlite

import hashlib
import os
import collections
from urllib import parse



import os
import sys
import io
import datetime

def printT(s):
    print("[{0}]: {1}".format(datetime.datetime.now(), s), flush=True)
    # print("[{0}]: {1}".format(datetime.datetime.now(), s))
    sys.stdout.flush()

def exchangeCouponsKFC(waiting_delta=0.3, sleep_time=0.03, thread_number=12):

    requests.packages.urllib3.disable_warnings()

    cookies = os.environ["JD_COOKIE"].split('&') if "JD_COOKIE" in os.environ else []

    # 每个线程每个账号循环次数
    if len(cookies) == 0:
        print("All accounts have the coupon today! Exiting...")
        # 当前cookies没有时，就
        return

    threads = []
    for i in range(thread_number):
        threads.append(threading.Thread(target=exchangeKFC, args=(cookies[i % len(cookies)], )))

    printT('Ready for coupons...')

    jd_timestamp = datetime.datetime.fromtimestamp(jdTime() / 1000)
    server_delta = (jd_timestamp - datetime.datetime.now()).total_seconds()
    printT(f"Server delay (JD server - current server): {server_delta}s.")
    nex_minute = (jd_timestamp + datetime.timedelta(minutes=1)).replace(second=0, microsecond=0)
    waiting_time = (nex_minute - jd_timestamp).total_seconds()
    printT(f"Waiting {waiting_time}s...")
    time.sleep(max(waiting_time - waiting_delta, 0))

    printT("Sub-thread(s) start...")
    for t in threads:
        t.start()
        time.sleep(sleep_time)
    for t in threads:
        t.join()
    printT("Sub-thread(s) done...")

    print()



def jdTime():
    url = 'http://api.m.jd.com/client.action?functionId=queryMaterialProducts&client=wh5'
    headers = {
        "user-agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36'
    }
    try:
        index = 0
        while index < 3:
            res = requests.get(url=url, headers=headers, timeout=1).json()
            if 'currentTime2' in res:
                return int(res['currentTime2'])
            index += 1
        return int(round(time.time()*1000))
    except:
        return int(round(time.time()*1000))

def exchangeKFC(cookie):
    url = f"https://rsp.jd.com/resource/lifePrivilege/receive/v1?lt=m&an=plus.mobile&uniqueId=60947948441996&_={int(round(time.time() * 1000))}"
    headers = {
        "Host": "rsp.jd.com",
        "accept": "application/json, text/plain, */*",
        "user-agent": "jdapp;android;10.5.2;;;appBuild/96428;ef/1;ep/%7B%22hdid%22%3A%22JM9F1ywUPwflvMIpYPok0tt5k9kW4ArJEU3lfLhxBqw%3D%22%2C%22ts%22%3A1654535539316%2C%22ridx%22%3A-1%2C%22cipher%22%3A%7B%22sv%22%3A%22EG%3D%3D%22%2C%22ad%22%3A%22CzUmCzvsYzSnCtYzDNq0ZG%3D%3D%22%2C%22od%22%3A%22YtLwCzc0DQG3ZNOzEQS2Zq%3D%3D%22%2C%22ov%22%3A%22Ctq%3D%22%2C%22ud%22%3A%22ENY1DNGnCNC1DNC0EJY4BJHtDNvvC2Y1DNUzCm%3D%3D%22%7D%2C%22ciphertype%22%3A5%2C%22version%22%3A%221.2.0%22%2C%22appname%22%3A%22com.jingdong.app.mall%22%7D;jdSupportDarkMode/0;Mozilla/5.0 (Linux; Android 9; MI 6 Build/PKQ1.190118.001; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/89.0.4389.72 MQQBrowser/6.2 TBS/045946 Mobile Safari/537.36",
        "origin": "https://plus.m.jd.com",
        "x-requested-with": "com.jingdong.app.mall",
        "sec-fetch-site": "same-site",
        "sec-fetch-mode": "cors",
        "sec-fetch-dest": "empty",
        "referer": "https://plus.m.jd.com/",
        "accept-encoding": "gzip, deflate, br",
        "accept-language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7"
    }
    headers['cookie'] = cookie
    res = requests.get(url=url, headers=headers).json()
    printT(f"User: {getUserName(cookie)}, {res['msg']}")


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


def loopForDays(function,
        second_ahead,
        sleep_time,
        thread_number=12,
        coupon_type="59-20",
        clock_list=[0, 10, 14, 18, 22],
        url="",
        batch_size=0,
        other_batch_size=0,
        debug_flag_str="DEBUG_918",
        body_dict={}):
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

            if not (debug_flag_str in os.environ and os.environ[debug_flag_str] == 'True'):
                print("\n" + ("Waiting to " + str(next_task_start_time)).center(80, "*") + "\n")
                printT(f"Waiting {waiting_time}s.")
                time.sleep(waiting_time)

            ts_time = int(round((datetime.datetime.now() - datetime.timedelta(minutes=5)).timestamp() * 1000))

            printT(f"Starting coupon in {next_task_start_time}...")

            function(waiting_delta=second_ahead, sleep_time=sleep_time, thread_number=thread_number)

            if debug_flag_str in os.environ and os.environ[debug_flag_str] == 'True':
                print()
                printT(f"Test end. Please set os.environ['{debug_flag_str}'] = \"False\"")
                break

            printT("Waiting 60s...")
            time.sleep(60)


if __name__ == "__main__":
    # plus会员，尽量3个号起步
    os.environ["JD_COOKIE"] = "&".join([
        'pt_key=xxxxxxx;pt_pin=xxxxxxx;',
        'pt_key=xxxxxxx;pt_pin=xxxxxxx;',
        'pt_key=xxxxxxx;pt_pin=xxxxxxx;'
        ])

    # 为True时调试，为False时部署
    os.environ["DEBUG_KFC"] = "True"

    loopForDays(exchangeCouponsKFC, second_ahead=0.25, sleep_time=0.05, thread_number=12, coupon_type=None,
                clock_list=[10], url=None,
                batch_size=None, other_batch_size=None, debug_flag_str="DEBUG_KFC", body_dict={})

