#!/bin/env python3
# -*- coding: utf-8 -*
'''
项目名称:exchange_19_5.py
Author: yangyang
功能：
Date: 2022-5-7
cron: 20 59 9,21,23 * * *
new Env("极速版19减5");
'''

from exchange_lib import *

body_dict = {
    'activityId': 'vN4YuYXS1mPse7yeVPRq4TNvCMR',
    'scene': '1',
    'args': 'key=E72F2D6FD3B257AE6EAEEF81FEF44D9C3EFB9B5E0F0E11C4562D68BDA7BA69BF5C4E716FB9BBD7B1678E83551EA3A72E_bingo,roleId=3FE9EECAAA41B666E4FFAF79F20E21120520F1A5AFE5C9E8D77BD263F6726B9E3576C6C5571777201DA90CF204F2336AB211D7BA6D0E7255BAFF71BCC9ED7782F4BB5E97DDCA47183788BB228E79E0C3717A7A407B6A09AF264D2E039E68D7F7A324A6712BDC849C70E81350EC3D18F8017F65C0C32784AA4ADF36B01FC0CF3728DBB0686C8AB96E44ED620C481364031AF452C35A2915D91C9B0DB4C58FE1F0_bingo,strengthenKey=B95D6A81ACB1760E33CCD3461D64D27E35226C092A2A7087E8B3C00CCEFB777DF39E29594032DA24BEEB7AC34D593FBC_bingo'
}

# 优先前4个号，全部抢到后从后面每次执行4个号
# exchangeCouponsMayMonthV2(header="https://api.m.jd.com/client.action?functionId=lite_newBabelAwardCollection&client=wh5&clientVersion=1.0.0", body_dict=body_dict, batch_size=4, waiting_delta=0.2, process_number=4, coupon_type="19-5")


exchangeCouponsMayMonthV3(header="https://api.m.jd.com/client.action?functionId=lite_newBabelAwardCollection&client=wh5&clientVersion=1.0.0", body_dict=body_dict, batch_size=6, other_batch_size=10, waiting_delta=0.25, sleep_time=0.025, thread_number=20, coupon_type="19-5")
