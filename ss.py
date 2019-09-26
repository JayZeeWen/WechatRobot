#导入模块
from wxpy import *
import os
import uuid
from ossHelper import uploadFile,downloadFile,temp_dir
'''import logging

LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"    # 日志格式化输出
DATE_FORMAT = "%m/%d/%Y %H:%M:%S %p" 
fp = logging.FileHandler('robot_log.txt',encoding='utf-8')
fs = logging.StreamHandler()


logging.basicConfig(level=logging.INFO,format=LOG_FORMAT, datefmt=DATE_FORMAT, handlers=[fp, fs])
logging.debug('this is logfile') 

#初始化机器人
try:
	bot = Bot(cache_path =True)
except Exception as e:
	print(e)
	pass

my_friend = bot.friends().search('风具浪小子', sex=MALE, city='深圳')[0]
my_friend.send_file('E:/克拉西克/hi-robot-git/pre/logs/test.txt')'''
'''
@bot.register(Group, TEXT)
def receive_msg(msg):
	# 如果是群聊，但没有被 @，则不回复
	#if isinstance(msg.chat, Group) and not msg.is_at:
	print('show me {}'.format(msg))
	logging.info('logging show me {}'.format(msg))
embed()'''


'''url = "https://wx.qq.com/"
r = requests.post(url,timeout=10)
print(r.text)'''

suffix = '.jpg'
fileName  =  str(uuid.uuid1()).replace('-','')
fileName = fileName + suffix
print(fileName)





