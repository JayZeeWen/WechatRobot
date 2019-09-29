#coding:utf-8
#导入模块  2
import os
from wxpy import *
import logging
import uuid
import time
import json
import _thread
import pika
import requests

from mqSender import *
from read_config import *
from myTuling import call_tuling
from ossHelper import uploadFile,downloadFile,temp_dir
from middleHelper import *

LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"    # 日志格式化输出
DATE_FORMAT = "%m/%d/%Y %H:%M:%S %p" 
str_time = time.strftime("%Y%m%d", time.localtime()) 
fp = logging.FileHandler('../logs/log_'+str_time +'.txt',encoding='utf-8')
fs = logging.StreamHandler()

logging.basicConfig(level=logging.INFO,format=LOG_FORMAT, datefmt=DATE_FORMAT, handlers=[fp, fs])
logging.debug('this is logfile')

#import read_config
host = getProp('rabbitmq','host')
queue_s = getProp('rabbitmq','queue_s')
queue_r = getProp('rabbitmq','queue_r')
name = getProp('rabbitmq','name')
pwd = getProp('rabbitmq','password')
port = getProp('rabbitmq','port')

#robot_name = read_config.robot_name
#robot_id = read_config.robot_id
kouling = getProp('robot','kouling')
kouling_reply = getProp('robot','kouling_reply')
is_test=getProp('robot','is_test') #是否是测试
recv_name=getProp('robot','receive_name') #自动回复 的微信好友 
list_recv = recv_name.split(',')
qr_save_path=getProp('robot','qrCodeSavePath') #二维码存储路径
key_tuling=getProp('robot','tuling_key')#图灵机器人apikey
middle_host=getProp('robot','middel_host')#中台服务器地址

logging.info('name:%s'% name)
logging.info('port:%s'% port)
logging.info('host:%s'% host)
logging.info('queue_s:%s' % (queue_s))
logging.info('queue_r:%s' % (queue_r))
logging.info('robot_id:%s' % robot_id)
logging.info('robot_name:%s' % robot_name)

tuling = Tuling(api_key= key_tuling)

#credentials = pika.PlainCredentials(name, pwd)

class RobotContext:

	bot = None
	switcher = {}

	def __init__(self):
		credentials = pika.PlainCredentials(name, pwd)
		self.credentials = pika.PlainCredentials(name, pwd)
		self.connection = pika.BlockingConnection(pika.ConnectionParameters(host=host,credentials=credentials,heartbeat=0))
		self.channel = self.connection.channel()
		

	def send_mq(self,msg):
		self.channel.queue_declare(queue=queue_s)
		#发送信息：exchange指定交换，routing_key指定队列名，body指定消息内容
		#channel.basic_publish(exchange='',routing_key='zhang',body='hhhhhhh')
		self.channel.basic_publish(exchange='',routing_key=queue_s,body=msg)
		#关闭链接
		#connection.close()

	def receive_mq(self,callback):
		#创建队列名，此处也可省略，在找不到队列时创建
		self.channel.queue_declare(queue=queue_r)   
		#指定队列接收消息,callback接收消息，queue指定队列，no_ack不给发送者发送确认消息
		#channel.basic_consume(callback,queue='zhang',no_ack=True)
		self.channel.basic_consume(queue=queue_r,on_message_callback=callback)
		logging.info('starting consuming,waiting for message,to exit press ctrl+c')
		#持续接收消息,阻塞
		self.channel.start_consuming()
	
	def callback(ch,method,properties,body):
		#print('object method recived:')
		#print('object method recived:' + str(body, encoding = "utf-8") )
		logging.info('receive msg from midder platform')
		dataMsg = json.loads(str(body, encoding = "utf-8"))
		logging.info('receive msg from midder platform:{}'.format(dataMsg))
		if dataMsg['repResult'] == '2': #若未找到匹配的资源，则调用图灵接口回复
			sourceMsg = dataMsg['sourceMsg'] 
			puid = dataMsg['puid'] 
			dataMsg['msg'] = call_tuling(puid,sourceMsg)
		if dataMsg != None:
			#execfunc = RobotContext.switcher.get(dataMsg['action'])
			#execfunc = RobotContext.switcher.get(dataMsg['action'])
			try:
				ch.basic_ack(delivery_tag = method.delivery_tag)
				execfunc = RobotContext.switcher.get(dataMsg['action'])
				execfunc(dataMsg)				
			except Exception as e:
				logging.error('callback Exception：{}'.format(repr(e)))
		else:
			ch.basic_ack(delivery_tag = method.delivery_tag)

	def qr_callback(uuid, status, qrcode):	
		logging.info("in qrCallBack ------------- uuid " + uuid )
		#print("in qrCallBack ------------- status " + status )
		with open(qr_save_path, 'wb') as f:
			f.write(qrcode)
		

	def initBot(self,qr_callback):
		
		logging.info('-------------开始登陆微信----------' )
		#RobotContext.bot = Bot( qr_path =  "qrcode_test.jpg")
		RobotContext.bot = Bot( cache_path =True, console_qr = True ,qr_callback = qr_callback)
		logging.info('-------------微信登陆成功----------' )
		# 启用 puid 属性，并指定 puid 所需的映射数据保存/载入路径
		RobotContext.bot.enable_puid('wxpy_puid.pkl')
		return RobotContext.bot

	def callbackHandleRegister(self, name, func):
		RobotContext.switcher[name] = func

rc = RobotContext()
bot = rc.initBot(qr_callback=RobotContext.qr_callback)

#打印来自其他好友、群聊和公众号消息
@bot.register(Friend, TEXT)
def print_others(msg):
	#print(msg.chat)
	#print(msg.chat.remark_name())
	#print(msg.is_at)
	logging.info("receive message From Freiend:chat_puid="+ msg.chat.puid +" chat_name="+ msg.chat.nick_name + ",content=" + str(msg.raw['Content']))
	chatMsg = wapperMsg('Friend',None,None,msg)
	#rc.send_mq(chatMsg)
	if is_test == "Y" :
		for recvName in list_recv:
			found = bot.friends().search(recvName)
			youfou = ensure_one(found)
			if youfou and msg.sender.nick_name == found[0].nick_name :
				replyFriendMsg(chatMsg,msg)
				break
				#rc.send_mq(chatMsg)
	else :
		replyFriendMsg(chatMsg,msg)
		#rc.send_mq(chatMsg)


@bot.register(Friend,NOTE)
def recvFriendNote(msg):
	#TODO 取消关注后的操作
	#取消关注后发送消息会接受到 note 如下
	#xxxxx开启了朋友验证，你还不是他（她）朋友。请先发送朋友验证请求，对方验证通过后，才能聊天。<a href="weixin://findfriend/verifycontact">发送朋友验证</a>
	logging.info("receive Note From Freiend:chat_puid=" + msg.chat.puid + " chat_name=" + msg.chat.nick_name + ",content=" + str(	msg.raw['Content']))
	#logging.info(msg)

def replyFriendMsg(chatMsg,botMsg):
	sendMqMsg(chatMsg)
	'''
	msgJson = json.loads(chatMsg)
	msg = msgJson['msg']
	isMatch =  callMiddleToCheck(msg)
	#若没有找到匹配的策略，则直接调用图灵机器人回复
	if isMatch :
		sendMqMsg(chatMsg)
	else :
		tuling.do_reply(botMsg) '''



@bot.register(Group, TEXT)
def receive_msg(msg):
	# 如果是群聊，但没有被 @，则不回复
	#if isinstance(msg.chat, Group) and not msg.is_at: 
	logging.info('receive message from Group[' + msg.chat.nick_name + '] - sender['+ msg.member.name +'] -' + msg.raw['Content'])
	if isinstance(msg.chat, Group) and msg.is_at:
		chatMsg = wapperMsg('Group',msg.is_at,None, msg)
		#rc.send_mq(chatMsg)
		content =  callMiddleToGetReptMsg(chatMsg)
		reptMsg = ''
		if len(content) > 0 and content['msg'] is not None:
			reptMsg = content['msg']
		if content['repResult'] == '2':
			tuling.do_reply(msg,at_member = False)
		else :
			msg.chat.send(reptMsg)
		#sendMqMsg(chatMsg)
	elif (isinstance(msg.chat, Friend)):
		chatMsg = wapperMsg('Friend',None,None, msg)
		#rc.send_mq(chatMsg)
		sendMqMsg(chatMsg)


def wapperMsg(chatType,isAt,action,msg):

	chatMsg = {}
	#消息来源类别
	chatMsg['chatType'] = chatType
	#群聊是否被@
	chatMsg['isAt'] = isAt
	#消息
	chatMsg['msg'] = msg.raw['Content']
	
	#群会话  sender为群组  一对一会话 sender为对方用户
	chatMsg['chatName'] = msg.chat.nick_name
	

	if action != "accept" and chatType != 'Group' :

		chatMsg['remarkName'] = msg.chat.remark_name
		#头像

		#签名
		chatMsg['signature'] = msg.chat.signature
		#性别
		chatMsg['gender'] = msg.chat.sex
		#地区
		chatMsg['area'] = msg.chat.province + "-" + msg.chat.city
	#当群会话  member为实际消息发送人
	if msg.member is not None:
		chatMsg['msgMember'] = msg.member.name
		chatMsg['puid'] = msg.member.puid
		chatMsg['wechatId'] = msg.member.wxid
		found = bot.friends().search(msg.member.name)
		if len(found) > 0 :
			sureOne = ensure_one(found)
			if sureOne:
				chatMsg['remarkName'] = found[0].name
		else:
			chatMsg['remarkName'] = msg.member.name
	else :
		chatMsg['puid'] = msg.chat.puid
		chatMsg['wechatId'] = msg.chat.wxid

	if action is not None:
		chatMsg["action"] = action
	chatMsg['conversationId'] = str(uuid.uuid1())
	
	#chatMsgStr = str(chatMsg)
	chatMsgStr = json.dumps(chatMsg,ensure_ascii=False)

	logging.info('wrapper msg is :{}'.format(chatMsgStr))
	return chatMsgStr


#退出指令 执行方法
def do_quit(data=None):
	#todo 微信名称加离线备注
	#quit()
	bot.logout()
	bot.join()
	quit()


rc.callbackHandleRegister('quit', do_quit)

#回复指令
def do_reply(data=None):
	if data == None:
		logging.info('wrong reply message, there is no data dict')
	else:
		chat = find_chat(data)
		if chat is None :
			#没有找到好友，可能已经取消关注，TODO 调用接口更新用户记录表
			return
		msgType = data['msgType'] #消息类型，（文本、图片、文件）
		if msgType is None or msgType == "text":
			sent_msg = chat.send(data['msg'])
		elif msgType == "img":  #发送图片
			fileName = data['msg']
			downloadFile(fileName)
			path = os.path.join(temp_dir, f'{str(fileName)}')
			chat.send_image(path)
			os.remove(path)
		elif msgType == "file": #发送文件
			fileName = data['msg']
			downloadFile(fileName)
			path = os.path.join(temp_dir, f'{str(fileName)}')
			chat.send_file(path)
			os.remove(path)

def find_chat(data):
	func = chatSwitcher.get(data['chatType'])
	return func(data)

def find_friend(data):
	search = bot.friends().search(data['chatName'])
	if len(search) < 1 :
		logging.info('no friend was found  chatName is : ' + data['chatName'])
		return  None
	friend = search[0]
	return friend

def find_group(data):
	group = bot.groups().search(data['chatName'])[0]
	return group

chatSwitcher = {
	'Friend':find_friend,
	'Group':find_group
}

#绑定账号，更改备注名称
def do_binding(data =None):
	if data == None:
		logging.info('wrong reply message, there is no data dict')
	else:
		chat = find_chat(data)
		if data["remarkName"] is not None :
			#若为绑定用户操作，会使用中台传递的备注名做为备注
			chat.set_remark_name(data["remarkName"])
		chat.send(data['msg'])

rc.callbackHandleRegister('reply', do_reply)
rc.callbackHandleRegister('binding', do_binding)


# 注册好友请求类消息
@bot.register(msg_types=FRIENDS)
# 自动接受验证信息中包含 'wxpy' 的好友请求
def auto_accept_friends(msg):
	# 判断好友请求中的验证文本
	# 接受好友 (msg.card 为该请求的用户对象)
	new_friend = bot.accept_friend(msg.card)
	
	chatMsg = {}
	#消息来源类别
	chatMsg['chatType'] = 'Friend'
	chatMsg['chatName'] =  new_friend.name

	#頭像
	# 将头像文件下载下来并上传到阿里云，然后删除本地文件
	suffix = '.jpg'
	fileName = str(uuid.uuid1()).replace('-', '')
	fileName = fileName + suffix
	path = os.path.join(temp_dir, f'{str(fileName)}')
	img = new_friend.get_avatar(save_path = path)
	uploadFile(fileName)
	os.remove(path)

	chatMsg['wxImg'] = fileName


	#签名
	chatMsg['signature'] = new_friend.signature
	#性别
	chatMsg['gender'] = new_friend.sex
	#地区
	chatMsg['area'] = new_friend.province + "-" + new_friend.city
	chatMsg['conversationId'] = str(uuid.uuid1())
	chatMsg['msg'] = '请求好友'
	chatMsg['action'] = 'accept'
	chatMsgStr = json.dumps(chatMsg,ensure_ascii=False)
	#chatMsg = wapperMsg('Friend',None,'accept', msg)
	#rc.send_mq(chatMsgStr)
	sendMqMsg(chatMsgStr)
	# 向新的好友发送消息
	new_friend.send(kouling_reply)


_thread.start_new_thread(RobotContext.receive_mq,(rc,RobotContext.callback))
#进入python 命令行 让程序保持运行
embed()