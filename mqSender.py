import pika
from read_config import *

host = getProp('rabbitmq','host')
queue_s = getProp('rabbitmq','queue_s')
queue_r = getProp('rabbitmq','queue_r')
name = getProp('rabbitmq','name')
pwd = getProp('rabbitmq','password')
port = getProp('rabbitmq','port')

credentials = pika.PlainCredentials(name, pwd)
connection = pika.BlockingConnection(pika.ConnectionParameters(host=host,credentials=credentials,heartbeat=0))
channel = connection.channel()
#channel.queue_declare(queue=queue_s)

'''
def __init__(self):
    credentials = pika.PlainCredentials(name, pwd)
    self.credentials = pika.PlainCredentials(name, pwd)
    self.connection = pika.BlockingConnection(pika.ConnectionParameters(host=host,credentials=credentials,heartbeat=0))
    self.channel = self.connection.channel() '''

def sendMqMsg(msg):
    print(msg)
    channel.queue_declare(queue=queue_s)
    channel.basic_publish(exchange='',routing_key=queue_s,body=msg)
    