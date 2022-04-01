#!/bin/env python3
# -*- coding: utf-8 -*
'''
项目名称:exchange_10_4.py
Author: yangyang
功能：
Date: 2022-3-21
cron: 45 59 7,10,13,19 * * *
new Env("极速版10减4(python)");
'''

from exchange_lib import *

body = r"body=%7B%22activityId%22%3A%22vN4YuYXS1mPse7yeVPRq4TNvCMR%22%2C%22scene%22%3A%221%22%2C%22args%22%3A%22key%3D440A3074D8054F656466EE989DEF40E4DE6342B45A4AB5D48889C7B31DD4E52ED6EB7F5C0174376325C72F3C5D85C6AA_bingo%2CroleId%3DB1781EF2C2537FB0E4A5B23AC99529A4_bingo%2CstrengthenKey%3D19F512DCD8EE34ABE9C4FB4A92C2F42AA1447D26BB4D8F8F1ADD929FC07559FC_bingo%22%7D"
exchangeCoupons(body=body)