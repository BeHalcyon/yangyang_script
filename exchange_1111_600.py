#!/bin/env python3
# -*- coding: utf-8 -*
'''
项目名称: exchange_1111_600.py
Author: yangyang
功能：
Date: 2022-5-23
cron: 10 59 19 * * *
new Env("金融1111减600");
'''
from exchange_lib import *



body = {"activityId":"27ymdYiFp6M7sA1WkbULRVuERRbX","gridInfo":"","scene":"3","args":"","platform":"1","orgType":"2","openId":"-1","pageClickKey":"-1","eid":"","fp":"","shshshfp":"","shshshfpa":"","shshshfpb":"","childActivityUrl":"https%3A%2F%2Fprodev.m.jd.com%2Fmall%2Factive%2F27ymdYiFp6M7sA1WkbULRVuERRbX%2Findex.html%3F","userArea":"-1","client":"-1","clientVersion":"-1","uuid":"-1","osVersion":"-1","brand":"-1","model":"-1","networkType":"-1","jda":"122270672.16120607038311261864002.1612060703.1652575925.1653311685.108","sdkToken":"","token":"","jstub":"","pageClick":"Babel_Coupon","actKey":"E560E80A2A3538A7376056BA278BDCF085FC7808DFDFE4E9C2F467EAD8D02049C3364F6CD21639661E6D7E7C263B274ACF810C2EB1D250E74511D057DACDD6125D9195816BEAF1C15E8BF8D4BF50F63934EE99DDBDC8291FF8B501D936A78AEAA2657B80E3AC97A28DFF9080FBDD811F8BF90A9907EF432E2C7A4388C0E91F9B3ADDF207C6AA84F6249955712B7A71CA346968D95E869BDFE7B0754E4A8621023C42C8EA5C592BE376B694D770224C43_bingo","couponSource":"manual","couponSourceDetail":"-100","channel":"通天塔会场","batchId":"","headArea":"605715ec560d6508f7403b91b677d79c","mitemAddrId":"","geo":{"lng":"","lat":""},"addressId":"","posLng":"","posLat":"","focus":"","innerAnchor":"","cv":"2.0","floor_id":"77501330"}


exchangePayCoupon(header="https://api.m.jd.com/client.action?functionId=newBabelAwardCollection&screen=800*1324&client=wh5&clientVersion=1.0.0", body=body, batch_size=10, other_batch_size=5, waiting_delta=0.25, sleep_time=0.03, thread_number=20, coupon_type="1111-600")