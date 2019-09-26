import os
import configparser

#获取当前文件路径
cur_path = os.path.dirname(os.path.realpath(__file__))


#获取config.ini的路径
config_path = os.path.join(cur_path,'config.ini')


#读取配置
conf = configparser.ConfigParser()
conf.read(config_path,encoding='utf-8')

rabbitmq_host = conf.get('rabbitmq','host')
#rabbitmq_queue = conf.get('rabbitmq','queue')


robot_name = conf.get('robot','name')
robot_id = conf.get('robot','id')

def getProp(upname,subname):
	return conf.get(upname, subname)
	pass


