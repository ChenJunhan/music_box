import urllib.parse                   # 参数处理
import http.client                    # 建立http连接
import json                           # json处理
from urllib import request            # 发送请求
import execjs                         # 运行js代码
from prettytable import PrettyTable   # 打印表格形式
import io                             # 改变默认编码
import sys                            # 改变默认编码
import os                             # 处理路径

class download(object):
  def __init__(self):

    # 读取js加密函数文件
    jsFile = open('core.js', 'r')
    content = jsFile.read()
    self.ctx = execjs.compile(content)
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer,encoding='gb18030')  # 改变标准输出的默认编码 避免报'gbk' codec can't encode character '\uc5ec' in position 1092 错误

  # 搜索音乐列表
  def searchList(self):
    key = input('请输入下载的音乐名：')           # 搜索音乐关键词

    encSec = self.ctx.call(
      'd',
      json.dumps({"hlpretag":"<span class='s-fc7'>","hlposttag":"</span>","s": key,"type":"1","offset":"0","total":"true","limit":"30","csrf_token":""}),
      '010001', 
      '00e0b509f6259df8642dbc35662901477df22677ec152b5ff68ace615bb7b725152b3ab17a876aea8a5aa76d2e417629ec4ee341f56135fccf695280104e0312ecbda92557c93870114af6c9d05c4f7f0c3685b7a46bee255932575cce10b424d813cfe4875d3e82047b97ddef52741d546b8e289dc6935b3ece0462db0a22b8e7', 
      '0CoJUm6Qyw8W8jud'
    )

    url = 'https://music.163.com/weapi/cloudsearch/get/web?csrf_token='
    musicList = self.request('POST', url, encSec)['result'].get('songs')                # 歌曲列表
    musicList = list(filter(lambda m: m['privilege']['st'] == 0, musicList))            # 过滤掉没有下载链接的音乐

    if (musicList == None or len(musicList) == 0): 
      print('很抱歉，未能找到相关搜索结果！')
      return
    
    # 制作表格
    x = PrettyTable(["编号","歌名", "歌手"])
    
    for i, m in enumerate(musicList):
      name = m['name']     
      singer = m['ar'][0]['name']
      x.add_row([i, name, singer])
    
    print(x)                            # 显示列表

    while 1:
      
      try:
        id = int(input('请输入下载的音乐编号：'))
      except ValueError:
        id = 30                  # 若输入格式非数字格式的按输入30即编号不存在

      if (id < len(musicList)):  # 输入的编号存在于列表内则下载，否则提示重新输入编号
        self.downloadMusic(musicList[id])
        break
      else:
        print('输入的编号不存在！请重新输入')
 

  # 下载音乐
  def downloadMusic(self, music):
    
    ids =  "[" + str(music['id']) + "]"
    name = music['name'] + '.mp3'

    encSec = self.ctx.call(
      'd', 
      json.dumps({"ids": ids, "br": 128000, "csrf_token": ""}),
      '010001', 
      '00e0b509f6259df8642dbc35662901477df22677ec152b5ff68ace615bb7b725152b3ab17a876aea8a5aa76d2e417629ec4ee341f56135fccf695280104e0312ecbda92557c93870114af6c9d05c4f7f0c3685b7a46bee255932575cce10b424d813cfe4875d3e82047b97ddef52741d546b8e289dc6935b3ece0462db0a22b8e7', 
      '0CoJUm6Qyw8W8jud'
    )          # 调用js代码中的d函数

    url = 'https://music.163.com/weapi/song/enhance/player/url?csrf_token='
    data = self.request('POST', url, encSec)       # 发送获取音乐链接请求

    if (data['data'][0]['url'] == None): 
      print('该歌曲暂无下载链接！')
      return
    f = request.urlopen(data['data'][0]['url'])    # 打开音乐下载链接
    d = f.read()                                   # 读取文件内容并保存在桌面
    saveDir = os.getcwd().replace('\\', "/") + '/music/'   # 获取当前绝对路径

    if os.path.isdir(saveDir):    # 若无music文件夹则创建
      pass
    else:
      os.mkdir(saveDir)

    with open(saveDir + name, 'wb') as code:    
        code.write(d)
    print('成功下载到', saveDir, '目录中！')

  # 发送请求
  def request(self, type, url, encSec):
    data = {
      'params': encSec['encText'],
      'encSecKey': encSec['encSecKey']
    } 
    test_data_url_encode = urllib.parse.urlencode(data)         # 将请求数据进行url编码

    conn = http.client.HTTPConnection('music.163.com')
    header = {"Content-type": "application/x-www-form-urlencoded", "Accept": "text/plain"}

    conn.request(method = type, url = url, body = test_data_url_encode, headers = header)
    response = conn.getresponse()
    res = response.read()

    str1 = json.loads(res.decode('utf-8'))     # 将 bytes格式 转成 string格式 再转 字典

    if (str1['code'] == 200):
      return str1   
    else:
      print('请求发生错误！')


if __name__ == '__main__':
  load = download()
  load.searchList()
