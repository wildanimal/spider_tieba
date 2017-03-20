# -*- coding: utf-8 -*-  

import string  
import urllib2  
import re

import requests
import urllib
import urllib2
import re
import cookielib


class baiduLogin:
    url_token = 'https://passport.baidu.com/v2/api/?getapi&tpl=pp&apiver=v3&tt=1426660772709&class=login&logintype=basicLogin&callback=bd__cbs__hif73f'
    url_login = 'https://passport.baidu.com/v2/api/?login'
    url_tieba = 'http://tieba.baidu.com/f/like/mylike?v=1387441831248'
    session = requests.Session()

    def startLogin(self, username, password):
        # urllib2.install_opener(self.opener)
        postData = {
            'username': username,
            'password': password,
            'token': self.getToken(),
            'charset': 'UTF-8',
            'apiver': 'v3',
            'isPhone': 'false',
            'tpl': 'pp',
            'u': 'https://passport.baidu.com/',
            'staticpage': 'https://passport.baidu.com/static/passpc-account/html/v3Jump.html',
            'callback': 'parent.bd__pcbs__ra48vi'
        }

        myhead = {
            'Host': 'passport.baidu.com',
            'Referer': 'https://passport.baidu.com/v2/?login',
            'Connection': 'keep-alive',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate, sdch',
            'Accept-Language': 'zh-CN,zh;q=0.8,en;q=0.6',
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/40.0.2214.115 Safari/537.36',
        }
        self.session.post(self.url_login, data=postData, headers=myhead)

    def getToken(self):
        r = self.session.get(u'http://www.baidu.com/')
        r = self.session.get(self.url_token)
        # 取个别名并且从分组中取出token
        token = re.search(u'"token" : "(?P<token>.*?)"', r.text)
        return token.group('token')

    def getMyTieBa(self):
        tieba = self.session.get(self.url_tieba)
        tieba.encoding = 'gbk'
        success = True if 'STATUS OK' in tieba.text else False
        if success:
            print(u'登陆成功')
        else:
            print(u'登陆失败')

        return success

  
#----------- 处理页面上的各种标签 -----------  
class HTML_Tool:  
    # 用非 贪婪模式 匹配 \t 或者 \n 或者 空格 或者 超链接 或者 图片  
    BgnCharToNoneRex = re.compile("(\t|\n| |<a.*?>|<img.*?>)")  
      
    # 用非 贪婪模式 匹配 任意<>标签  
    EndCharToNoneRex = re.compile("<.*?>")  
  
    # 用非 贪婪模式 匹配 任意<p>标签  
    BgnPartRex = re.compile("<p.*?>")  
    CharToNewLineRex = re.compile("(<br/>|</p>|<tr>|<div>|</div>)")  
    CharToNextTabRex = re.compile("<td>")  
  
    # 将一些html的符号实体转变为原始符号  
    replaceTab = [("<","<"),(">",">"),("&","&"),("&","\""),(" "," ")]  
      
    def Replace_Char(self,x):  
        x = self.BgnCharToNoneRex.sub("",x)  
        x = self.BgnPartRex.sub("\n    ",x)  
        x = self.CharToNewLineRex.sub("\n",x)  
        x = self.CharToNextTabRex.sub("\t",x)  
        x = self.EndCharToNoneRex.sub("",x)  
  
        for t in self.replaceTab:    
            x = x.replace(t[0],t[1])    
        return x    
      
class Baidu_Spider:
    session = None
    # 申明相关的属性  
    def __init__(self,url, session):
        self.session = session
        self.myUrl = url + '?see_lz=1'  
        self.datas = []  
        self.myTool = HTML_Tool()  
        print u'已经启动百度贴吧爬虫，咔嚓咔嚓'  
    
    # 初始化加载页面并将其转码储存  
    def baidu_tieba(self):  
        # 读取页面的原始信息并将其从gbk转码
        myPage = self.session.get(self.myUrl)
        myPage.encoding = 'utf-8'
        myPage = myPage.text
        # 计算楼主发布内容一共有多少页  
        endPage = self.page_counter(myPage)  
        # 获取该帖的标题  
        title = self.find_title(myPage)  
        print u'文章名称：' + title  
        # 获取最终的数据  
        self.save_data(self.myUrl,title,endPage)  
  
    #用来计算一共有多少页  
    def page_counter(self,myPage):  
        # 匹配 "共有<span class="red">12</span>页" 来获取一共有多少页  
        myMatch = re.search(r'class="red">(\d+?)</span>', myPage, re.S)  
        if myMatch:    
            endPage = int(myMatch.group(1))  
            print u'爬虫报告：发现楼主共有%d页的原创内容' % endPage  
        else:  
            endPage = 0  
            print u'爬虫报告：无法计算楼主发布内容有多少页！'  
        return endPage  
  
    # 用来寻找该帖的标题  
    def find_title(self,myPage):  
        # 匹配 <h1 class="core_title_txt" title="">xxxxxxxxxx</h1> 找出标题  
        myMatch = re.search(r'<h1.*?>(.*?)</h1>', myPage, re.S)  
        title = u'暂无标题'  
        if myMatch:  
            title  = myMatch.group(1)  
        else:  
            print u'爬虫报告：无法加载文章标题！'  
        # 文件名不能包含以下字符： \ / ： * ? " < > |  
        title = title.replace('\\','').replace('/','').replace(':','').replace('*','').replace('?','').replace('"','').replace('>','').replace('<','').replace('|','')  
        return title  
  
  
    # 用来存储楼主发布的内容  
    def save_data(self,url,title,endPage):  
        # 加载页面数据到数组中  
        self.get_data(url,endPage)  
        # 打开本地文件  
        f = open(title+'.txt','w+')
        for line in self.datas:
            f.write(line.encode('utf-8'))
        f.close()  
        print u'爬虫报告：文件已下载到本地并打包成txt文件'  
        print u'请按任意键退出...'  
        raw_input();  
  
    # 获取页面源码并将其存储到数组中  
    def get_data(self,url,endPage):  
        url = url + '&pn='  
        for i in range(1,endPage+1):  
            print u'爬虫报告：爬虫%d号正在加载中...' % i  
            myPage = self.session.get(url + str(i))
            myPage.encoding = 'utf-8'
            myPage = myPage.text
            # 将myPage中的html代码处理并存储到datas里面  
            self.deal_data(myPage)
              
  
    # 将内容从页面代码中抠出来  
    def deal_data(self,myPage):  
        myItems = re.findall('id="post_content.*?>(.*?)</div>',myPage,re.S)  
        for item in myItems:  
            data = self.myTool.Replace_Char(item.replace("\n",""))
            print(data)
            self.datas.append(data+'\n\n')
  
  
  
#-------- 程序入口处 ------------------

print u'请输入百度用户名：'
username = raw_input()
print u'请输入百度密码：'
password = raw_input()

baidu = baiduLogin()
baidu.startLogin(username, password)
# baidu.getMyTieBa()

if baidu.getMyTieBa():
    # 以某小说贴吧为例子
    # bdurl = 'http://tieba.baidu.com/p/4907972923?see_lz=1&pn=1'
    print u'请输入贴吧的地址最后的数字串：'
    bdurl = 'http://tieba.baidu.com/p/' + str(raw_input(u'http://tieba.baidu.com/p/'))

    #调用
    mySpider = Baidu_Spider(bdurl, baidu.session)
    mySpider.baidu_tieba()
