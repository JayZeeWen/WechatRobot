
import logging
import time

LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"    # 日志格式化输出
DATE_FORMAT = "%m/%d/%Y %H:%M:%S %p" 

def init():
    
    str_time = time.strftime("%Y%m%d%H%M%S", time.localtime()) 
    fp = logging.FileHandler('../logs/log_'+str_time +'.txt',encoding='utf-8')
    fs = logging.StreamHandler()

    logging.basicConfig(level=logging.INFO,format=LOG_FORMAT, datefmt=DATE_FORMAT, handlers=[fp, fs])
    

def logInfo(msg):
    init()
    logging.info(msg)

def logError(msg):
    init()
    logging.error(msg)