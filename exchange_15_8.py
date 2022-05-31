#!/bin/env python3
# -*- coding: utf-8 -*
'''
项目名称:exchange_15_8_test.py
Author: yangyang
功能：
Date: 2022-5-7
cron: 20 59 8,11,14,17,19 * * *
new Env("极速版15减8");
'''

from exchange_lib import *

body_dict = {
    'activityId': '3H885vA4sQj6ctYzzPVix4iiYN2P',
    'scene': '1',
    'args': 'key=DF6500A60EBB047C1539292254D320D7E80F9297D19486370D6A0DD220E76A1CD91818B1BCEE491D10789D7765041113_bingo,roleId=A921D0996A757D3D319487D17C0F25FE01264B7B8DA4DBEF981EF390D1DC02E92308FBC1CF805C8B6550E0A1EED8671F5360D7210975255E5A17758A1D4815AB567D73B11DD737D321A8D6DAD3B6E47D9856DB2370DFDE42DF7A403051EAE598426A548597D1A8C8B06DB2408647136E62AB87E9BDA89DC607FFF91F49DDF2D7D5654AE896C595FB0166D7DDD65C69887601704ADA6163C9D9D6BEB403BAD565_bingo,strengthenKey=3FE987FADD098B5D46BA38B21875A5EBD8C02F19572CB3C5CC0385902CD416A223A89D9BE16CD64801ED6D818465540C_bingo'
}

waiting_delta = float(os.environ['WAITING_DELTA']) if "WAITING_DELTA" in os.environ else 0.18

# 优先前4个号，全部抢到后从后面每次执行2个号
# exchangeCouponsMayMonthV2(header="https://api.m.jd.com/client.action?functionId=lite_newBabelAwardCollection&client=wh5&clientVersion=1.0.0", body_dict=body_dict, batch_size=5, other_batch_size=2, waiting_delta=0.25, process_number=4, coupon_type="15-8")

exchangeCouponsMayMonthV3(header="https://api.m.jd.com/client.action?functionId=lite_newBabelAwardCollection&client=wh5&clientVersion=1.0.0", body_dict=body_dict, batch_size=6, other_batch_size=5, waiting_delta=0.20, sleep_time=0.025, thread_number=14, coupon_type="15-8")