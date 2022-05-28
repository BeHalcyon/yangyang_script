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

import json
import re
import requests
import sys


def getUserName(cookie):
    try:
        return unquote(re.compile(r"pt_pin=(.*?);").findall(cookie)[0])
    except Exception as e:
        print(e, "ERROR in cookie format！")
        exit(2)


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
    result_string = json.dumps(result) if 'result' not in result else result['result']['floorResult'][
        'biz_msg'] if 'biz_msg' in result['result']['floorResult'] else result['result']['floorResult']
    printT(
        f"Thread: {thread_id}/{thread_number}, user：{getUserName(ck)}: {result_string}")

    if "成功" in result_string or "已兑换" in result_string:
        mask_dict[ck] = -1
    elif "不足" in result_string:
        mask_dict[ck] = 0


def exchangeWithoutSignOrLog(
        header='https://api.m.jd.com/client.action?functionId=newBabelAwardCollection&client=wh5&clientVersion=1.0.0',
        body={}, waiting_delta=0.3, sleep_time=0.03, thread_number=4, coupon_type=""):
    requests.packages.urllib3.disable_warnings()

    cookies = os.environ["JD_COOKIE"].split('&') if "JD_COOKIE" in os.environ else []

    # 每线程每个账号循环次数
    if len(cookies) == 0:
        print("All accounts have the coupon today! Exiting...")
        # 当前cookies没有时，就
        return

    random.shuffle(cookies)

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

    print()

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
            print(f"User: {getUserName(ck)} 点点券不足")
            content += f"User: {getUserName(ck)} 点点券不足！\n"
        elif state == -2:
            print(f"User: {getUserName(ck)} ck过期")
            content += f"User: {getUserName(ck)} ck过期！\n"
        else:
            print(f"User: {getUserName(ck)} 未抢到")
            content += f"User: {getUserName(ck)} 未抢到！\n"

    content += f"\n----------------------\n"

    if len(coupon_type):
        sendNotification(summary=summary, content=content)

    printT("Ending...")


def loopForDays(header,
                body,
                waiting_delta,
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

        print("\n" + ("Waiting to " + str(next_task_start_time)).center(80, "*") + "\n")
        printT(f"Waiting {waiting_time}s.")
        time.sleep(waiting_time)

        printT(f"Starting coupon in {next_task_start_time}...")

        exchangeWithoutSignOrLog(header=header,
                                 body=body,
                                 waiting_delta=waiting_delta,
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
            "pt_key=AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA;pt_pin=BBBBBBBBBBBBB;",
            "pt_key=AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA;pt_pin=BBBBBBBBBBBBB;",
            "pt_key=AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA;pt_pin=BBBBBBBBBBBBB;"
        ]
    )

    # TODO
    # Not necessary: Add wxpusher notification if you want
    os.environ["WXPUSHER_APP_TOKEN"] = ""
    os.environ["WXPUSHER_UID"] = ""

    loopForDays(header=header,
                body=body_dict,
                waiting_delta=0.4,  # 线程启动等待耗时
                sleep_time=0.05,    # 每个线程的等待时间
                thread_number=20,   # 线程数量
                coupon_type="59-20(3)"
                )
