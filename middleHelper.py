#!/usr/bin/env python 
# -*- coding:utf-8 -*-
#中台接口帮助类
import json
import requests
from read_config import *
from logHelper import *


middle_host=getProp('robot','middel_host')#中台服务器地址

#调用接口 检查  内容是否有匹配的策略
def callMiddleToCheck(msg):
    url = middle_host + "/msg/checkHasMatchStra"
    para = {'message': msg}
    r = requests.post(url, para)
    logging.info("call middle api : 【checkHasMatchStra】  ,call result is :" + r.text)
    r.encoding = 'utf-8'
    content = json.loads(r.text)

    return content

#调用接口 获取回复内容
def callMiddleToGetReptMsg(chatMsg):
    url = middle_host + "/msg/getRepMsg"
    para = {'message': chatMsg}
    r = requests.post(url, para)
    logging.info("call middle api 【getRepMsg】 ,call result is :" + r.text)
    r.encoding = 'utf-8'
    content = json.loads(r.text)
    return content

#调用接口  更行登陆状态
def updateLoginState(state):
    url = middle_host + "/msg/updateLoginState"
    para = {'loginState': state}
    r = requests.post(url, para)
    logging.info("call middle api 【getRepMsg】 ,call result is :" + r.text)
    r.encoding = 'utf-8'
    content = json.loads(r.text)
    return content