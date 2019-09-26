# -*- coding:utf-8 -*-

import oss2
import os
from read_config import getProp

endpoint = getProp('aliyunOSS','endpoint')
bucket = getProp('aliyunOSS','bucket')
accessKeyId = getProp('aliyunOSS','accessKeyId')
accessKeySecret = getProp('aliyunOSS','accessKeySecret')
downloadPath = getProp('aliyunOSS','downloadPath')

auth = oss2.Auth(accessKeyId, accessKeySecret)
bucket = oss2.Bucket(auth, endpoint, bucket)

temp_dir = os.path.join(os.getcwd(), downloadPath)
def uploadFile(fileName):
    path = os.path.join(temp_dir, f'{str(fileName)}')
    bucket.put_object_from_file(fileName, path)
    return


def downloadFile(fileName):
    path_down = os.path.join(temp_dir, fileName)
    bucket.get_object_to_file(fileName, path_down)
