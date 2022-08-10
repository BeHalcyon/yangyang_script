
#!/bin/env python3
# -*- coding: utf-8 -*
'''
name: script_glados_checkin.py
Author: yangyang
Origin: 
Content: 
Date: 2022-3-21
cron: 0 20 11 * * *
new Env("glados签到");
'''

import os
import traceback
from typing import Optional

import requests
import json


COOKIES = os.getenv('GLADOS_COOKIE') if "GLADOS_COOKIE" in os.environ else ''

LOCAL_OUTPUT = True
BOT_TOKEN = os.getenv('BOT_TOKEN')
CHAT_ID = os.getenv('CHAT_ID')

HOST = "glados.rocks"
ORIGIN_URL = f"https://{HOST}"
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36"
BUDGET_DATA_PATH = "/ql/script/BeHalcyon_yangyang_script/budget.json"

def sendNotification(summary, content):
    if "WXPUSHER_APP_TOKEN" in os.environ and "WXPUSHER_UID" in os.environ:
        url = "http://wxpusher.zjiecode.com/api/send/message"
        body = {
            "appToken": os.environ["WXPUSHER_APP_TOKEN"],
            "content": content,
            "summary": summary,
            # "contentType": 1,
            # "topicIds": [
            #     123
            # ],
            "uids": [
                os.environ["WXPUSHER_UID"]
            ],
        }
        try:
            res = requests.post(url, json=body).json()
            if 'code' in res and res['code'] == 1000:
                print("WxPusher: Message send successfully.")
        except Exception as e:
            print(f"WxPusher: Message send failed: {e}")
    else:
        print(f"WxPusher: Message send failed: Please configure environments (WXPUSHER_APP_TOKEN and WXPUSHER_UID).")

def send_msg(msg: str):
    sendNotification(summary="glados checkin", content=msg)


def report_success(msg: str, left_days: int, plan: str, used_gb: float, total_gb: int):
    send_msg(
        '--------------------\n'
        'GLaDOS CheckIn\n'
        'Msg: ' + msg + '\n' +
        'Plan: ' + plan + ' Plan\n' +
        'Left days: ' + str(left_days) + '\n' +
        'Usage: ' + '%.3f' % used_gb + 'GB\n' +
        'Total: ' + str(total_gb) + 'GB\n' +
        '--------------------'
    )


def report_cookies_expired():
    send_msg(
        '--------------------\n'
        'GLaDOS CheckIn\n'
        'Msg: Your cookies are expired!\n'
        '--------------------'
    )


def report_checkin_error(msg: str):
    send_msg(
        '--------------------\n'
        'GLaDOS CheckIn\n'
        'Msg: Check in error!\n'
        'Error:\n' + msg + '\n' +
        '--------------------'
    )


def report_env_error(msg: str):
    send_msg(
        '--------------------\n'
        'GLaDOS CheckIn\n'
        'Msg: Running environment error!\n'
        'Error:\n' + msg + '\n' +
        '--------------------'
    )


def api_traffic():
    traffic_url = f"{ORIGIN_URL}/api/user/traffic"
    referer_url = f"{ORIGIN_URL}/console"

    with requests.get(
            traffic_url,
            headers={'cookie': COOKIES,
                     'referer': referer_url,
                     'origin': ORIGIN_URL,
                     'user-agent': UA,
                     'content-type': 'application/json;charset=UTF-8'}
    ) as r:
        return r.json()


def api_check_in() -> dict:
    check_in_url = f"{ORIGIN_URL}/api/user/checkin"
    referer_url = f"{ORIGIN_URL}/console/checkin"

    payload = {'token': 'glados.network'}

    with requests.post(
            check_in_url,
            headers={'cookie': COOKIES,
                     'referer': referer_url,
                     'origin': ORIGIN_URL,
                     'user-agent': UA,
                     'content-type': 'application/json;charset=UTF-8'},
            data=json.dumps(payload)
    ) as r:
        return r.json()


def api_status() -> dict:
    status_url = f"{ORIGIN_URL}/api/user/status"
    referer_url = f"{ORIGIN_URL}/console/checkin"

    with requests.get(
            status_url,
            headers={'cookie': COOKIES,
                     'referer': referer_url,
                     'origin': ORIGIN_URL,
                     'user-agent': UA}
    ) as r:
        return r.json()


def get_budget(vip_level: Optional[int]) -> dict:
    with open(BUDGET_DATA_PATH, 'r') as f:
        budget_info = json.load(f)
        user_budgets = [i for i in budget_info if
                        (vip_level is not None and 'vip' in i and i['vip'] == vip_level) or (vip_level is None and 'vip' not in i)]
        if len(user_budgets) > 0:
            return user_budgets[0]
        else:
            raise EnvironmentError(f'Budget info not found for this user! VIP: {vip_level}')


def run():
    check_in_response = api_check_in()
    check_in_msg = check_in_response['message']

    if check_in_msg == '\u6ca1\u6709\u6743\u9650':
        report_cookies_expired()
        return

    status_response = api_status()
    left_days = int(status_response['data']['leftDays'].split('.')[0])
    vip_level = status_response['data']['vip']

    traffic_response = api_traffic()
    used_gb = traffic_response["data"]["today"] / 1024 / 1024 / 1024

    user_budget = get_budget(vip_level)
    total_gb = user_budget['budget']
    plan = user_budget['level']

    report_success(check_in_msg, left_days, plan, used_gb, total_gb)


def main():
    try:
        run()
    except BaseException:
        report_checkin_error(traceback.format_exc())


if __name__ == '__main__':
    try:
        if COOKIES is None:
            raise EnvironmentError('Environment COOKIES not found!')
        elif not LOCAL_OUTPUT and BOT_TOKEN is None:
            raise EnvironmentError('Environment BOT_TOKEN not found!')
        elif not LOCAL_OUTPUT and CHAT_ID is None:
            raise EnvironmentError('Environment CHAT_ID not found!')
        else:
            main()
    except BaseException:
        report_env_error(traceback.format_exc())