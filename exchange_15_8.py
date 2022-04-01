#!/bin/env python3
# -*- coding: utf-8 -*
'''
项目名称:exchange_15_8.py
Author: yangyang
功能：
Date: 2022-3-21
cron: 45 59 8,11,14,16,19 * * *
new Env("极速版15减8(python)");
'''

from exchange_lib import *

body = r"body=%7B%22activityId%22%3A%223H885vA4sQj6ctYzzPVix4iiYN2P%22%2C%22scene%22%3A%221%22%2C%22args%22%3A%22key%3D79F6166D6F9BB11C9ED9696C6E30D9C1D392C277F9B79AB559E9868E1EE0910308189D1B2C9883FC5560EDA0CD002985_bingo%2CroleId%3DC6DCE94E14C0BEE454EA964509F4B26C_bingo%2CstrengthenKey%3D19F512DCD8EE34ABE9C4FB4A92C2F42A3E4F1D227F16BC3264497B20B54D33F5_bingo%22%7D"
exchangeCoupons(body=body)