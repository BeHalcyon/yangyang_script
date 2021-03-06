#!/bin/env python3
# -*- coding: utf-8 -*
'''
name: sign.py
Author: yangyang
Origin: https://github.com/Dimlitter/zju-dailyhealth-autocheck.git
Content: 添加青龙自动签到依赖
Date: 2022-3-21
cron: 0 20 8 * * *
new Env("ZJU健康打卡");
'''

import requests
import re
import json
import datetime
import time
import os
import random


# 推送tg
def push_tg(token, chat_id, desp=""):
    now = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    """
    推送消息到TG
    """
    if token == '':
        print("[注意] 未提供token，不进行tg推送！")
    elif chat_id == '':
        print("[注意] 未提供chat_id，不进行tg推送！")
    else:
        
        # server_url = "https://api.telegram.org/bot{}/sendmessage".format(token)
        server_url = "https://yangyang.halcyon.workers.dev/bot{}/sendmessage".format(token)
        params = {
            "text": '      {}'.format(str(now)) +  '\n=============================\n              ZJU健康打卡\n=============================\n' + desp,
            "chat_id": chat_id
        }
        print(server_url)
        response = requests.get(server_url, params=params)
        json_data = response.json()
 
        if json_data['ok'] == True:
            print("[{}] 推送成功。".format(now))
        else:
            print("[{}] 推送失败：{}({})".format(now, json_data['error_code'], json_data['description']))


#签到程序模块
class LoginError(Exception):
    """Login Exception"""
    pass


def get_day(delta=0):
    """
    获得指定格式的日期
    """
    today = datetime.date.today()
    oneday = datetime.timedelta(days=delta)
    yesterday = today - oneday
    return yesterday.strftime("%Y%m%d")


def take_out_json(content):
    """
    从字符串jsonp中提取json数据
    """
    s = re.search("^jsonp_\d+_\((.*?)\);?$", content)
    return json.loads(s.group(1) if s else "{}")


def get_date():
    """Get current date"""
    today = datetime.date.today() 
    return "%4d%02d%02d" % (today.year, today.month, today.day)


class ZJULogin(object):
    """
    Attributes:
        username: (str) 浙大统一认证平台用户名（一般为学号）
        password: (str) 浙大统一认证平台密码
        sess: (requests.Session) 统一的session管理
    """
    headers = {
        'user-agent': 'Mozilla/5.0 (Linux; U; Android 11; zh-CN; M2012K11AC Build/RKQ1.200826.002) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/69.0.3497.100 UWS/3.22.0.36 Mobile Safari/537.36 AliApp(DingTalk/6.0.7.1) com.alibaba.android.rimet.zju/14785964 Channel/1543545060864 language/zh-CN 2ndType/exclusive UT4Aplus/0.2.25 colorScheme/light',
    }
    # BASE_URL = "https://healthreport.zju.edu.cn/ncov/wap/default/index"
    # LOGIN_URL = "https://zjuam.zju.edu.cn/cas/login?service=http%3A%2F%2Fservice.zju.edu.cn%2F"


    def __init__(self, username, password, delay_run=False):
        self.username = username
        self.password = password
        self.delay_run = delay_run
        self.sess = requests.Session()
        
        self.TG_TOKEN = getEnvs(os.environ['TG_BOT_TOKEN'])	#TG机器人的TOKEN
        self.CHAT_ID = str(getEnvs(os.environ['TG_USER_ID']))	    #推送消息的CHAT_ID

        self.lng= os.getenv("lng")
        self.lat= os.getenv("lat")

        self.imgaddress = 'https://healthreport.zju.edu.cn/ncov/wap/default/code'
        self.BASE_URL = "https://healthreport.zju.edu.cn/ncov/wap/default/index"
        self.LOGIN_URL = "https://zjuam.zju.edu.cn/cas/login?service=http%3A%2F%2Fservice.zju.edu.cn%2F"

    def login(self):
        """Login to ZJU platform"""
        res = self.sess.get(self.LOGIN_URL)
        execution = re.search(
            'name="execution" value="(.*?)"', res.text).group(1)
        res = self.sess.get(
            url='https://zjuam.zju.edu.cn/cas/v2/getPubKey').json()
        n, e = res['modulus'], res['exponent']
        encrypt_password = self._rsa_encrypt(self.password, e, n)

        data = {
            'username': self.username,
            'password': encrypt_password,
            'execution': execution,
            '_eventId': 'submit',
            "authcode": ""
        }
        res = self.sess.post(url=self.LOGIN_URL, data=data)
        # check if login successfully
        if '用户名或密码错误' in res.content.decode():
            raise LoginError('登录失败，请核实账号密码重新登录')
        if '异常' in res.content.decode():
            raise LoginError('登录异常，请检查原因')
        # print(res.content.decode())
        print("统一认证平台登录成功~")
        # exit()
        return self.sess

    def _rsa_encrypt(self, password_str, e_str, M_str):
        password_bytes = bytes(password_str, 'ascii')
        password_int = int.from_bytes(password_bytes, 'big')
        e_int = int(e_str, 16)
        M_int = int(M_str, 16)
        result_int = pow(password_int, e_int, M_int)
        return hex(result_int)[2:].rjust(128, '0')


class HealthCheckInHelper(ZJULogin):
    headers = {
        'user-agent': 'Mozilla/5.0 (Linux; U; Android 11; zh-CN; M2012K11AC Build/RKQ1.200826.002) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/69.0.3497.100 UWS/3.22.0.36 Mobile Safari/537.36 AliApp(DingTalk/6.0.7.1) com.alibaba.android.rimet.zju/14785964 Channel/1543545060864 language/zh-CN 2ndType/exclusive UT4Aplus/0.2.25 colorScheme/light',
    }

    REDIRECT_URL = "https://zjuam.zju.edu.cn/cas/login?service=https%3A%2F%2Fhealthreport.zju.edu.cn%2Fa_zju%2Fapi%2Fsso%2Findex%3Fredirect%3Dhttps%253A%252F%252Fhealthreport.zju.edu.cn%252Fncov%252Fwap%252Fdefault%252Findex%26from%3Dwap"

    def get_ip_location(self):
        headers = {
            'authority': 'webapi.amap.com',
            'pragma': 'no-cache',
            'cache-control': 'no-cache',
            'sec-ch-ua': '"Chromium";v="92", " Not A;Brand";v="99", "Google Chrome";v="92"',
            'sec-ch-ua-mobile': '?0',
            'user-agent': 'Mozilla/5.0 (Linux; U; Android 11; zh-CN; M2012K11AC Build/RKQ1.200826.002) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/69.0.3497.100 UWS/3.22.0.36 Mobile Safari/537.36 AliApp(DingTalk/6.0.7.1) com.alibaba.android.rimet.zju/14785964 Channel/1543545060864 language/zh-CN 2ndType/exclusive UT4Aplus/0.2.25 colorScheme/light',
            'accept': '*/*',
            'sec-fetch-site': 'cross-site',
            'sec-fetch-mode': 'no-cors',
            'sec-fetch-dest': 'script',
            'referer': 'https://healthreport.zju.edu.cn/',
            'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'cookie': 'isg=BIaGbUMSG7BxFM4x941hm4D913wI58qhRFwZi3CvdKmEcyaN2nUJsfYKT6-_W8K5',
        }

        params = (
            ('key', '729923f88542d91590470f613adb27b5'),
            ('callback', 'jsonp_859544_'),
            ('platform', 'JS'),
            ('logversion', '2.0'),
            ('appname', 'https://healthreport.zju.edu.cn/ncov/wap/default/index'),
            ('csid', '17F714D6-756D-49E4-96F2-B31F04B14A5A'),
            ('sdkversion', '1.4.16'),
        )
        response = self.sess.get(
            'https://webapi.amap.com/maps/ipLocation?key=729923f88542d91590470f613adb27b5&callback=jsonp_859544_&platform=JS&logversion=2.0&appname=https%3A%2F%2Fhealthreport.zju.edu.cn%2Fncov%2Fwap%2Fdefault%2Findex&csid=17F714D6-756D-49E4-96F2-B31F04B14A5A&sdkversion=1.4.16',
            headers=headers, params=params)
        return take_out_json(response.text)

    def get_geo_info(self, location: dict):
        params = (
            ('key', '729923f88542d91590470f613adb27b5'),
            ('s', 'rsv3'),
            ('language', 'zh_cn'),
            ('location', '{lng},{lat}'.format(lng=location.get("lng"), lat=location.get("lat"))),
            ('extensions', 'base'),
            ('callback', 'jsonp_607701_'),
            ('platform', 'JS'),
            ('logversion', '2.0'),
            ('appname', 'https://healthreport.zju.edu.cn/ncov/wap/default/index'),
            ('csid', '63157A4E-D820-44E1-B032-A77418183A4C'),
            ('sdkversion', '1.4.16'),
        )

        response = self.sess.get('https://restapi.amap.com/v3/geocode/regeo', headers=self.headers, params=params, )
        return take_out_json(response.text)

    def take_in(self, geo_info: dict):
        formatted_address = geo_info.get("regeocode").get("formatted_address")
        address_component = geo_info.get("regeocode").get("addressComponent")
        if not formatted_address or not address_component: return

        # 获得id和uid参数
        res = self.sess.get(self.BASE_URL, headers=self.headers)
        if len(res.content) == 0:
            print('网页获取失败，请检查网络并重试')
            self.Push('网页获取失败，请检查网络并重试')
        html = res.content.decode()

        new_info_tmp = json.loads(re.findall(r'def = ({[^\n]+})', html)[0])
        new_id = new_info_tmp['id']
        new_uid = new_info_tmp['uid']
        # 拼凑geo信息
        lng, lat = address_component.get("streetNumber").get("location").split(",")
        geo_api_info_dict = {"type": "complete", "info": "SUCCESS", "status": 1, 
                             "position": {"Q": lat, "R": lng, "lng": lng, "lat": lat},
                             "message": "Get geolocation success.Convert Success.Get address success.", "location_type": "ip",
                             "accuracy": "null", "isConverted": "true", "addressComponent": address_component,
                             "formattedAddress": formatted_address, "roads": [], "crosses": [], "pois": []}

        data = {
            'sfymqjczrj': '0',
            'zjdfgj': '',
            'sfyrjjh': '0',
            'cfgj': '',
            'tjgj': '',
            'nrjrq': '0',
            'rjka': '',
            'jnmddsheng': '',
            'jnmddshi': '',
            'jnmddqu': '',
            'jnmddxiangxi': '',
            'rjjtfs': '',
            'rjjtfs1': '',
            'rjjtgjbc': '',
            'jnjtfs': '',
            'jnjtfs1': '',
            'jnjtgjbc': '',
            # 是否确认信息属实
            'sfqrxxss': '1',
            'sfqtyyqjwdg': '0',
            'sffrqjwdg': '0',
            'sfhsjc': '',
            'zgfx14rfh': '0',
            'zgfx14rfhdd': '',
            'sfyxjzxgym': '1',
            # 是否不宜接种人群
            'sfbyjzrq': '5',
            'jzxgymqk': '6', # 这里是第三针相关参数，1是已接种第一针，4是已接种第二针（已满6个月），5是已接种第二针（未满6个月），6是已接种第三针，3是未接种，记得自己改
            'tw': '0',
            'sfcxtz': '0',
            'sfjcbh': '0',
            'sfcxzysx': '0',
            'jcjg': '',
            'qksm': '',
            'sfyyjc': '0',
            'jcjgqr': '0',
            'remark': '',
            # 浙江省杭州市西湖区三墩镇西湖国家广告产业园西湖广告大厦
            # '\u6D59\u6C5F\u7701\u676D\u5DDE\u5E02\u897F\u6E56\u533A\u4E09\u58A9\u9547\u897F\u6E56\u56FD\u5BB6\u5E7F\u544A\u4EA7\u4E1A\u56ED\u897F\u6E56\u5E7F\u544A\u5927\u53A6',
            'address': formatted_address,
            # {"type":"complete","info":"SUCCESS","status":1,"cEa":"jsonp_859544_","position":{"Q":30.30678,"R":120.06375000000003,"lng":120.06375,"lat":30.30678},"message":"Get ipLocation success.Get address success.","location_type":"ip","accuracy":null,"isConverted":true,"addressComponent":{"citycode":"0571","adcode":"330106","businessAreas":[],"neighborhoodType":"","neighborhood":"","building":"","buildingType":"","street":"西园三路","streetNumber":"1号","country":"中国","province":"浙江省","city":"杭州市","district":"西湖区","township":"三墩镇"},"formattedAddress":"浙江省杭州市西湖区三墩镇西湖国家广告产业园西湖广告大厦","roads":[],"crosses":[],"pois":[]}
            # '{"type":"complete","info":"SUCCESS","status":1,"cEa":"jsonp_859544_","position":{"Q":30.30678,"R":120.06375000000003,"lng":120.06375,"lat":30.30678},"message":"Get ipLocation success.Get address success.","location_type":"ip","accuracy":null,"isConverted":true,"addressComponent":{"citycode":"0571","adcode":"330106","businessAreas":[],"neighborhoodType":"","neighborhood":"","building":"","buildingType":"","street":"\u897F\u56ED\u4E09\u8DEF","streetNumber":"1\u53F7","country":"\u4E2D\u56FD","province":"\u6D59\u6C5F\u7701","city":"\u676D\u5DDE\u5E02","district":"\u897F\u6E56\u533A","township":"\u4E09\u58A9\u9547"},"formattedAddress":"\u6D59\u6C5F\u7701\u676D\u5DDE\u5E02\u897F\u6E56\u533A\u4E09\u58A9\u9547\u897F\u6E56\u56FD\u5BB6\u5E7F\u544A\u4EA7\u4E1A\u56ED\u897F\u6E56\u5E7F\u544A\u5927\u53A6","roads":[],"crosses":[],"pois":[]}',
            # {"type":"complete","position":{"Q":30.30975640191,"R":120.085647515191,"lng":120.085648,"lat":30.309756},"location_type":"html5","message":"Get geolocation success.Convert Success.Get address success.","accuracy":40,"isConverted":true,"status":1,"addressComponent":{"citycode":"0571","adcode":"330106","businessAreas":[],"neighborhoodType":"","neighborhood":"","building":"","buildingType":"","street":"龙宇街","streetNumber":"17-18号","country":"中国","province":"浙江省","city":"杭州市","district":"西湖区","towncode":"330106109000","township":"三墩镇"},"formattedAddress":"浙江省杭州市西湖区三墩镇翠柏浙江大学(紫金港校区)","roads":[],"crosses":[],"pois":[],"info":"SUCCESS"}
            'geo_api_info': geo_api_info_dict,
            # 浙江省 杭州市 西湖区
            # '\u6D59\u6C5F\u7701 \u676D\u5DDE\u5E02 \u897F\u6E56\u533A'
            'area': "{} {} {}".format(address_component.get("province"), address_component.get("city"),
                                      address_component.get("district")),
            # 浙江省
            # '\u6D59\u6C5F\u7701'
            'province': address_component.get("province"),
            # 杭州市
            # '\u676D\u5DDE\u5E02'
            'city': address_component.get("city"),
            # 是否在校：在校将'sfzx'改为1
            'sfzx': '1', 
            'sfjcwhry': '0',
            'sfjchbry': '0',
            'sfcyglq': '0',
            'gllx': '',
            'glksrq': '',
            'jcbhlx': '',
            'jcbhrq': '',
            'bztcyy': '4', # 这里也变了
            'sftjhb': '0',
            'sftjwh': '0',
            'fjsj':	'0',
            # 👇-----12.1日修改-----👇
            'sfjcqz': '', #修改
            'jcqzrq': '',
            # 👆-----12.1日修改-----👆
            'jrsfqzys': '',
            'jrsfqzfy': '',
            'sfyqjzgc': '',
            # 是否申领杭州健康码
            'sfsqhzjkk': '1',
            # 杭州健康吗颜色，1:绿色 2:红色 3:黄色
            'sqhzjkkys': '1',
            'gwszgzcs': '',
            'szgj': '',
            'fxyy': '',
            'jcjg': '',
            # uid每个用户不一致
            'uid': new_uid,     
            # id每个用户不一致
            'id': new_id,
            # 下列原来参数都是12.1新版没有的
            # 日期
            'date': get_date(),
            'created': round(time.time()),
            'szsqsfybl': '0',
            'sfygtjzzfj': '0',
            'gtjzzfjsj': '',
            'gwszdd': '',
            'szgjcs': '',
            'ismoved': '0', # 位置变化为1，不变为0
            'zgfx14rfhsj':'',
             # 👇-----2022.3.30日修改-----👇
            'jrdqjcqk': '',
            'jcwhryfs': '',	
            'jchbryfs': '',	
            'xjzd': '',	
            'sfsfbh':'0',
            'jhfjrq':'',	
            'jhfjjtgj':'',	
            'jhfjhbcc':'',	
            'jhfjsftjwh':'0',
            'jhfjsftjhb':'0',
            'szsqsfybl':'0',
            'gwszgz':'',
            # 👆-----2022.3.30日修改-----👆
        }
        response = self.sess.post('https://healthreport.zju.edu.cn/ncov/wap/default/save', data=data,
                                  headers=self.headers)
        return response.json()

    def Push(self,res):
        if self.CHAT_ID and self.TG_TOKEN and len(self.CHAT_ID) and len(self.TG_TOKEN):
            
            push_tg(self.TG_TOKEN, self.CHAT_ID, '浙江大学每日健康打卡 V2.0 '+ " \n\n 签到结果: " + res) 
            print("推送完成！")
        else:
            print("telegram推送未配置，请自行查看签到结果")
        
        
    def run(self):
        print("正在为{}健康打卡".format(self.username))
        if self.delay_run:
            # 确保定时脚本执行时间不太一致
            time.sleep(random.randint(1, 10))
        try:
            self.login()
            # 拿取eai-sess的cookies信息
            self.sess.get(self.REDIRECT_URL)
            # 由于IP定位放到服务器上运行后会是服务器的IP定位
            # location = self.get_ip_location()
            # print(location)
            # location = {'info': 'LOCATE_SUCCESS', 'status': 1, 'lng': self.lng, 'lat': self.lat}
            # 浙江省杭州市西湖区三墩镇浙江大学紫金港校区信访接待室浙江大学(紫金港校区)
            location = {'info': 'LOCATE_SUCCESS', 'status': 1, 'lng': 120.090834, 'lat': 30.303819}
            print(location)
            
            geo_info = self.get_geo_info(location)
            print(geo_info)
            
            res = self.take_in(geo_info)

            print(res)
            
            self.Push(res.get("m"))

        except requests.exceptions.ConnectionError :
            # reraise as KubeException, but log stacktrace.
            print("打卡失败,请检查github服务器网络状态")
            self.Push('打卡失败,请检查github服务器网络状态')


def getEnvs(label):
    try:
        if label == 'True' or label == 'yes' or label == 'true' or label == 'Yes':
            return True
        elif label == 'False' or label == 'no' or label == 'false' or label == 'No':
            return False
    except:
        pass
    try:
        if '.' in label:
            return float(label)
        elif '&' in label:
            return label.split('&')
        elif '@' in label:
            return label.split('@')
        else:
            return int(label)
    except:
        return label


if 'ZJU_ACCOUNT' in os.environ and 'ZJU_PASSWORD' in os.environ:
    account = str(getEnvs(os.environ['ZJU_ACCOUNT']))
    pwd = getEnvs(os.environ['ZJU_PASSWORD'])
    s = HealthCheckInHelper(account, pwd, delay_run=True)
    s.run()
else:
    print("环境变量未配置！")