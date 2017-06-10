# -*- coding: utf-8 -*-

import requests
import getpass
import os
import hashlib
from time import clock as now
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

base_url = 'http://114.115.139.232:8080/xxzx/a/'
headers = {'user-agent': 'Mozilla/5.0 (Linux; Android 5.1.1; Nexus 6 Build/LYZ28E)'
                         ' AppleWebKit/537.36 (KHTML, like Gecko) '
                         'Chrome/58.0.3029.110 Mobile Safari/537.'}
cookies = 'cookies'
floder_url = ''
all_md5 = []

def main():
    username = input('请输入登录名：')
    password = input('请输入密码：')
    # 使用getpass模块,输入密码时，不可见
    # password = getpass.win_getpass('请输入密码：')
    # if(os = unix):
    #     password = getpass.unix_getpass('请输入密码：')
    login(username, password, headers)
    set_upload_floder()
    traversal_floder_files()
    judge_file_upload_state()
    while 1:
      loopwatch()


#登录，获取用户信息和cookie
def login(username,password,headers):
    global cookies
    login_url = base_url + 'login?__ajax=true'
    account = {'username' : username , 'password' : password, 'mobileLogin' :'true'}
    login_info = requests.post(login_url, data=account, headers = headers)
    print(login_info.json())
    login_info_json = login_info.json()
    print(login_info_json['name'] + '登录成功')
    cookies = login_info_json['sessionid']


#设置自动上传的文件夹
def set_upload_floder():
    global floder_url
    print('------------------------------配置自动上传图片文件夹----------------------------------------')
    print('---------------------------如果不输入，默认地址:/var/pic------------------------------------')
    floder_url = input('输入图片文件夹地址:')
    if floder_url == '':
        floder_url = 'C:/Users/Yuan/Pictures/lovewallpaper'


#遍历文件夹所有文件名
def traversal_floder_files():
    list_dirs = os.listdir(floder_url)
    for filename in list_dirs:
        files_url = floder_url+ '/' + filename
        #将所遍历的图片上传到服务器
        # upload(files_url, filename)


#通过md5值,判断图片是否已经上传过
def getmd5(filename):
    file_txt = open(filename,'rb').read()
    m = hashlib.md5()
    m.update(file_txt)
    return m.hexdigest()


def judge_file_upload_state():
    global all_md5
    total_file = 0
    total_delete = 0
    total_upload = 0
    start = now()
    for file in os.listdir(floder_url):
        total_file += 1
        real_path = os.path.join(floder_url,file)
        files_url = floder_url + '/' + file
        if os.path.isfile(real_path) == True:
            filemd5 = getmd5(files_url)
            #判断当前图片md5码是否存在服务器已有图片的md5码中，如果存在就不上传，不存在就上传。
            #可以连接数据库中的图片md5码进行匹配判断
            if filemd5 in all_md5:
                total_delete += 1
                print('已存在图片:',file)
                #跳转到监控文件夹
            else:
                all_md5.append(filemd5)
                total_upload += 1
                # 将所遍历的图片上传到服务器
                upload(files_url, file)
    end = now()
    time_last = end - start
    print('图片总数:',total_file)
    print('重复图片个数:',total_delete)
    print('更新图片个数:',total_upload)
    print('耗时',time_last,'秒')





#post上传文件到服务器
def upload(files_url, filename):
     upload_url = base_url + 'tpsb/uploadPicture;JSESSIONID=' + cookies
     files = {'file': open(files_url, 'rb')}
     upload_request = requests.post(upload_url, files=files)
     print('正在上传：'+ files_url)


#循环监测文件夹内容变化，如果有新图片则自动添加
#使用watchdog库进行监控文件夹变动，如果有变动，上传新内容
class MyHandler(FileSystemEventHandler):
    def on_created(self, event):
        print("目录中有新文件")
        print('开始将新文件上传到服务器')
        judge_file_upload_state()


    def on_deleted(self, event):
        print("有文件被删除")

    def on_modified(self, event):
        print('文件被修改')

    def on_moved(self, event):
        print('文件被重命名或者被删除')


def loopwatch():
    event_handler = MyHandler()
    observer = Observer()
    observer.schedule(event_handler, floder_url, recursive=True)
    observer.start()
    observer.join()




if __name__ == '__main__':
    main()