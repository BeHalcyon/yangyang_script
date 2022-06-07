#!/bin/env python3
# -*- coding: utf-8 -*
'''
项目名称:exchange_plus_coupons.py
Author: yangyang
功能：
Date: 2022-5-7
cron: 20 59 9,13,17,23 * * *
new Env("plus抢券");
'''

from exchange_lib import *

def exchangePlusCoupon(header='https://api.m.jd.com/client.action?functionId=newBabelAwardCollection&client=wh5&clientVersion=1.0.0',
        body_list=[], batch_size=4, other_batch_size=4, waiting_delta=0.3, sleep_time=0.03, thread_number=4, coupon_type=""):

    requests.packages.urllib3.disable_warnings()

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
    database = SQLProcess(body_list[0]['args'].replace('=', '').replace(',', ''), database_dict)
    # 插入所有数据，如果存在则更新
    insert_start = time.time()
    for i, ck in enumerate(cookies):
        database.insertItem(ck, time.time(), str(datetime.date.today()), len(cookies) - i)
    insert_end = time.time()
    print("\nTime for updating/inserting cookie database: {:.2f}s\n".format(insert_end - insert_start))

    print('\nThe database before updating: ')
    database.printTodayItems()

    # 可修订仓库batch size，非零点抢券时更新
    # TODO DEBUG
    if datetime.datetime.now().strftime('%H') != '230':
        # cookies, visit_times = database.filterUsers(batch_size)
        # 前priority_number个号优先级相同，全部抢完后才执行后面账号，后面先按照之前版本的权重排序，每次获取user_number个ck
        cookies, visit_times = database.filterUsersWithPriorityLimited(user_number=other_batch_size,
                                                                       year_month_day=str(datetime.date.today()),
                                                                       priority_number=batch_size)
    # 23点只提前batch_size个
    else:
        cookies = cookies[:min(batch_size, len(cookies))]
        visit_times = []

    # 每个线程每个账号循环次数
    if len(cookies) == 0:
        print("All accounts have the coupon today! Exiting...")
        # 当前cookies没有时，就
        return

    # 每个线程只负责一个ck
    request_url_list = []
    # thread_number = len(body_dict_list) * thread_number
    for process_id in range(thread_number):
        for body in body_list:
            buffer_body_string = f"body={parse.quote(json.dumps(body).replace(' ', ''))}"
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
                'body': buffer_body_string
            })

    print("\n待抢账号：")
    print("\n".join([getUserName(ck) for ck in cookies]), '\n')

    threads = []
    mask_dict = {}
    for ck in cookies:
        mask_dict[ck] = 1

    thread_number = len(body_list) * thread_number
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

    summary = f"Coupon ({coupon_type})"
    content = ""

    # 将为False的ck更新为负值
    for ck, state in mask_dict.items():
        if state <= 0:
            database.insertItem(ck, time.time(), str(datetime.date.today()), state)
        # else:
        # 当前尚未抢到时，权重+1，state为0时说明火爆，不自增
        database.addTimes(ck, str(datetime.date.today()))
        if state == -1:
            print(f"账号：{getUserName(ck)} 抢到{coupon_type}优惠券")
            content += f"账号：{getUserName(ck)} 抢到{coupon_type}优惠券\n"

    print('\n更新后数据库如下：')
    today_information = database.printTodayItems()
    content += f"\n\n----------------------\n今日抢到{coupon_type}优惠券账号如下：\n" + today_information + "----------------------\n"

    if len(coupon_type):
        sendNotification(summary=summary, content=content)

    database.close()


body_dict_list = [
    # 耳机
    {
        'activityId': '2X2rJK2NgjmEZLPanyYD1FvbxwAN',
        'scene': '1',
        'args': 'roleId=77525429,key=mdaft7e0r9i9abl6cem5s7429de45d87'
    },
    # Dior
    {
        'activityId': '2X2rJK2NgjmEZLPanyYD1FvbxwAN',
        'scene': '1',
        'args': 'roleId=77389437,key=mfa3t8e6r5ifa5l1c9m6s12390a56447'
    },
    # SK-II
    {
        'activityId': '2X2rJK2NgjmEZLPanyYD1FvbxwAN',
        'scene': '1',
        'args': 'roleId=77389441,key=m2aat1e1r7i9a1lccdmcsaaadce463f0'
    }
]

exchangePlusCoupon(header='https://api.m.jd.com/client.action?functionId=newBabelAwardCollection&client=wh5&clientVersion=1.0.0',
        body_list=body_dict_list, batch_size=4, other_batch_size=4, waiting_delta=0.3, sleep_time=0.02, thread_number=8, coupon_type="plus_coupons")
