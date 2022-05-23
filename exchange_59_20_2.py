#!/bin/env python3
# -*- coding: utf-8 -*
'''
项目名称:exchange_59_20.py
Author: yangyang
功能：
Date: 2022-5-12
cron: 0 58 9,13,17,21,23 * * *
new Env("京东59减20(2)");
'''

from exchange_lib import *



# 不需要点点券兑换的59-20
def exchangeWithoutNecklaceCoupon(header='https://api.m.jd.com/client.action?functionId=newBabelAwardCollection&client=wh5&clientVersion=1.0.0',
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

    cookies = os.environ["JD_COOKIE"].split('&')

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
    database = SQLProcess(json.dumps(body).replace('=', '').replace(',', '').replace('{', '').replace('}', '').replace('"', '').replace(' ', '').replace(':', ''), database_dict)
    # 插入所有数据，如果存在则更新
    insert_start = time.time()
    for i, ck in enumerate(cookies):
        database.insertItem(ck, time.time(), str(datetime.date.today()), len(cookies) - i)
    insert_end = time.time()
    print("\nTime for updating/inserting cookie database: {:.2f}s\n".format(insert_end - insert_start))

    print('\nThe database before updating: ')
    database.printTodayItems()

    # 可修订仓库batch size，非零点抢券时更新
    if datetime.datetime.now().strftime('%H') != '23':
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

    # 将优先级最高的ck增加一次机会，当存在的ck对应次数都一致时不增加。
    if len(cookies) > 1 and len(visit_times):
        max_times = max(visit_times)
        for i in range(len(visit_times)):
            if visit_times[i] == max_times:
                cookies.append(cookies[i])
                break


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

if __name__ == "__main__":


    body_dict = {"activityId":"csTQSAnfQypSN7KeyCwJWthE6aV","from":"H5node","scene":"1","args":"key=m9a6teebr9iaa0lfc4m6sbb4a6351303,roleId=76337067"}
    exchangeCouponsMayMonthV3(
        header="https://api.m.jd.com/client.action?functionId=lite_newBabelAwardCollection&client=wh5&clientVersion=1.0.0",
        body_dict=body_dict, batch_size=6, other_batch_size=5, waiting_delta=0.25, sleep_time=0.025, thread_number=20,
        coupon_type="59-20(2)")