#!/bin/env python3
# -*- coding: utf-8 -*
'''
项目名称:exchange_59_20.py
Author: yangyang
功能：
Date: 2022-5-12
cron: 0 58 8,11,14,17,19 * * *
new Env("京东59减20抢券");
'''

import random
import requests
import re
import sys
import datetime
import multiprocessing
import time
from urllib.parse import quote, unquote



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
    res = getSignAPI('getCcFeedInfo', body) #st sv sign
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
        r = re.compile(r"pt_pin=(.*?);")    #指定一个规则：查找pt_pin=与;之前的所有字符,但pt_pin=与;不复制。r"" 的作用是去除转义字符.
        userName = r.findall(cookie)        #查找pt_pin=与;之前的所有字符，并复制给r，其中pt_pin=与;不复制。
        #print (userName)
        userName = unquote(userName[0])     #r.findall(cookie)赋值是list列表，这个赋值为字符串
        #print(userName)
        return userName
    except Exception as e:
        print(e,"cookie格式有误！")
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

def receiveNecklaceCouponWithLoop(cookies, api_dict, loop_times, process_id=0, process_number=1):
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
            prefix_info = f"账户：{getUserName(cookie)},进程：{process_id + 1}/{process_number},循环：{t + 1}/{loop_times}："
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


def receiveNecklaceCoupon(url, body, cookie):
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
                msg = f'{desc}，满{quota}减{discount}({otherStyleTime}过期)'
                printT(msg)
            else:
                printT(res['result']['desc'])
        else:
            printT(res['msg'])
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
    # 每个cookie的receiveKey不一样
    cookies = os.environ["JD_COOKIE"].split('&')
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
    printT(f"{len(cookies)} receive keys have been generated. {len(cookies) - len(filtered_cookies)} invalid receive keys have been filtered...")
    cookies = filtered_cookies

    # the api_dict is a dict of item, each of which includes 'url' and 'body'
    loop_time = 1
    # process_number = 4
    api_number_for_each_cookie = loop_time * process_number
    printT(f"Generating {len(cookies) * api_number_for_each_cookie} api links ({len(cookies)} cookies, {process_number} processes, and {loop_time} times)...")
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
    jd_timestamp = datetime.datetime.fromtimestamp(jdTime()/1000)
    nex_hour = (jd_timestamp + datetime.timedelta(hours=1)).replace(minute=0, second=0, microsecond=0)
    waiting_time = (nex_hour - datetime.datetime.now()).total_seconds()
    printT(f"Waiting {waiting_time}s")
    # waiting_delta = 0.26
    time.sleep(max(waiting_time - waiting_delta, 0))

    # receiveNecklaceCouponWithLoop(cookies, api_dict, loop_time, 0, process_number)
    pool = multiprocessing.Pool(processes=process_number)
    for i in range(process_number):
        random.shuffle(cookies)
        pool.apply_async(receiveNecklaceCouponWithLoop, args=(cookies.copy(), api_dict, loop_time, i, process_number, ))
        time.sleep(0.025)
    pool.close()
    pool.join()

    printT("Ending...")

exchange(batch_size=4, waiting_delta=0.26, process_number=4)