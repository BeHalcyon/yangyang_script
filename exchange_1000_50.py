#!/bin/env python3
# -*- coding: utf-8 -*
'''
项目名称:exchange_15_8_test.py
Author: yangyang
功能：
Date: 2022-5-7
cron: 20 59 0,23 * * *
new Env("极速版1000减50");
'''

from exchange_lib import *


body_dict = {
    "activityId":"21Shup6BDitJApvnfuc8AjHnzfZ4",
    "from":"H5node",
    "scene":"1",
    "args":"key=22FE59D3730027DFB458F3BC9C35D73D523716F29A63144DB6A29C8A7BB889D99B36C7E79A04A9A53C14B4BB8B7513D4_bingo,roleId=52E158CAAD1045488275F9E4FBEFB1169D7C4A1DE1AF6DBEFE9BA2AF61D484A4EB6955FA4918C9211ACE5834B033589E5CFF3A90CDAFF2423EBD8FF8FFC668A4717CBA40BA903AC6EE009254B309C57398C8BE5AFB71D22D53CFD2D7C302E05DD0DDF4000E1BA356848FE1CA1E7E90F579FE7C4B3B6C9B51889F98CC3B815F47E9E4D2AB996AA49673D37E244FE516427C3E65A7E9DE2AAF73752FA58B0CCFD8AD5179B2E1F7A0905DA8F7399C85E92E_bingo",
    "actKey":"22FE59D3730027DFB458F3BC9C35D73D523716F29A63144DB6A29C8A7BB889D99B36C7E79A04A9A53C14B4BB8B7513D4_bingo"
}

waiting_delta = float(os.environ['WAITING_DELTA']) if "WAITING_DELTA" in os.environ else 0.18

# 优先前4个号，全部抢到后从后面每次执行2个号
# exchangeCouponsMayMonthV2(header="https://api.m.jd.com/client.action?functionId=lite_newBabelAwardCollection&client=wh5&clientVersion=1.0.0", body_dict=body_dict, batch_size=5, other_batch_size=2, waiting_delta=0.25, process_number=4, coupon_type="15-8")

exchangeCouponsMayMonthV3(header="https://api.m.jd.com/client.action?functionId=lite_newBabelAwardCollection&client=wh5&clientVersion=1.0.0", body_dict=body_dict, batch_size=7, other_batch_size=10, waiting_delta=0.20, sleep_time=0.025, thread_number=14, coupon_type="1000-50")