#!/bin/env python3
# -*- coding: utf-8 -*
'''
项目名称:exchange_19_5.py
Author: yangyang
功能：
Date: 2022-3-21
cron: 45 59 6,9,14,17,20 * * *
new Env("极速版19减5(python)");
'''

from exchange_lib import *

body = r"body=%7B%22activityId%22%3A%22vN4YuYXS1mPse7yeVPRq4TNvCMR%22%2C%22scene%22%3A%221%22%2C%22args%22%3A%22key%3D13CE10DEFD75052795FFEBDA31379B65F2F22C26C5C5F0E3B8A128B978111DBB7A5BB54EBDB1373E0C35F5DEB9B67446_bingo%2CroleId%3DADAC87F1EC515A647C5357A175E3519B_bingo%2CstrengthenKey%3D19F512DCD8EE34ABE9C4FB4A92C2F42AAEFAF03A89700155D56A825B54D6675D_bingo%22%7D"
exchangeCoupons(body=body)