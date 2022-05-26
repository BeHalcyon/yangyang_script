# encoding: utf-8
# -*- coding: utf-8 -*
'''
项目名称:exchange_check_coupons.py
Author: yangyang
功能：
Date: 2022-5-12
cron: 0 58 14,7 * * *
new Env("优惠券通知");
'''

import requests
import json
import datetime
import time
import re
from urllib.parse import unquote
import os
import sys


def getUserName(cookie):
    try:
        return unquote(re.compile(r"pt_pin=(.*?);").findall(cookie)[0])
    except Exception as e:
        print(e, "ERROR in cookie format！")
        exit(2)


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


def generateCouponInfo(user_name, coupon_dict):
    content = user_name + " 今日优惠券如下：\n=========================================\n"
    flag = False
    for coupon_name, coupon_info in coupon_dict.items():
        if coupon_info['coupon_number']:
            content += coupon_info[
                           'coupon_type'] + coupon_name + f"：共有{coupon_info['coupon_number']}张，今日领取{coupon_info['today_get']}张，今日将过期{coupon_info['today_expire']}张！\n"
            flag = True
    if not flag:
        content = ""
    else:
        content += "=========================================\n\n"
    return content


def findCoupons(cookie):
    requests.packages.urllib3.disable_warnings()
    coupon_dict = {
        "点点券59-20": {
            "coupon_number": 0,
            "today_expire": 0,
            "today_get": 0,
            "coupon_type": ""
        },
        "15-8元": {
            "coupon_number": 0,
            "today_expire": 0,
            "today_get": 0,
            "coupon_type": "极速版"
        },
        "15-5元": {
            "coupon_number": 0,
            "today_expire": 0,
            "today_get": 0,
            "coupon_type": "极速版"
        },
        "19-5元": {
            "coupon_number": 0,
            "today_expire": 0,
            "today_get": 0,
            "coupon_type": "极速版"
        },
        "10-3元": {
            "coupon_number": 0,
            "today_expire": 0,
            "today_get": 0,
            "coupon_type": "极速版"
        },
        "10-2元": {
            "coupon_number": 0,
            "today_expire": 0,
            "today_get": 0,
            "coupon_type": "极速版"
        },
        "5-2元": {
            "today_get": 0,
            "coupon_number": 0,
            "today_expire": 0,
            "coupon_type": "极速版"
        }
    }

    url = f"https://wq.jd.com/activeapi/queryjdcouponlistwithfinance?state={1}&wxadd=1&filterswitch=1&_={int(time.time() * 1000)}&sceneval=2&g_login_type=1&callback=jsonpCBKB&g_ty=ls"
    headers = {
        'authority': 'wq.jd.com',
        "User-Agent": "jdapp;iPhone;9.4.4;14.3;network/4g;Mozilla/5.0 (iPhone; CPU iPhone OS 14_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148;supportJDSHWK/1",
        'accept': '*/*',
        'referer': 'https://wqs.jd.com/',
        'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'cookie': cookie
    }
    res = requests.get(url, headers=headers, verify=False)
    res = json.loads(res.text.replace("try{ jsonpCBKB(", "").replace("\n);}catch(e){}", ""))
    coupon_list = res['coupon']['useable']

    next_day = (datetime.datetime.now() + datetime.timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
    today = datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0).strftime("%d")
    next_day_timestamp = int(time.mktime(next_day.timetuple()) * 1000)

    for current_coupon in coupon_list:
        for coupon_name, coupon_info in coupon_dict.items():
            _res = re.compile(f"[^\d]{coupon_name.split('-')[0]}.{coupon_name.split('-')[1]}[^\d]?")
            if len(_res.findall(current_coupon['couponTitle'])):
                # if coupon_name in current_coupon['couponTitle']:
                coupon_dict[coupon_name]['coupon_number'] += 1
                expire_time = int(current_coupon['endTime'])
                # print(current_coupon)
                # today expire
                if expire_time <= next_day_timestamp:
                    coupon_dict[coupon_name]['today_expire'] += 1
                if datetime.datetime.fromtimestamp(int(current_coupon['beginTime']) / 1000.0).strftime("%d") == today:
                    coupon_dict[coupon_name]['today_get'] += 1

    coupon_content = generateCouponInfo(getUserName(cookie), coupon_dict)
    return coupon_content


if __name__ == '__main__':

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
    os.environ["WXPUSHER_APP_TOKEN"] = "AT_2us2aVEfFfvcl2zk8E3fWQwyxEgqYt6c"
    os.environ["WXPUSHER_UID"] = "UID_tsUTi2JU8CZxW7b58OryyaIdaiOW"

    summary = "优惠券速览"
    content = ""
    cookies = os.environ["JD_COOKIE"].split('&') if "JD_COOKIE" in os.environ else []
    for cookie in cookies:
        content += findCoupons(cookie)
    print(content)
    sendNotification(summary=summary, content=content)
