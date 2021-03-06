#!/bin/env python3
# -*- coding: utf-8 -*
'''
项目名称:exchange_5_2.py
Author: yangyang
功能：
Date: 2022-5-7
cron: 20 59 8,21 * * *
new Env("极速版5减2");
'''

from exchange_lib import *

body_dict = {
    'activityId': 'vN4YuYXS1mPse7yeVPRq4TNvCMR',
    'scene': '1',
    'args': 'key=BCE52145EC2FBDDE212899674C8CA1C12A3A133EEA5D70CB9D998AF6B3F4648C22AC20BFEB2B797D1292322C150A0DC2_bingo,roleId=3FE9EECAAA41B666E4FFAF79F20E211241BC51D1C03478640D4EF32FA22832B7C93468B462C8C368D7E33CA18F54891E8F724E3FA38C39E3AFF697601E6A963307103764559652634BA6CCE6381F1828595FEF41EB51E1BA767BD9A65C50A2C7BA67856B8EF2F3832993B5BAA153318C36E547F9705253F5F49D90ED1E5295A18B7209C46177FD1360CED7B842EBDC3902E0E52602C222F01FC09EF875F6D80692D6C2B0BD424A95462C410A7FCE02B6_bingo,strengthenKey=E69C4C9B08504F0E61532E94C2391A4F3C8C17E33845A8E820806A9C43EC1E9A5F11FBCC2FD05131CD8992A7B435F3C6_bingo'
}

# 优先前4个号，全部抢到后从后面每次执行4个号
# exchangeCouponsMayMonthV2(header="https://api.m.jd.com/client.action?functionId=lite_newBabelAwardCollection&client=wh5&clientVersion=1.0.0", body_dict=body_dict, batch_size=6, waiting_delta=0.2, process_number=4)

exchangeCouponsMayMonthV3(header="https://api.m.jd.com/client.action?functionId=lite_newBabelAwardCollection&client=wh5&clientVersion=1.0.0", body_dict=body_dict, batch_size=8, other_batch_size=10, waiting_delta=0.25, sleep_time=0.025, thread_number=20, coupon_type="5-2")
