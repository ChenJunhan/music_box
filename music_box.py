import urllib.parse                   # 参数处理
import http.client                    # 建立http连接
import json                           # json处理
from urllib import request            # 发送请求
import execjs                         # 运行js代码
from prettytable import PrettyTable   # 打印表格形式
import io                             # 改变默认编码
import sys                            # 改变默认编码
import os                             # 处理路径
from http import cookiejar            # 获取cookie

class download(object):
  def __init__(self):

    # 读取js加密函数文件
    jsFile = open('core.js', 'r')
    content = jsFile.read()
    self.ctx = execjs.compile(content)
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8')  # 改变标准输出的默认编码 避免报'gbk' codec can't encode character '\uc5ec' in position 1092 错误

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

    isContinue = input('是否继续下载音乐? Y or N:')
    if (isContinue == 'Y' or isContinue == 'y'):
      self.searchList()

  # 发送请求
  def request(self, type, url, encSec):
    data = {
      'params': encSec['encText'],
      'encSecKey': encSec['encSecKey']
    } 
    test_data_url_encode = urllib.parse.urlencode(data).encode(encoding="UTF-8")         # 将请求数据进行url编码

    header = {
      "Content-type": "application/x-www-form-urlencoded", 
      "Accept": "text/plain",
      "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36",
      "Cookie": "usertrack=c+xxClmeTCye9ji6A21+Ag==; _ntes_nnid=8588145d4f4fc6e14eb46108f65bbe8c,1503546412380; _ntes_nuid=8588145d4f4fc6e14eb46108f65bbe8c; vjuids=3009edcf9.15fdc463eda.0.ce4d81bfaee59; __gads=ID=d02df168419c382c:T=1511229109:S=ALNI_MYNhR-8kMeEaYWNjvj68WCc-Re8Kw; _ga=GA1.2.1842392025.1503546413; NTES_CMT_USER_INFO=125526182%7C%E6%9C%89%E6%80%81%E5%BA%A6%E7%BD%91%E5%8F%8B07uS2C%7C%7Cfalse%7CbTE4ODI0MzA5OTg0XzFAMTYzLmNvbQ%3D%3D; P_INFO=m18824309984_1@163.com|1522235352|0|csa|00&99|gud&1522232977&xyq#gud&440300#10#0#0|188984&1|csa&xyq|18824309984@163.com; UM_distinctid=16396c3a7ae5a8-053b4656fcc51d-b34356b-1fa400-16396c3a7affc8; __f_=1527568616655; _iuqxldmzr_=32; WM_TID=J%2BrEU1ukjsq7ZlpgBZJOlpGCKG1c75BP; c98xpt_=30; jsessionid-cpta=z%2BIz3uAc4JYp973wVItnPwlmVILQ8du1l7anhOckN2bGhw0jeCvTFk%2FfHgpAhdIO%5CTaKCugJ9C%5Cb8vEW9fR%2F89YhInNl4ef%2B%5CA27nYzvd%5CNZhHV7n84cn6cxXvamxBVpElUS43qGt253OV%2Bqt6Q7FW%2BEjHajP85KE%2FmFQGrWjlzj%5CeNU%3A1530588905078; vjlast=1511229112.1531728450.11; __utmz=187553192.1531728450.1.1.utmcsr=google|utmccn=(organic)|utmcmd=organic|utmctr=(not%20provided); __utma=187553192.1842392025.1503546413.1531728450.1531728449.1; __utmc=94650624; Province=020; City=0755; ne_analysis_trace_id=1533884193178; s_n_f_l_n3=91ab9d3593ff1f3a1533884193181; _antanalysis_s_id=1533884193420; vinfo_n_f_l_n3=91ab9d3593ff1f3a.1.15.1511229373536.1531728587725.1533884353912; JSESSIONID-WYYY=o7%2F6Qeil7dF1C%2BYZW5Vz8FanUVTG4qWg%2F8l%2FoxDyxxz0wkwPP5cq4jXD%5CV%2B5rxV2llmBm8dl7qwoUK50x9yko8Q6uzDZev0wg7CeZBSDlqmrI5rz2glsD6Jgz%2BKZdu%5CM2N0CSr6GHeD421g1k6HScc%2B%5CxoE2WHT9cf%2BtIeaskKr2aYW7%3A1534229751011; __utma=94650624.1842392025.1503546413.1534144531.1534227951.31; __utmz=94650624.1534227951.31.24.utmcsr=google|utmccn=(organic)|utmcmd=organic|utmctr=(not%20provided); WM_NI=T%2Fb7b6%2FlbQtbKTvDXQIJ%2B%2BS2l2lAQkbG4WQhExVrcU8CIXc4HwwgA5xQd5ifW3ZDWvuJLQmLwnj6ILoFRhEpBKWOkOqwskOtNj1DXxbnod5oSHij2qIi4dk0yrNwh5QZNUM%3D; WM_NIKE=9ca17ae2e6ffcda170e2e6eea4fb6dbc9d99b3b3798fb9ffd2c54eae8700dacd67b38bfcb1f34fb79cf7b3c22af0fea7c3b92a98f1aed8e13eedb4aeb2f76a898cbaa5db5b8b96e5ccd23ab0eea4a2d461a299fcb8d46487a89a93e25ffc9d87b9e2408ca9b988c43fbc8facd6ec6e95ed96a5d67eb79684b2f048b5b2a6d7cc48ad9a9e89c87c829599b0ea45b3a9bd8cce808eb6ffa5db74a2b2a185b8659198a78bb17b8bb7fc85ea3cbbae8298eb3f938682b6d037e2a3; playerid=72535080; __utmb=94650624.6.10.1534227951"
    }

    # 声明一个CookieJar对象实例来保存cookie
    # cookie = cookiejar.CookieJar()
    # # 利用urllib.request库的HTTPCookieProcessor对象来创建cookie处理器,也就CookieHandler
    # handler = request.HTTPCookieProcessor(cookie)
    # # 通过CookieHandler创建opener
    # opener = request.build_opener(handler)
    # #安装opener作为urlopen()使用的全局URL opener，即以后调用urlopen()时都会使用安装的opener对象
    # request.install_opener(opener)

    req = request.Request(url, test_data_url_encode, header)
    response = request.urlopen(req)
    # print(cookie)

    res = response.read()

    str1 = json.loads(res.decode('utf-8'))     # 将 bytes格式 转成 string格式 再转 字典
  
    return str1   


if __name__ == '__main__':
  load = download()
  load.searchList()
