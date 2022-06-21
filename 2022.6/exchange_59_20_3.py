#!/bin/env python3
# -*- coding: utf-8 -*
'''
项目名称:exchange_59_20_3.py
Author: yangyang
功能：
Date: 2022-5-23
cron: 0 59 9,13,19,21,23 * * *
new Env("京东59减20点点券2");
'''

from exchange_lib import *


def exchangeThread(cookie, request_url, mask_dict, thread_id, thread_number):
    # 当前时间段抢空；；活动结束了
    # process_stop_code_set = set(['D2', 'A15', 'A6'])
    # if datetime.datetime.now().strftime('%H') != '23':
    #     process_stop_code_set.add('A14')  # 今日没了
    ck = cookie

    response = requests.post(url=request_url['url'], verify=False, headers=request_url['headers'],
                             data=request_url['body'])
    result = response.json()
    result_string = result['result']['floorResult']['biz_msg'] if 'biz_msg' in result['result']['floorResult'] else result['result']['floorResult']
    printT(
        f"Thread: {thread_id}/{thread_number}, user：{getUserName(ck)}: {result_string}")

    if "成功" in result_string or "已兑换" in result_string:
        mask_dict[ck] = -1
    elif "不足" in result_string:
        mask_dict[ck] = 0


def exchangeWithoutSignOrLog(header='https://api.m.jd.com/client.action?functionId=newBabelAwardCollection&client=wh5&clientVersion=1.0.0',
        body={}, batch_size=4, other_batch_size=4, waiting_delta=0.3, sleep_time=0.03, thread_number=4, coupon_type=""):
    # TODO DEBUG
    debug_flag = False

    requests.packages.urllib3.disable_warnings()

    # TODO
    pwd = os.path.dirname(os.path.abspath(__file__)) + os.sep
    path = pwd + "env.sh"

    sid = ''.join(random.sample('123456789abcdef123456789abcdef123456789abcdef123456789abcdef', 32))
    sid_ck = ''.join(
        random.sample('123456789abcdef123456789abcdef123456789abcdef123456789abcdefABCDEFGHIJKLMNOPQRSTUVWXYZ', 43))

    cookies = os.environ["JD_COOKIE"].split('&') if "JD_COOKIE" in os.environ else []

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
    # cookies, visit_times = database.filterUsers(user_number=60, year_month_day=today_week_str)
    # cookies = cookies[:min(len(cookies), batch_size)]


    # 可修订仓库batch size，非零点抢券时更新
    # TODO DEBUG
    if datetime.datetime.now().strftime('%H') != '230':
        # cookies, visit_times = database.filterUsers(batch_size)
        # 前priority_number个号优先级相同，全部抢完后才执行后面账号，后面先按照之前版本的权重排序，每次获取user_number个ck
        cookies, visit_times = database.filterUsersWithPriorityLimited(user_number=other_batch_size,
                                                                       year_month_day=today_week_str,
                                                                       priority_number=batch_size)
    # # 23点只提前batch_size个
    else:
        # cookies = cookies[:min(batch_size, len(cookies))]
        # visit_times = []
        cookies, visit_times = database.filterUsers(user_number=batch_size, year_month_day=today_week_str)
    # cookies, visit_times = database.filterUsers(batch_size)

    # 每个线程每个账号循环次数
    if len(cookies) == 0:
        print("All accounts have the coupon today! Exiting...")
        # 当前cookies没有时，就
        return

    # 将优先级最高的ck增加一次机会，当存在的ck对应次数都一致时不增加。
    if len(cookies) > 1 and len(visit_times):
        max_times = max(visit_times)
        for i in range(len(visit_times)):
            if visit_times[i] == max_times:
                cookies.append(cookies[i])
                break

    random.shuffle(cookies)
    # cookies = cookies[-3:]
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

    if datetime.datetime.now().strftime('%H') == '19':
        waiting_delta += 0.1

    printT('Ready for coupons...')

    jd_timestamp = datetime.datetime.fromtimestamp(jdTime() / 1000)
    server_delta = (jd_timestamp - datetime.datetime.now()).total_seconds()
    printT(f"Server delay (JD server - current server): {server_delta}s.")
    if debug_flag:
        nex_time = (jd_timestamp + datetime.timedelta(minutes=1)).replace(second=0, microsecond=0)
    else:
        nex_time = (jd_timestamp + datetime.timedelta(hours=1)).replace(minute=0, second=0, microsecond=0)
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




body_dict= {
    "batchId":"859658610"
}

waiting_delta = float(os.environ['WAITING_DELTA']) if "WAITING_DELTA" in os.environ else 0.18

# exchangeCouponsMayMonthV3(header="https://api.m.jd.com/client.action?functionId=lite_newBabelAwardCollection&client=wh5&clientVersion=1.0.0", body_dict=body_dict, batch_size=5, other_batch_size=2, waiting_delta=0.25, process_number=4, coupon_type="15-8")
# exchangeWithoutSignOrLog(header="https://api.m.jd.com/client.action?functionId=lite_newBabelAwardCollection&client=wh5&clientVersion=1.0.0", body_dict=body_dict, batch_size=10, other_batch_size=5, waiting_delta=0.25, sleep_time=0.03, thread_number=20, coupon_type="15-8")
exchangeWithoutSignOrLog(header="https://api.m.jd.com/client.action?functionId=volley_ExchangeAssetFloorForColor&appid=coupon-activity&client=wh5&area=17_1381_50718_53772&geo=%5Bobject%20Object%5D&t=1653322985601&eu=5663338346331693&fv=9323932366232313",
                         body=body_dict, batch_size=6, other_batch_size=5, waiting_delta=0.37, sleep_time=0.03, thread_number=20, coupon_type="59-20(3)")