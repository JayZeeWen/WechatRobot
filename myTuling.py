import re
import requests
import json
from wxpy.api.messages import Message
from wxpy.api.chats import Group
from read_config import *
from logHelper import * 
url = 'http://openapi.tuling123.com/openapi/api/v2'
api_key=getProp('robot','tuling_key')#图灵机器人apikey
recv_name=getProp('robot','receive_name') #自动回复 的微信好友 
list_recv = recv_name.split(',')
print(list_recv)


def call_tuling(user_id ,text):
    '''userInfo = UserInfo(api_key,user_id)
    perception = Perception(text)
    js = json.dumps(perception,default=Perception.perception2dict)'''

    userInfo = {}
    userInfo['apiKey'] = api_key
    userInfo['userId'] = user_id

    inputText = {}
    inputText['text'] = text 

    p = {}
    p["inputText"] = inputText
    #目前只支持文字
    payload = dict(
        reqType=0,
        perception=p,
        userInfo=userInfo
    )
    try:
        #调用图灵官方接口拿到result
        r = requests.post(url, json=payload)
        answer = r.json()
        results = answer['results']
        reply_str = ''
        #拼接result 
        for r in results:
            type = r['resultType']
            rep = r['values']
            reply_str = reply_str + rep[type]
        return reply_str
    except Exception as e :
        print('Error:', e)
        return None
    

#call_tuling('20190614001','可以聊天吗')

