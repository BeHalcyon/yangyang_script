#!/bin/env python3
# -*- coding: utf-8 -*
'''
项目名称:exchange_29_8.py
Author: yangyang
功能：
Date: 2022-3-21
cron: 45 59 8,11,14,16,19 * * *
new Env("极速版29减8(python)");
'''

from exchange_lib import *

body = r"body=%7B%22activityId%22%3A%223H885vA4sQj6ctYzzPVix4iiYN2P%22%2C%22scene%22%3A%221%22%2C%22args%22%3A%22key%3D6102ED3D9BC7C8DFF14D1A36FFA89602070B138DF76D200B6FA411359FBAD50B1FD83787E7C9BEF8843A4631ADF6C792_bingo%2CroleId%3D20E136F5EB78E9D323CEA65000B08718_bingo%2CstrengthenKey%3D19F512DCD8EE34ABE9C4FB4A92C2F42A65327F2097264F7157C058E713F98BE4_bingo%22%7D"
exchangeCoupons(body=body)