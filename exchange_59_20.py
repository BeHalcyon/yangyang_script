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
from exchange_lib import *


# def getSignAPI(functionId, body):
#     sign_api = 'http://jd19.top:1998/newlog?func=getsign'
#     Token = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJleHAiOjE2NTM1NDQ2MDksImlhdCI6MTY1MjMzNTAwOSwiaXNzIjoiYmlsaWJpbGkifQ.BeYPUnXcEAMWPNdsPNGUbZ4Ms4HlJSTByqRkkzKaIvA'
#     headers = {
#         'Accept': '*/*',
#         # "accept-encoding": "gzip, deflate, br",
#         'Content-Type': 'application/json',
#         'Authorization': 'Bearer ' + Token
#     }
#     data = {
#         'functionId': functionId,
#         'body': body
#     }
#     try:
#         res = requests.post(url=sign_api, headers=headers, json=data, timeout=30).json()
#         if res['code'] == 200:
#             return res['data']
#         else:
#             print(res['msg'])
#             return -1
#     except:
#         return -1


# def getSignAPI(functionId, body):
#     sign_api = 'http://jd.330660.xyz/api/jd/sign'
#     headers = {
#         'Content-Type': 'application/x-www-form-urlencoded',
#     }
#     data = {
#         'functionId': functionId,
#         'body': json.dumps(body)
#     }
#     res = requests.post(url=sign_api, headers=headers, data=data, timeout=30).json()
#     if res['code'] == 200:
#         # print(res)
#         return res
#     else:
#         print(res['message'])
#         return -1

def getSignAPI(functionId, body):
    if "JD_SIGN_API" in os.environ and "JD_SIGN_API_TOKEN" in os.environ:
        url = os.environ['JD_SIGN_API']
        token = os.environ['JD_SIGN_API_TOKEN']
        data = {'functionId': functionId,
                'body': json.dumps(body),
                'token': token
                }
        try:
            res = requests.post(url, data=data).json()
            return {'result': res}
        except Exception as e:
            print(e)
            exit()
    else:
        print("Please set environ first!")
        exit()


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
        result = res['result']
        functionId = result['functionId']
        rsbody = json.loads(json.dumps(result['body']))
        url = f'https://api.m.jd.com?functionId={functionId}&body=' + rsbody

        headers = {
            "Host": "api.m.jd.com",
            "cookie": cookie,
            "charset": "UTF-8",
            "user-agent": "okhttp/3.12.1;jdmall;android;version/10.1.4;build/90060;screen/720x1464;os/7.1.2;network/wifi;",
            "accept-encoding": "br,gzip,deflate",
            "cache-control": "no-cache",
            "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
            "content-length": str(len(rsbody)),
        }

        res = requests.post(url=url, headers=headers, data=result, timeout=30).json()

        if res['code'] == '0':
            if 'result' in res and 'couponList' in res['result']:
                for coupon in res['result']['couponList']:
                    if coupon['title'] != None and '每周可领一次' in coupon['title']:
                        receiveKey = coupon['receiveKey']
                        receive_dict[cookie] = receiveKey
                        return receiveKey
            # return res['result']['couponList'][0]['receiveKey']
            # for coupon in res['result']['couponList']:
            #     if coupon['title'] != None and '每周可领一次' in coupon['title']:
            #         receiveKey = coupon['receiveKey']
            #         receive_dict[cookie] = receiveKey
            #         return receiveKey
            print('没有找到59-20券的receiveKey')
            receive_dict[cookie] = ""
            return -1
        else:
            print('获取59-20券的receiveKey失败')
            receive_dict[cookie] = ""
            return -1
        # # print(res)
        # params = res['sign']
        # functionId = res['fn']
        # body = re_body.findall(params)[0]
        # params = params.replace(body, '')
        # url = f'https://api.m.jd.com?functionId={functionId}&' + params
        # # print(url)
        # headers = {
        #     "Host": "api.m.jd.com",
        #     "cookie": cookie,
        #     "charset": "UTF-8",
        #     "user-agent": "okhttp/3.12.1;jdmall;android;version/10.1.4;build/90060;screen/720x1464;os/7.1.2;network/wifi;",
        #     "accept-encoding": "br,gzip,deflate",
        #     "cache-control": "no-cache",
        #     "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
        #     "content-length": str(len(body)),
        # }
        # res = requests.post(url=url, headers=headers, data=body, timeout=30).json()
        # # print(res)
        # if res['code'] == '0':
        #     # return res['result']['couponList'][0]['receiveKey']
        #     for coupon in res['result']['couponList']:
        #         if coupon['title'] != None and '每周可领一次' in coupon['title']:
        #             receiveKey = coupon['receiveKey']
        #             receive_dict[cookie] = receiveKey
        #             return receiveKey
        #     print('没有找到59-20券的receiveKey')
        #     receive_dict[cookie] = ""
        #     return -1
        # else:
        #     print('获取59-20券的receiveKey失败')
        #     receive_dict[cookie] = ""
        #     return -1


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
        result = res['result']
        data = json.loads(json.dumps(result['body']))
        functionId = result['functionId']
        url = f'https://api.m.jd.com?functionId={functionId}&body=' + data
        return (url, result)

        # params = res['sign']
        # functionId = res['fn']
        # body = re_body.findall(params)[0]
        # params = params.replace(body, '')
        # url = f'https://api.m.jd.com?functionId={functionId}&' + params
        # # return [url, body]
        # return (url, body)


def receiveNecklaceCouponWithLoop(cookies, api_dict, loop_times, mask_dict, process_id=0, process_number=1):
    headers = {
        "Host": "api.m.jd.com",
        "cookie": '',
        "charset": "UTF-8",
        "user-agent": "okhttp/3.12.1;jdmall;android;version/10.1.4;build/90060;screen/720x1464;os/7.1.2;network/wifi;",
        # "user-agent": userAgent(),
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
            # elif "未登录" in target_info:
            #     mask_dict[cookie] = -2


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


def receiveNecklaceCouponThread(cookie, api_para, mask_dict, thread_id=0, thread_number=1):
    headers = {
        "Host": "api.m.jd.com",
        "cookie": '',
        "charset": "UTF-8",
        "user-agent": "okhttp/3.12.1;jdmall;android;version/10.1.4;build/90060;screen/720x1464;os/7.1.2;network/wifi;",
        # "user-agent": userAgent(),
        "accept-encoding": "br,gzip,deflate",
        "cache-control": "no-cache",
        "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
        "content-length": '',
    }

    url, body = api_para
    headers["cookie"] = cookie
    headers["content-length"] = str(len(body))
    prefix_info = f"Process: {thread_id + 1}/{thread_number}, User: {getUserName(cookie)}, "
    target_info = ""
    res = requests.post(url=url, headers=headers, data=body).json()
    try:
        if res['code'] == '0' and res['msg'] == '响应成功':
            target_info = res['result']['desc']
            # if res['result']['optCode'] == '9000':
            #     desc = res['result']['desc']
            #     quota = res['result']['couponInfoList'][0]['quota']
            #     discount = res['result']['couponInfoList'][0]['discount']
            #     endTime = res['result']['couponInfoList'][0]['endTime']
            #     timeStamp = int(endTime) / 1000
            #     timeArray = time.localtime(timeStamp)
            #     otherStyleTime = time.strftime("%Y-%m-%d", timeArray)
            #     target_info = f'{desc}，满{quota}减{discount}({otherStyleTime}过期)'
            # else:
            #     target_info = res['result']['desc']
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
            "type": os.environ['DATABASE_TYPE'],
            "host": os.environ['DATABASE_HOST'],  # 数据库主机地址
            "port": os.environ['DATABASE_PORT'],
            "user": os.environ['DATABASE_USER'],  # 数据库用户名
            "passwd": os.environ['DATABASE_PASSWD'],  # 数据库密码
            "database": os.environ['DATABASE_DATABASE']
        }
    else:
        database_dict = {
            'type': 'sqlite',
            'name': "filtered_cks.db"
        }
    # 存入数据库
    database = SQLProcess("cks_59_20_" + time.strftime("%Y%W"), database_dict)
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
    # cookies, visit_times = database.filterUsers(user_number=60, year_month_day=today_week_str)
    cookies = cookies[:min(len(cookies), batch_size)]
    # cookies = cookies[-3:]
    print("\nAccount ready to run：")
    print("\n".join([getUserName(ck) for ck in cookies]), '\n')

    # 如果是23点，需要等待到0点后执行
    is_23_hour = datetime.datetime.now().strftime('%H') == '23'
    if is_23_hour:
        jd_timestamp = datetime.datetime.fromtimestamp(jdTime() / 1000)
        if not is_debug:
            nex_hour = (jd_timestamp + datetime.timedelta(hours=1)).replace(minute=0, second=0, microsecond=0)
        else:
            nex_hour = (jd_timestamp + datetime.timedelta(minutes=1)).replace(second=0, microsecond=0)
        waiting_time = (nex_hour - jd_timestamp).total_seconds()
        printT(f"Waiting to 00:00, waiting {waiting_time}s...")
        time.sleep(max(waiting_time - 0.01, 0))

        cur_index = 0
        while cur_index < 200:
            receive_key_dict = {}
            getCcFeedInfo(cookies[-1], receive_key_dict)
            if len(receive_key_dict[cookies[-1]]):
                printT("Find receive key. Continuing...")
                break
            else:
                printT("No receive key found. Waiting 3s...")
                time.sleep(3000)
            cur_index += 1

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
    if not is_23_hour:
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
        pool.apply_async(receiveNecklaceCouponWithLoop,
                         args=(cookies.copy(), api_dict, loop_time, mask_dict, i, process_number,))
        time.sleep(0.08)
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
        elif state == -2:
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


# 多进程改为多线程
def exchangeV3(batch_size=4, waiting_delta=0.26, loop_times=4, sleep_time=0.03):
    # TODO DEBUG
    is_debug = False
    # # TODO DEBUG
    # printT("Waiting to 22:00")
    # time.sleep(8700)

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
            "type": os.environ['DATABASE_TYPE'],
            "host": os.environ['DATABASE_HOST'],  # 数据库主机地址
            "port": os.environ['DATABASE_PORT'],
            "user": os.environ['DATABASE_USER'],  # 数据库用户名
            "passwd": os.environ['DATABASE_PASSWD'],  # 数据库密码
            "database": os.environ['DATABASE_DATABASE']
        }
    else:
        database_dict = {
            'type': 'sqlite',
            'name': "filtered_cks.db"
        }
    # 存入数据库
    database = SQLProcess("cks_59_20_" + time.strftime("%Y%W"), database_dict)
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
    # cookies, visit_times = database.filterUsers(user_number=60, year_month_day=today_week_str)
    cookies = cookies[:min(len(cookies), batch_size)]
    random.shuffle(cookies)
    # cookies = cookies[-3:]
    print("\nAccount ready to run：")
    print("\n".join([getUserName(ck) for ck in cookies]), '\n')

    # 如果是23点，需要等待到0点后执行
    is_23_hour = datetime.datetime.now().strftime('%H') == '23'
    if is_23_hour:
        jd_timestamp = datetime.datetime.fromtimestamp(jdTime() / 1000)
        if not is_debug:
            nex_hour = (jd_timestamp + datetime.timedelta(hours=1)).replace(minute=0, second=0, microsecond=0)
        else:
            nex_hour = (jd_timestamp + datetime.timedelta(minutes=1)).replace(second=0, microsecond=0)
        waiting_time = (nex_hour - jd_timestamp).total_seconds()
        printT(f"Waiting to 00:00, waiting {waiting_time}s...")
        time.sleep(max(waiting_time - 0.01, 0))

        cur_index = 0
        while cur_index < 200:
            receive_key_dict = {}
            getCcFeedInfo(cookies[-1], receive_key_dict)
            if len(receive_key_dict[cookies[-1]]):
                printT("Find receive key. Continuing...")
                break
            else:
                printT("No receive key found. Waiting 3s...")
                time.sleep(3000)
            cur_index += 1

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
    # loop_time = 1
    # process_number = 4
    api_number_for_each_cookie = loop_times
    printT(
        f"Generating {len(cookies) * api_number_for_each_cookie} api links ({len(cookies)} cookies, {len(cookies) * api_number_for_each_cookie} threads, and {loop_times} times)...")
    # api_dict = {}
    # for cookie in cookies:
    #     # get url and body for each receive with api_number_for each_cookie times
    #     api_dict[cookie] = []
    #     for t_id in range(len(cookies)):
    #         buffer = []
    #         for t in range(loop_times):
    #             buffer.append(getReceiveNecklaceCouponSign(receive_key=receive_key_dict[cookie]))
    #         api_dict[cookie].append(buffer)

    thread_api_arrays = []
    for t in range(loop_times):
        for cookie in cookies:
            thread_api_arrays.append((cookie, getReceiveNecklaceCouponSign(receive_key=receive_key_dict[cookie])))

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
    if not is_23_hour:
        # Debug: 测试时关闭
        if not is_debug:
            nex_hour = (jd_timestamp + datetime.timedelta(hours=1)).replace(minute=0, second=0, microsecond=0)
        else:
            nex_hour = (jd_timestamp + datetime.timedelta(minutes=1)).replace(second=0, microsecond=0)
        waiting_time = (nex_hour - jd_timestamp).total_seconds()
        printT(f"Waiting {waiting_time}s...")
        # waiting_delta = 0.26
        # time.sleep(max(waiting_time - waiting_delta - server_delta, 0))
        time.sleep(max(waiting_time - waiting_delta, 0))

    # mask_dict = multiprocessing.Manager().dict()
    # for ck in cookies:
    #     mask_dict[ck] = 1
    # receiveNecklaceCouponWithLoop(cookies, api_dict, loop_time, 0, process_number)
    # pool = multiprocessing.Pool(processes=process_number)
    # for i in range(process_number):
    #     cookies.insert(0, cookies.pop())
    #     pool.apply_async(receiveNecklaceCouponWithLoop,
    #                      args=(cookies.copy(), api_dict, loop_time, mask_dict, i, process_number,))
    #     time.sleep(0.08)
    # pool.close()
    # pool.join()

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

    print()
    # 将为False的ck更新为负值
    for ck, state in mask_dict.items():
        if state == -1:
            print(f"User: {getUserName(ck)} 抢到优惠券")
        elif state == 0:
            print(f"User: {getUserName(ck)} 点点券不足")
        elif state == -2:
            print(f"User: {getUserName(ck)} ck过期")

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
    api_para = getReceiveNecklaceCouponSign(receive_key_dict[cookie])
    for i in range(loop_time):
        receiveNecklaceCouponThread(cookie, api_para, mask_dict, thread_id=thread_id, thread_number=thread_number)
        time.sleep(sleep_time)
    return

# 0点特殊处理
# 多开几个线程，每个线程单独处理一个
# waiting_delta：提前多少秒开始运行
def exchange0Clock(batch_size=4, waiting_delta=0, loop_times=1, sleep_time=0.03):
    is_debug = False

    printT("Starting..." + (" (Debug Mode)" if is_debug else ""))

    cookies = os.environ["JD_COOKIE"].split('&') if "JD_COOKIE" in os.environ else []
    # get cookies from databse
    if 'DATABASE_TYPE' in os.environ and \
            'DATABASE_HOST' in os.environ and \
            'DATABASE_PORT' in os.environ and \
            'DATABASE_USER' in os.environ and \
            'DATABASE_PASSWD' in os.environ and \
            'DATABASE_DATABASE' in os.environ:
        database_dict = {
            "type": os.environ['DATABASE_TYPE'],
            "host": os.environ['DATABASE_HOST'],  # 数据库主机地址
            "port": os.environ['DATABASE_PORT'],
            "user": os.environ['DATABASE_USER'],  # 数据库用户名
            "passwd": os.environ['DATABASE_PASSWD'],  # 数据库密码
            "database": os.environ['DATABASE_DATABASE']
        }
    else:
        database_dict = {
            'type': 'sqlite',
            'name': "filtered_cks.db"
        }
    # 存入数据库
    database = SQLProcess("cks_59_20_" + time.strftime("%Y%W"), database_dict)
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
            threading.Thread(target=receiveKeyAndNecklaceCoupon, args=(cookie, mask_dict, loop_times, sleep_time, i, len(cookies)))
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

    print()
    # 将为False的ck更新为负值
    for ck, state in mask_dict.items():
        if state == -1:
            print(f"User: {getUserName(ck)} 抢到优惠券")
        elif state == 0:
            print(f"User: {getUserName(ck)} 点点券不足")
        elif state == -2:
            print(f"User: {getUserName(ck)} ck过期")

    print('\nDatabase after updating：')
    database.printAllItems()
    database.close()

    printT("Ending...")


if __name__ == '__main__':
    # freeze_support()
    # exchangeV2(batch_size=3, waiting_delta=0.23)
    # exchange(batch_size=3, waiting_delta=0.23, process_number=4)
    # exchange(batch_size=3, waiting_delta=0.45, process_number=4)


    # 20220518 抢到3，会火爆，说明间隔可以。
    # exchangeV3(batch_size=3, waiting_delta=0.4, loop_times=4, sleep_time=0.025)

    # 20220520 10点场：waiting_delta=0.4，sleep_time=0.025正常
    # 14点场：waiting_delta=0.4，sleep_time=0.025 过早，存在火爆，建议修改为waiting_delta=0.3, sleep_time=0.035


    cur_hour = datetime.datetime.now().strftime('%H')
    if cur_hour != "23":
        exchangeV3(batch_size=3, waiting_delta=0.4, loop_times=4, sleep_time=0.035)
    else:
        # 0点场，每个线程负责一个号。
        exchange0Clock(batch_size=6, waiting_delta=1, loop_times=1, sleep_time=0.03)