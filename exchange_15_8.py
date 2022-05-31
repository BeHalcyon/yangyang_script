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
    'args': 'key=4C884367B622BB96ABD488103A5036F58B08100D4FEC967D97AA8854BC13AF4A50BE6F7B01529B9D56C52BEAB5EB5235_bingo,roleId=A921D0996A757D3D319487D17C0F25FE701307BE103D49F3D1562C7CF5D02F01F1043E437093D585B4730F630A66804F8AE429E9F2C40EE1F0580E482F388FEEF1F5A8A69753844555247364707E6E41040F01DEE945DF4C10432FB4875EA6DF48164CC736ACE898EE9E8947855DBC30CD8BF4D53E7EA1B873BAAE1052D9BB9748A8F83F1E3CD76509AFB2939FC10B6AE2ADCB50653791DF313F8F7BF0AF7AE7_bingo,strengthenKey=3FE987FADD098B5D46BA38B21875A5EBD8C02F19572CB3C5CC0385902CD416A23D357AD5C32B073932D1986E4D335028_bingo'
}

waiting_delta = float(os.environ['WAITING_DELTA']) if "WAITING_DELTA" in os.environ else 0.18

# 优先前4个号，全部抢到后从后面每次执行2个号
# exchangeCouponsMayMonthV2(header="https://api.m.jd.com/client.action?functionId=lite_newBabelAwardCollection&client=wh5&clientVersion=1.0.0", body_dict=body_dict, batch_size=5, other_batch_size=2, waiting_delta=0.25, process_number=4, coupon_type="15-8")

exchangeCouponsMayMonthV3(header="https://api.m.jd.com/client.action?functionId=lite_newBabelAwardCollection&client=wh5&clientVersion=1.0.0", body_dict=body_dict, batch_size=6, other_batch_size=5, waiting_delta=0.20, sleep_time=0.025, thread_number=14, coupon_type="15-8")