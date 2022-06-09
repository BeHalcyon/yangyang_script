#!/bin/env python3
# -*- coding: utf-8 -*
'''
项目名称:yangyang_59_20_3.py
Author: yangyang
功能：
Date: 2022-5-26
cron: 0 59 9,19,23 * * *
new Env("券后9.9");
'''

from exchange_lib import *


def getUserName(cookie, mask=False):
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
    # 当前时间段抢空；；活动结束了
    # process_stop_code_set = set(['D2', 'A15', 'A6'])
    # if datetime.datetime.now().strftime('%H') != '23':
    #     process_stop_code_set.add('A14')  # 今日没了
    ck = cookie

    response = requests.post(url=request_url['url'], verify=False, headers=request_url['headers'],
                             data=request_url['body'])
    result = response.json()
    print(result)
    # print(result)
    if 'result' not in result:
        if 'retMessage' in result:
            result_string = result['retMessage']
        else:
            result_string = "TODO Message."
    else:
        if 'desc' in result['result']:
            result_string = result['result']['desc']
        elif 'floorResult' in result['result']:
            if 'biz_msg' in result['result']['floorResult']:
                result_string = result['result']['floorResult']['biz_msg']
            else:
                result_string = result['result']['floorResult']
        else:
            result_string = "TODO Message2."
        # result_string =  result['result']['floorResult']['biz_msg'] if 'biz_msg' in result['result']['floorResult'] else result['result']['floorResult']
    printT(
        f"Thread: {thread_id}/{thread_number}, user：{getUserName(ck, True)}: {result_string}")

    if "成功" in result_string or "已兑换" in result_string:
        mask_dict[ck] = -1
    elif "不足" in result_string:
        mask_dict[ck] = 0


def exchangeWithoutSignOrLog(
        header='https://api.m.jd.com/client.action?functionId=newBabelAwardCollection&client=wh5&clientVersion=1.0.0',
        body={}, waiting_delta=0.3, sleep_time=0.03, thread_number=4, coupon_type=""):
    requests.packages.urllib3.disable_warnings()

    cookies = os.environ["JD_COOKIE"].split('&') if "JD_COOKIE" in os.environ else []

    if len(cookies) == 0:
        print("All accounts have the coupon today! Exiting...")
        # 当前cookies没有时，就
        return

    database_dict = {
        'type': 'sqlite',
        'name': "filtered_cks.db"
    }
    batch_size = 3
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


def exchange(
        url='https://api.m.jd.com/client.action?functionId=centerReceiveCoupon&appid=XPMSGC2019&client=m&uuid=16540613779751444237701',
        headers={},
        body={}, waiting_delta=0.3, sleep_time=0.03, thread_number=4, coupon_type=""):
    requests.packages.urllib3.disable_warnings()

    cookies = os.environ["JD_COOKIE"].split('&') if "JD_COOKIE" in os.environ else []

    if len(cookies) == 0:
        print("All accounts have the coupon today! Exiting...")
        # 当前cookies没有时，就
        return

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

    batch_size = 6
    # 存入数据库
    database = SQLProcess("cp9_9_" + time.strftime("%Y%W"), database_dict)
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

    print("\nAccount ready to run：")
    print("\n".join([getUserName(ck) for ck in cookies]), '\n')

    # 每个线程只负责一个ck
    request_url_list = []
    for process_id in range(thread_number):
        buffer_body_string = f"body={parse.quote(json.dumps(body).replace(' ', ''))}"
        headers['Cookie'] = cookies[process_id % len(cookies)]
        request_url_list.append({
            'url': url,
            'headers': headers,
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

    today_information = database.printAllItems(year_month_day=today_week_str)
    content += f"\n\n----------------------\n今日{coupon_type}优惠券账号状态如下：\n" + today_information + "----------------------\n"

    if len(coupon_type):
        sendNotification(summary=summary, content=content)

    database.close()
    printT("Ending...")


def loopForDays(url,
                headers,
                body,
                second_ahead,
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

        if not ('DEBUG_59_20_3' in os.environ and os.environ['DEBUG_59_20_3'] == 'True'):
            print("\n" + ("Waiting to " + str(next_task_start_time)).center(80, "*") + "\n")
            printT(f"Waiting {waiting_time}s.")
            time.sleep(waiting_time)

            printT(f"Starting coupon in {next_task_start_time}...")

        # exchangeWithoutSignOrLog(header=header,
        #                          body=body,
        #                          waiting_delta=second_ahead,
        #                          sleep_time=sleep_time,
        #                          thread_number=thread_number,
        #                          coupon_type=coupon_type)

        exchange(url=url,
                 headers=headers,
                 body=body,
                 waiting_delta=second_ahead,
                 sleep_time=sleep_time,
                 thread_number=thread_number,
                 coupon_type=coupon_type,
                 )


if __name__ == "__main__":
    
    url = "https://api.m.jd.com/client.action?functionId=centerReceiveCoupon&appid=XPMSGC2019&client=m&uuid=16540613779751444237701"
    headers = {
        "authority": "api.m.jd.com",
        "Accept": "*/*",
        "accept": "application/json, text/plain, */*",
        "accept-language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "content-type": "application/x-www-form-urlencoded",
        "origin": "https://h5.m.jd.com",
        "referer": "https://h5.m.jd.com/",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-site",
        "Connection": "keep-alive",
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1"
    }
    body_dict = {
        "extend": "D550270EB8017CE5A21E2296239BFEED62DF83A8550280B801D00BEF43263A3A4B6FEC15745E95CCAC610D2FED164A44B1DA7F79BF316E599EA2B24106BE59DE6B8A6160AC012ADDDE7362D4FAC56DBEA5EA86FBEC0B6379777090D3FC6C082847ABA2B1C26F0E78A475DB7E2EAC9CE9A77F3BEBEA9403EFA1D1E9E60EDC18D575F838E2BC1B086A5B0BBD0306869BCF3E7D61BEF354ECE95FE2D4C57BE6142D57823A172A2572C1A0ACE8A16CCA4D2BFC1944795FFEA00FE12584D5807DE664022D0F9B577E77CA65D5F28430A4F36E3BF1611BFA19E40CDDC876733FD3F9A8",
        "rcType": "1",
        "source": "couponCenter_app",
        "random": "4533121",
        "couponSource": "1",
        "extraData": "{\"log\":\"1654446655883~1IpFJFtqjrXMDFxc0FCejAxMQ==.QEV0dk5FRXJyQkVKeTxOBgsOdRU8NhA6BEBfd25PXUI/cARADS5zAjU9BgU7HgMmJAkcJAwOIjkyBiANDw==.6a05398f~5,1~3985E8C714D250083441B470488347909E183072~0t0pu3k~C~TBtBWRQLb28dGkFWXxUDbhZSABkLdhQCCh55FUAYQhMYEFUNGAF1Gw9sGAR0fB4AFgUIAhtNFxgUVQMfCH8ZDmsbC3IFGgAaAgEIGUwQahUXU0RfFggACBkaQUQbDxYHBwEGBQwDDgcDCwAADgAHBxMUF09XUxsPFkJFQEZFGhkaRVJYFw4UV1JGRU1BTVMVFRdEUl8WCGoNGQ0GBRUDGAcAGAMdDWgUEF1TFw4FHRZRQhoPGgYODlZVUFIFAQJaUwlWDgpXAgBUAlcBCAcKUFJaBQIFExgQX0gXAhB7UFtBThFVU0NbXQ4GFRUXQBQLBQQEDAEMBAEMAAwOAhgQW1MXAhBWGxkWUEFWEAsaWglKc3dyc3deRFVXS1hvf3thfXVxU0MQHRpbThANG3JbWVZYVxFxW1scFRUXWldHFggTWxcUEERaRxYMagMDAxQBCAJqFRdGWRMOaRNZFxQQVhsZFlcTGBBQGhkaUxUVF1UUHRZTE2UZGltYWBcOFFdSVFdeU0xGFRUXVVwTDhBEGhkaUV4bDxZBAhoDHwgXFBBUX2pCFAsWAgAaGRpQUxsPFkRQWlZeVQgMBwQKBAYHExgQXFIXAmkGFQUYBmwYEFNUWl8QDRtUFhoTWUFWGg8aUxVE~0vzqfjd\",\"sceneid\":\"couponNinePointNineHome\"}"
    }

    exchange(url=url,
             headers=headers,
             body=body_dict,
             waiting_delta=0.33,
             sleep_time=0.03,
             thread_number=12,
             coupon_type="券后9.9",
             )
