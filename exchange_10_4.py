#!/bin/env python3
# -*- coding: utf-8 -*
'''
项目名称:exchange_10_4.py
Author: yangyang
功能：
Date: 2022-3-21
cron: 45 59 9,11,17,19 * * *
new Env("极速版10减4(python)");
'''

from exchange_lib import *

body = r"body=%7B%22activityId%22%3A%223H885vA4sQj6ctYzzPVix4iiYN2P%22%2C%22scene%22%3A%221%22%2C%22args%22%3A%22key%3D9F77A904F38D9D2EA7968850FE8E4CF8408EF50BCE7C6FF518E48C3F1453D4DDDE2267491E3A0134A4B3422E11261222_bingo%2CroleId%3DF922BBE3F2239AD921A7360D331C1010_bingo%2CstrengthenKey%3D19F512DCD8EE34ABE9C4FB4A92C2F42A01B287B27F5B68E70E7CC11BBE843EA0_bingo%22%7D"
exchangeCoupons(body=body)