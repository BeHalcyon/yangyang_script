#!/bin/env python3
# -*- coding: utf-8 -*
'''
项目名称:exchange_9p9_6.py
Author: yangyang
功能：
Date: 2022-4-8
cron: 30 59 9 * * *
new Env("极速版9.9减6(python)");
'''

from exchange_lib import *

body = r"body=%7B%22activityId%22%3A%223H885vA4sQj6ctYzzPVix4iiYN2P%22%2C%22scene%22%3A%221%22%2C%22args%22%3A%22key%3DDE0D4055A7177661AFE7665B21D4E5BD3C77419B4D58A36B71F75F46E96856D8270B7F9DAEE7922F7017CD82E1E1B483_bingo%2CroleId%3DFBFCA24892286E5ED792986756046832_bingo%2CstrengthenKey%3D19F512DCD8EE34ABE9C4FB4A92C2F42ADBD8409383A6DA2E6E9B79F1DF132EA8_bingo%22%7D"
exchangeCoupons(body=body, batch_size=5)