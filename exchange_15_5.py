#!/bin/env python3
# -*- coding: utf-8 -*
'''
项目名称:exchange_15_5.py
Author: yangyang
功能：
Date: 2022-5-7
cron: 10 59 9,23 * * *
new Env("极速版15减5");
'''

from exchange_lib import *

body_dict = {
    'activityId': 'vN4YuYXS1mPse7yeVPRq4TNvCMR',
    'scene': '1',
    'args': 'key=751709DD793408174D56C44D3BFC3C434680AB42380C39D573683566316F1F090B3C468368A1FA0640C15E1A2A6BB25A_bingo,roleId=3FE9EECAAA41B666E4FFAF79F20E21122587E42E9489C92604E9B1CD426BF61F9DA8FF4F6F381F7CE14913B40C4A4E49DBD8A0F39C4428871CEA2BFB7AC136DBBC79AE321F4D5D092EFE0978EEEDB540EEE7D12BB491ECBE8EED47E3A2038461275DC7CE64BA016EE4FED74741BE686315495C99C4E9322C8F1B1AFD867E3599767D7054A4E0FC481F922E410D2C20FC568C5C67F6E2232124870EEC42166F6B_bingo,strengthenKey=19F512DCD8EE34ABE9C4FB4A92C2F42A83880C27EA00E5A7DF564D095F19F994_bingo'
}

# 优先前4个号，全部抢到后从后面每次执行4个号
exchangeCouponsMayMonthV2(header="https://api.m.jd.com/client.action?functionId=lite_newBabelAwardCollection&client=wh5&clientVersion=1.0.0", body_dict=body_dict, batch_size=4, waiting_delta=0.2, process_number=4, coupon_type="15-5")
