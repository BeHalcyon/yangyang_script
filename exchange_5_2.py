#!/bin/env python3
# -*- coding: utf-8 -*
'''
项目名称:exchange_5_2.py
Author: yangyang
功能：
Date: 2022-3-21
cron: 30 59 6,8,11,17 * * *
new Env("极速版5减2(python)");
'''

from exchange_lib import exchangeCoupons

body = r"body=%7B%22activityId%22%3A%223H885vA4sQj6ctYzzPVix4iiYN2P%22%2C%22scene%22%3A%221%22%2C%22args%22%3A%22key%3D64616D6FB9F745A939AEBE59B5331E98A02F7F3EBE7E2A8C6BC39900A5FB433C383A3885B1901C0036F186675FDB6B40_bingo%2CroleId%3D454CDE7D149EE1DA28FDC5C9AD4D3FF6_bingo%2CstrengthenKey%3DE69C4C9B08504F0E61532E94C2391A4F3C8C17E33845A8E820806A9C43EC1E9A491F137D4E80D894F6D14060E284A36C_bingo%22%7D"
exchangeCoupons(body=body)