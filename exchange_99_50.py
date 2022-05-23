#!/bin/env python3
# -*- coding: utf-8 -*
'''
项目名称: exchange_99_50.py
Author: yangyang
功能：
Date: 2022-5-23
cron: 10 59 19 * * *
new Env("金融99减50");
'''

from exchange_lib import *

body = {"activityId":"27ymdYiFp6M7sA1WkbULRVuERRbX",
        "gridInfo":"",
        "scene":"3",
        "args":"",
        "platform":"1",
        "orgType":"2",
        "openId":"-1",
        "pageClickKey":"-1",
        "eid":"",
        "fp":"",
        "shshshfp":"",
        "shshshfpa":"",
        "shshshfpb":"",
        "childActivityUrl":"https%3A%2F%2Fprodev.m.jd.com%2Fmall%2Factive%2F27ymdYiFp6M7sA1WkbULRVuERRbX%2Findex.html%3F",
        "userArea":"-1","client":"-1",
        "clientVersion":"-1","uuid":"-1",
        "osVersion":"-1","brand":"-1","model":"-1",
        "networkType":"-1","jda":"","sdkToken":"","token":"",
        "jstub":"","pageClick":"Babel_Coupon",
        "actKey":"E560E80A2A3538A7376056BA278BDCF0B67E2F491B769DF9EA2B6168B51364DD2B3ABEE7C3F5F0F05A0C836E0F22324C0B26938122249B2DEE8BBCA61C6D9D9C8D6631CDA374DF7F977B6E88857EA9FDCE43D4B767C1E332B2E507F283FF23DAD7AE79AFC6B68FC16D55E396EDCFA5E9EA97F2091F57F890016A20054FECC746979A20858D3DD62A9F9A60D627F62D379C4D2A854246CF4C06217F9B7C558AD2D46F55CA16F531C210224C38381DE2BE_bingo",
        "couponSource":"manual","couponSourceDetail":"-100","channel":"通天塔会场","batchId":"","headArea":"605715ec560d6508f7403b91b677d79c","mitemAddrId":"","geo":{"lng":"","lat":""},"addressId":"","posLng":"","posLat":"","focus":"","innerAnchor":"","cv":"2.0",
        "floor_id":"77501330"
        }


exchangePayCoupon(header="https://api.m.jd.com/client.action?functionId=newBabelAwardCollection&screen=800*1324&client=wh5&clientVersion=1.0.0", body=body, batch_size=6, other_batch_size=5, waiting_delta=0.25, sleep_time=0.3, thread_number=20, coupon_type="99-50")