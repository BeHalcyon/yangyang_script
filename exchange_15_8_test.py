#!/bin/env python3
# -*- coding: utf-8 -*
'''
项目名称:exchange_15_8_test.py
Author: yangyang
功能：
Date: 2022-5-7
cron: 30 59 8,11,14,17,19 * * *
new Env("极速版15减8测试版(python)");
'''

from exchange_lib import *
exchangeCouponsMayMonth(header="https://api.m.jd.com/client.action?functionId=newBabelAwardCollection", body_with_logs_file="/ql/scripts/XiangyangHe_yangyang_script/logs.npy", waiting_delta=0.36)