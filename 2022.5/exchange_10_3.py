#!/bin/env python3
# -*- coding: utf-8 -*
'''
项目名称:exchange_10_3.py
Author: yangyang
功能：
Date: 2022-5-7
cron: 10 59 15 * * *
new Env("极速版10减3");
'''

from exchange_lib import *

body_dict = {
    'activityId': 'vN4YuYXS1mPse7yeVPRq4TNvCMR',
    'scene': '1',
    'args': 'key=EDC82490F20A5D935C56A702456D489B3B9A0BF642892AE0C21FE1CC419C8F3BBED66A110B99B84B4750C2127C9846F4_bingo,roleId=3FE9EECAAA41B666E4FFAF79F20E21128C373924CDEB45F802BC863531F358CB4A26996E2C4891B41BD1AE95CFDCF825F5F65384C6E8613B4F54D21E40CA40DA8D6C8D219F45C7C0F56050FC9825723EA9DCEDA223F1B927FAD553341DB0F37357CCB292E621B930FFB3C446FC582D94A8A4A6CADA048E696604A09DCADC8C04008FD9418FFEF81D3C7585DF55EBDAC995D6B015B51786E7DC0AE9670767062B0B944F73FA9DC5C2DFB41B927B943DED_bingo,strengthenKey=E69C4C9B08504F0E61532E94C2391A4F3C8C17E33845A8E820806A9C43EC1E9AFE183C4CD0AF1C03DC7488C9405242B0_bingo'
}

# 优先前4个号，全部抢到后从后面每次执行4个号
# exchangeCouponsMayMonthV2(header="https://api.m.jd.com/client.action?functionId=lite_newBabelAwardCollection&client=wh5&clientVersion=1.0.0", body_dict=body_dict, batch_size=4, waiting_delta=0.2, process_number=4, coupon_type="10-3")


exchangeCouponsMayMonthV3(header="https://api.m.jd.com/client.action?functionId=lite_newBabelAwardCollection&client=wh5&clientVersion=1.0.0", body_dict=body_dict, batch_size=8, other_batch_size=10, waiting_delta=0.3, sleep_time=0.025, thread_number=20, coupon_type="10-3")
