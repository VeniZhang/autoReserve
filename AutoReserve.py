#coding:utf-8
import urllib,urllib2,cookielib,time
class AutoReserve():
    def __init__(self,userUrl,tomTimeUrl,reserveUrl):
        self.cj = cookielib.LWPCookieJar()
        self.opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cj))
        fp = open(userUrl, 'r')
        fp.readline()
        self.firstUser = fp.readline().strip()
        self.firstPwd = fp.readline().strip()
        self.secondUser = fp.readline().strip()
        self.secondPwd = fp.readline().strip()
        self.thirdUser = fp.readline().strip()
        self.thirdPwd = fp.readline().strip()
        self.devId=fp.readline().strip()
        fp.close()
        fp = open(tomTimeUrl, 'r')
        fp.readline()
        self.firstStart = fp.readline().strip()
        self.firstEnd = fp.readline().strip()
        self.secondStart = fp.readline().strip()
        self.secondEnd = fp.readline().strip()
        self.thirdStart = fp.readline().strip()
        self.thirdEnd = fp.readline().strip()
        self.reserveUrl=reserveUrl
    def login(self,userId, pwd):
        loginUrl = "http://libreserve.sau.edu.cn/ClientWeb/pro/ajax/login.aspx"
        data = {"id": userId, "pwd": pwd, "act": "login"}
        post_data = urllib.urlencode(data)
        request = urllib2.Request(loginUrl, post_data)
        html = self.opener.open(request).read()
        # if cj:
        #     print cj,html
        print "login:",userId,pwd
        if len(html)>200:
            return True
        else :
            raise Exception("login failed"+html)
    def reserve(self,devId, start, end):
        start_time="0000"
        end_time="0000"
        bookUrl = "http://libreserve.sau.edu.cn/ClientWeb/pro/ajax/reserve.aspx?dev_id=" + devId \
                  + "&lab_id=&kind_id=&type=dev&prop=&test_id=&term=&test_name=&start=" + start + \
                  "&end=" + end + "&start_time=" + start_time + "&end_time=" + end_time + "&up_file" \
                                                                                          "=""&memo=&act=set_resv&_=1464653639472"

        request = urllib2.Request(bookUrl)
        print devId,start,end
        html = self.opener.open(request).read()
        if html.find("操作成功")>-1:
             return True
        else:  raise Exception(html)
    def update(self,resvId, start, end):
        start_time="0000"
        end_time="0000"
        updateUrl = "http://libreserve.sau.edu.cn/ClientWeb/pro/ajax/reserve.aspx?resv_id=" \
                    + resvId + "&lab_id=&kind_id=&type=dev&prop=&test_id=&term=&test_name=&start=" + \
                    start + "&end=" + end + "&start_time=" + start_time + "&end_time=" + end_time + \
                    "&act=set_resv&_=1464492971590"
        request = urllib2.Request(updateUrl)
        html = self.opener.open(request).read()
        if html.find("操作成功")>-1:
            return True
        else:  raise Exception(html)
    def delete(self,resvId):
        deleteUrl = "http://libreserve.sau.edu.cn/ClientWeb/pro/ajax/reserve.aspx?act=del_resv&id=" + resvId + "&_=1464490225727"
        request = urllib2.Request(deleteUrl)
        html = self.opener.open(request).read()
        if html.find("操作成功")>-1:
             return True
        else:  raise Exception(html)
    #dev_id:100457475 date:2016-05-29 仅仅是预约座位的信息
    def getReservedSeatInfo(self,date,devId):
        url="http://libreserve.sau.edu.cn/ClientWeb/pro/ajax/device.aspx?dev_id="+devId+"&date="+date+"&act=get_rsv_sta&_=1464491157237"
        request = urllib2.Request(url)
        html = self.opener.open(request).read()
        print html
        return html
    def getReserveId(self):
        html=self.__getInfo()
        start=html.find("rsvId='")
        if start!=-1:
          id=html[start+7:start+16]
          #print "in getReserveId" + str(id)
          return id
        else :  raise Exception("no resvId")
    #会自动从reserve文件中读取数据 预约结束后会自动预约明天的座位
    def updatePerHalfHour(self):
        fp=open(self.reserveUrl, 'r')
        fp.readline()
        firstUser=fp.readline().strip()
        firstPwd=fp.readline().strip()
        self.__printUserReservedInfo("first",firstUser,fp.readline().strip(),fp.readline().strip())
        secondUser=fp.readline().strip()
        secondPwd=fp.readline().strip()
        self.__printUserReservedInfo("second", secondUser, fp.readline().strip(), fp.readline().strip())
        thirdUser=fp.readline().strip()
        thirdPwd=fp.readline().strip()
        self.__printUserReservedInfo("third", thirdUser, fp.readline().strip(), fp.readline().strip())
        fp.close()
        self.login(firstUser,firstPwd)
        firstStart,firstEnd=self.__getStartAndEndTime()
        self.login(secondUser, secondPwd)
        secondStart, secondEnd = self.__getStartAndEndTime()
        self.login(thirdUser, thirdPwd)
        thirdStart,thirdEnd = self.__getStartAndEndTime()
        n=self.__calculateNowToStart(firstStart)
        print "等待时间：" ,n-3000
        time.sleep(n-3000)#提前50分钟醒来
        i=0
        thirdIsOver=False
        secondIsOver=False
        firstIsOver=False
        #先判断 是否够一小时
        while True:
             time.sleep(1800)#单位秒
             print time.localtime()
             i+=1
             print "当前是",i,"次"
             if thirdUser !="":
                 if not thirdIsOver:
                     self.login(thirdUser, thirdPwd)
                     resvId = self.getReserveId()
                     thirdStart = self.__addHalfHour(thirdStart)
                     thirdEnd= self.__addHalfHour(thirdEnd)
                     self.__printUserReservedInfo("third", thirdUser, thirdStart, thirdEnd)
                     print "预约时长"
                     if self.__isOverHour(thirdStart,thirdEnd)>60:
                         self.update(resvId,thirdStart, thirdEnd)
                     else :
                         self. delete(resvId)
                         thirdIsOver=True
                         print "third is Over"
                         self.__save("\n"+thirdUser+"\n"+thirdPwd+"\n","w")
                         self.__reserveTom(self.thirdStart,self.thirdEnd)
                           #  预约明天的
             if secondUser!="":
                 if not secondIsOver:
                     self.login(secondUser,secondPwd)
                     resvId=self.getReserveId()
                     secondStart = self.__addHalfHour(secondStart)
                     secondEnd = self.__addHalfHour(secondEnd)
                     self.__printUserReservedInfo("second", secondUser, secondStart, secondEnd)
                     print "预约时长"
                     if self.__isOverHour(secondStart, secondEnd) >60:
                         self.update(resvId, secondStart, secondEnd, )
                     else:
                         self.delete(resvId)
                         secondIsOver=True
                         print "second is Over"
                         self.__save(secondUser + "\n" + secondPwd + "\n", "aw")
                         self.__reserveTom(self.secondStart,self.secondEnd)
                      #  预约明天的
             if firstUser!="":
                 if not firstIsOver:
                     self.login(firstUser, firstPwd)
                     resvId = self.getReserveId()
                     firstStart = self.__addHalfHour(firstStart)
                     firstEnd = self.__addHalfHour(firstEnd)
                     self.__printUserReservedInfo("first", firstUser, firstStart, firstEnd)
                     print "预约时长"
                     if self.__isOverHour(firstStart, firstEnd) > 60:
                         self.update(resvId,firstStart, firstEnd)
                     else:
                         self.delete(resvId)
                         firstIsOver=True
                         print "first is Over"
                         self.__save(firstUser + "\n" + firstPwd + "\n", "aw")
                         self.__reserveTom(self.firstStart,self.firstEnd)
                         exit(0)
    def cancelAll(self):
        user=[self.firstUser,self.secondUser,self.thirdUser]
        pwd=[self.firstPwd,self.secondPwd,self.thirdPwd]
        for i in range(0,1):
            try:
                self.login(user[i],pwd[i])
                resvId=self.getReserveId()
                self.delete(resvId)
            except:
               pass
        print "执行cancelAll 结束"
    #在此之前手动取消所有预约  根据热 tomTime文件
    def reserveTom(self):#手动预约明天
        self.login(self.firstUser, self.firstPwd)
        self.__save("\n"+self.firstUser + "\n" + self.firstPwd + "\n", "w")
        self.__reserveTom(self.firstStart, self.firstEnd)
        self.login(self.secondUser, self.secondPwd)
        self.__save(self.secondUser + "\n" + self.secondPwd + "\n", "aw")
        self.__reserveTom(self.secondStart,self.secondEnd)
        self.login(self.thirdUser, self.thirdPwd)
        self.__save(self.thirdUser + "\n" + self.thirdPwd + "\n", "aw")
        self.__reserveTom(self.thirdStart, self.thirdEnd)
    def __addHalfHour(self, s):  # 超过21的不再增加
        h = s[11:13]
        h = int(h)
        m = s[16:18]
        m = int(m)
        if h >= 21:
            return s
        m += 30
        if m >= 60:
            m -= 60
            h += 1
        h = str(h)
        m = str(m)
        if len(m) < 2:
            m = "0" + m
        if len(h) < 2:
            h = "0" + h
        return s[0:11] + h + "%3A" + m

    def __isOverHour(self, s1, s2):
        h1 = s1[11:13]
        h1 = int(h1)
        m1 = s1[16:18]
        m1 = int(m1)
        h2 = s2[11:13]
        h2 = int(h2)
        m2 = s2[16:18]
        m2 = int(m2)
        m = m2 - m1
        if m < 0:
            h = h2 - h1 - 1
            m += 60
        else:
            h = h2 - h1
        temp = h * 60 + m
        print "in isOverHour  " + str(temp)
        return h * 60 + m
    def __dayPlus(self, year, mon, day):
        m = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
        if int(year) % 4 == 0 and int(year) % 100 != 0 or int(year) % 400 == 0:
            m[1] += 1
        if day == m[mon - 1]:
            if mon != 12:
                mon += 1
            else:
                year += 1
                mon = 1
            day = 1
        else:
            day += 1
        return year, mon, day

    # start="0750"
    def __reserveTom(self, start, end):
        t = time.localtime()
        year = t.tm_year
        mon = t.tm_mon
        day = t.tm_mday
        print "预约 ", start + " to " + end
        year, mon, day = self.__dayPlus(year, mon, day)
        year = str(year)
        mon = str(mon)
        day = str(day)
        if len(mon) < 2:
            mon = "0" + mon
        if len(day) < 2:
            day = "0" + day
        t = year + "-" + mon + "-" + day + " "
        print t+start,t+end
        self.reserve(self.devId, urllib.quote_plus(t + start), urllib.quote_plus(t + end))
        self.__save(t + start + "\n" + t + end + "\n", "aw")
    def __save(self, str, method):
        fp = open(self.reserveUrl, method)
        fp.write(str)
        fp.close()
    def __printUserReservedInfo(self, order, id, start, end):
        print order + "User:", id
        print "startTime:", start
        print "endTime:", end
    #个人中心的信息
    def __getInfo(self):
        infoUrl = 'http://libreserve.sau.edu.cn/ClientWeb/xcus/a/center.aspx?_=1464430377548'
        request = urllib2.Request(infoUrl)
        html = self.opener.open(request).read()
        return  html
    def __getStartAndEndTime(self):
        html = self.__getInfo()
        index = html.find("start='")
        start = html[index + 7:index + 23]
        end = html[index + 30:index + 46]
        return urllib.quote_plus(start), urllib.quote_plus(end)
    def __calculateNowToStart(self,start):
        m = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
        start = urllib.unquote_plus(start)
        t=time.localtime()
        year=int(start[0:4])
        mon=int(start[5:7])
        day=int(start[8:10])
        hour=int(start[11:13])
        min=int(start[14:16])
        if year-t.tm_year >0:
            mon+=1
        if mon-t.tm_mon>0:
            day+=m[mon%12-1]
        dh = hour - t.tm_hour
        dmin = min - t.tm_min
        if dmin < 0:
            dh -= 1
            dmin += 60
        if day - t.tm_mday > 0:
            dh+=(24*(day-t.tm_mday))
        return (dh*60+dmin)*60


