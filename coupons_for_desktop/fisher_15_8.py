#!/bin/env python3
# -*- coding: utf-8 -*
'''
项目名称: fisher_15_8.py
Author: I know notiong
功能：
Date: 2022-5-7
cron: 20 59 8,11,14,17,19 * * *
new Env("极速版15减8");
'''

import time
import requests, re, json
from urllib.parse import unquote
import threading

import random
from urllib import parse

import os
import sys
import datetime


# 根据api接口生成sign
def getLogs(url=None, num=400):
    if url is None:
        if 'JDLITE_LOG_API' not in os.environ or len(os.environ['JDLITE_LOG_API']) == 0:
            print("ERROR! Please add JDLITE_LOG_APT!")
            exit()
        url = os.environ['JDLITE_LOG_API']

    log_list = []
    try:
        for i in range(num):
            log_list.append(json.dumps(requests.get(url=url).json()).replace(' ', ''))
            if i % 20 == 0:
                printT(f"Getting {i + 1}/{num} logs...")
        print(f"All {num} logs has been get.")
    except:
        log_list = []
        print("Error: No log found.")
        exit()
    return log_list


def printT(s):
    print("[{0}]: {1}".format(datetime.datetime.now(), s), flush=True)
    sys.stdout.flush()


def userAgent():
    return "jdapp;iPhone;9.4.8;14.3;xxxx;network/wifi;ADID/201EDE7F-5111-49E8-9F0D-CCF9677CD6FE;supportApplePay/0;hasUPPay/0;hasOCPay/0;model/iPhone13,4;addressid/2455696156;supportBestPay/0;appBuild/167629;jdSupportDarkMode/0;Mozilla/5.0 (iPhone; CPU iPhone OS 14_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148;supportJDSHWK/1"


def generateBody(log_dict):
    body_dict = {
        'activityId': '3H885vA4sQj6ctYzzPVix4iiYN2P',
        'scene': '1',
        'args': 'key=4C884367B622BB96ABD488103A5036F58B08100D4FEC967D97AA8854BC13AF4A50BE6F7B01529B9D56C52BEAB5EB5235_bingo,roleId=A921D0996A757D3D319487D17C0F25FE701307BE103D49F3D1562C7CF5D02F01F1043E437093D585B4730F630A66804F8AE429E9F2C40EE1F0580E482F388FEEF1F5A8A69753844555247364707E6E41040F01DEE945DF4C10432FB4875EA6DF48164CC736ACE898EE9E8947855DBC30CD8BF4D53E7EA1B873BAAE1052D9BB9748A8F83F1E3CD76509AFB2939FC10B6AE2ADCB50653791DF313F8F7BF0AF7AE7_bingo,strengthenKey=3FE987FADD098B5D46BA38B21875A5EBD8C02F19572CB3C5CC0385902CD416A23D357AD5C32B073932D1986E4D335028_bingo'
    }
    body = json.dumps({"activityId": body_dict['activityId'],
                       "scene": body_dict['scene'],
                       "args": body_dict['args'],
                       "log": log_dict['log'],
                       "random": log_dict['random']}
                      ).replace(' ', '')
    return f"body={parse.quote(body)}"


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


def exchangeThread(cookie, request_url, mask_dict, thread_id, thread_number):
    ck = cookie
    response = requests.post(url=request_url['url'], verify=False, headers=request_url['headers'],
                             data=request_url['body'])

    result = response.json()
    printT(
        f"Thread: {thread_id}/{thread_number}, user：{getUserName(ck)}: {result['subCode'] + ' : ' + result['subCodeMsg'] if 'subCodeMsg' in result.keys() else result}")

    if 'subCode' in result.keys():
        if result['subCode'] == 'A1' or result['subCode'] == 'A13':  # 领取成功；今日已领取；
            mask_dict[ck] = -1
        if result['subCode'] == 'A19':  # 很抱歉没抢到
            mask_dict[ck] = 0


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
        return int(round(time.time() * 1000))
    except:
        return int(round(time.time() * 1000))


def sendNotification(summary, content):
    if "WXPUSHER_APP_TOKEN" in os.environ and "WXPUSHER_UID" in os.environ:
        url = "http://wxpusher.zjiecode.com/api/send/message"
        body = {
            "appToken": os.environ["WXPUSHER_APP_TOKEN"],
            "content": content,
            "summary": summary,
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


def exchangeCouponsMayMonthV3(
        header='https://api.m.jd.com/client.action?functionId=lite_newBabelAwardCollection&client=wh5&clientVersion=1.0.0',
        waiting_delta=0.3, sleep_time=0.03, thread_number=4, coupon_type="", append_flag=True):
    # TODO DEBUG

    requests.packages.urllib3.disable_warnings()

    cookies = os.environ["JD_COOKIE"].split('&') if "JD_COOKIE" in os.environ else []

    visit_times = []

    if len(cookies) == 0:
        print("All accounts have the coupon today! Exiting...")
        return

    if append_flag and len(cookies) > 1 and len(visit_times):
        max_times = max(visit_times)
        for i in range(len(visit_times)):
            if visit_times[i] == max_times:
                cookies.append(cookies[i])
                break

    log_str_arr = getLogs(num=thread_number)

    # 每个线程只负责一个ck
    request_url_list = []
    for process_id in range(thread_number):
        request_url_list.append({
            'url': header,
            'headers': {
                "Accept": "*/*",
                "Accept-Encoding": "gzip, deflate",
                "Accept-Language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7",
                "Connection": "keep-alive",
                "Content-Type": "application/x-www-form-urlencoded",
                'origin': 'https://pro.m.jd.com',
                "Referer": "https://prodev.m.jd.com/jdlite/active/3H885vA4sQj6ctYzzPVix4iiYN2P/index.html?sid=bf6ae253e73f472d5ec294810f46665w&un_area=7_502_35752_35860",
                "Cookie": cookies[process_id % len(cookies)],
                "User-Agent": userAgent(),
            },
            'body': generateBody(json.loads(log_str_arr[process_id]))
        })

    print("\n待抢账号：")
    print("\n".join([getUserName(ck) for ck in cookies]), '\n')

    threads = []
    mask_dict = {}
    for ck in cookies:
        mask_dict[ck] = 1

    for i in range(thread_number):
        threads.append(threading.Thread(target=exchangeThread, args=(
            cookies[i % len(cookies)], request_url_list[i], mask_dict, i, thread_number)))

    random.shuffle(threads)

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

    summary = f"Coupon ({coupon_type})"
    content = ""

    # 将为False的ck更新为负值
    for ck, state in mask_dict.items():
        if state == -1:
            print(f"账号：{getUserName(ck)} 抢到{coupon_type}优惠券")
            content += f"账号：{getUserName(ck)} 抢到{coupon_type}优惠券\n"

    if len(coupon_type):
        sendNotification(summary=summary, content=content)


def loopForDays(function,
                second_ahead,
                sleep_time,
                thread_number=12,
                coupon_type="15-8",
                clock_list=[9, 12, 15, 18, 20],
                url="",
                batch_size=0,
                other_batch_size=0,
                debug_flag_str="DEBUG_15_8",
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

            function(
                header=url,
                waiting_delta=second_ahead, sleep_time=sleep_time, thread_number=thread_number, coupon_type=coupon_type,
                append_flag=False)

            if debug_flag_str in os.environ and os.environ[debug_flag_str] == 'True':
                print()
                printT(f"Test end. Please set os.environ['{debug_flag_str}'] = \"False\"")
                break

            printT("Waiting 60s...")
            time.sleep(60)


if __name__ == "__main__":

    # 接口
    os.environ["JDLITE_LOG_API"] = ""
    # wxpusher通知
    os.environ["WXPUSHER_APP_TOKEN"] = ""
    os.environ["WXPUSHER_UID"] = ""
    # 调试时为True，部署时为False
    os.environ['DEBUG_15_8'] = "False"

    # 建议3号起步
    os.environ["JD_COOKIE"] = "&".join([
        'pt_key=xxxxxxx;pt_pin=xxxxxxx;',
        'pt_key=xxxxxxx;pt_pin=xxxxxxx;',
        'pt_key=xxxxxxx;pt_pin=xxxxxxx;'
    ])

    loopForDays(exchangeCouponsMayMonthV3,
                second_ahead=0.4,
                sleep_time=0.08,
                thread_number=12,
                coupon_type="15-8",
                clock_list=[9, 12, 15, 18, 20],
                url="https://api.m.jd.com/client.action?functionId=lite_newBabelAwardCollection&client=wh5&clientVersion=1.0.0",
                debug_flag_str="DEBUG_15_8"
                )
