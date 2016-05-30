#coding:utf-8
import urllib,urllib2,cookielib,time
class AutoReserve():
    __firstUser=""
    def login(self,userId, pwd):
        loginUrl = "http://libreserve.sau.edu.cn/ClientWeb/pro/ajax/login.aspx"
        data = {"id": userId, "pwd": pwd, "act": "login"}
        post_data = urllib.urlencode(data)
        request = urllib2.Request(loginUrl, post_data)
        html = opener.open(request).read()
        # if cj:
        #     print cj,html
        if len(html)>200:
            return True
        else :
            raise Exception("login failed")
    def reserve(self,devId, start, end):
        start_time="0000"
        end_time="0000"
        bookUrl = "http://libreserve.sau.edu.cn/ClientWeb/pro/ajax/reserve.aspx?dev_id=" + devId \
                  + "&lab_id=&kind_id=&type=dev&prop=&test_id=&term=&test_name=&start=" + start + \
                  "&end=" + end + "&start_time=" + start_time + "&end_time=" + end_time + "&up_file" \
                                                                                          "=""&memo=&act=set_resv&_=1464490078151"
        request = urllib2.Request(bookUrl)
        html = opener.open(request).read()
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
        html = opener.open(request).read()
        if html.find("操作成功")>-1:
            return True
        else:  raise Exception(html)
    def delete(self,resvId):
        deleteUrl = "http://libreserve.sau.edu.cn/ClientWeb/pro/ajax/reserve.aspx?act=del_resv&id=" + resvId + "&_=1464490225727"
        request = urllib2.Request(deleteUrl)
        html = opener.open(request).read()
        if html.find("操作成功")>-1:
             return True
        else:  raise Exception(html)
    def __getInfo(self):
        infoUrl = 'http://libreserve.sau.edu.cn/ClientWeb/xcus/a/center.aspx?_=1464430377548'
        request = urllib2.Request(infoUrl)
        html = opener.open(request).read()
        return  html

    def getReserveInfo(self,date,devId):
        url="http://libreserve.sau.edu.cn/ClientWeb/pro/ajax/device.aspx?dev_id="+devId+"&date="+date+"&act=get_rsv_sta&_=1464491157237"
        request = urllib2.Request(url)
        html = opener.open(request).read()
        print html
        return html
    def getReserveId(self):
        html=self.__getInfo()
        start=html.find("rsvId='")
        if start!=-1:
          id=html[start+7:start+16]
          print "in getReserveId" + str(id)
          return id
        else :  raise Exception("no resvId")
    def loginAndUpdate(self,userId,pwd,start,end):#延迟半小时
        self.login(userId,pwd)
        resvId = self.getReserveId()
        self.update(resvId,start,end)
    def __addHalfHour(self,s):#超过20:30的不再增加
        h=s[11:13]
        h=int(h)
        m=s[16:18]
        m=int(m)
        if h>=20and m>=30 or h>=21:
            return s
        m+=30
        if m>=60:
            m-=60
            h+=1
        h = str(h)
        m = str(m)
        if len(m) < 2:
            m = "0" + m
        if len(h) < 2:
            h = "0" + h
        return s[0:11]+h+"%3A"+m
    def __isOverHour(self,s1,s2):
        h1= s1[11:13]
        h1 = int(h1)
        m1 = s1[16:18]
        m1 = int(m1)
        h2= s2[11:13]
        h2 = int(h2)
        m2 = s2[16:18]
        m2 = int(m2)
        m=m2-m1
        if m<0:
            h=h2-h1-1
            m+60
        else :h=h2-h1
        temp=h*60+m
        print "in isOverHour  "+str(temp)
        return h*60+m
    #未考虑 闰年,
    def __dayPlus(self,year,mon,day):
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

    def __reserveTom(self,num):
        t = time.localtime()
        year=t.tm_year
        mon=t.tm_mon
        day=t.tm_mday
        if num==0:
            start="07%3A50"
            end="11%3A50"
            print "预约 0750-1150"
        if num==1:
            start="12%3A40"
            end="16%3A40"
            print "预约 12-40-16-40"
        if num==2:
            start="17%3A30"
            end="21%3A30"
            print "预约 1730-2130"
        year,mon,day=self.__dayPlus(year,mon,day)
        year=str(year)
        mon=str(mon)
        day=str(day)
        if len(mon)<2:
             mon="0"+mon
        if len(day)<2:
             day="0"+day
        t=year+"-"+mon+"-"+day+"+"
        self.reserve("100457475",t+start,t+end)
        self.__save(t+start+"\n"+t+end+"\n","aw")
    def __save(self,str,method):
        fp = open("/Users/ZDQ/Documents/Develop/Python/reserve", method)
        fp.write(str)
        fp.close()
    #会自动从文件中读取数据 预约结束后会自动预约明天的座位
    def updatePerHalfHour(self):

        fp=open("/Users/ZDQ/Documents/Develop/Python/reserve", 'r')
        firstUser=fp.readline().strip()
        firstPwd=fp.readline().strip()
        firstStart=fp.readline().strip()
        firstEnd=fp.readline().strip()
        secondUser=fp.readline().strip()
        secondPwd=fp.readline().strip()
        secondStart =fp.readline().strip()
        secondEnd = fp.readline().strip()
        thirdUser=fp.readline().strip()
        thirdPwd=fp.readline().strip()
        thirdStart = fp.readline().strip()

        thirdEnd =fp.readline().strip()
        fp.close()
        i=0;
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
                 print "third:",thirdUser
                 thirdStart=self.__addHalfHour(thirdStart)
                 print "startTime",thirdStart
                 print "endTime",thirdEnd
                 #thirdEnd=addHalfHour(thirdEnd)

                 if not thirdIsOver:
                     print "预约时长"
                     if self.__isOverHour(thirdStart,thirdEnd)>60:
                         self.loginAndUpdate(thirdUser, thirdPwd, thirdStart, thirdEnd)
                     else :
                         self.login(thirdUser,thirdPwd)
                         resvId=self.getReserveId()
                         self. delete(resvId)
                         thirdIsOver=True
                         print "third is Over"
                         self.__save(thirdUser+"\n"+thirdPwd+"\n","w")
                         self.__reserveTom(0)
                           #  预约明天的
             if secondUser!="":
                 print "second:",secondUser
                 secondStart = self.__addHalfHour(secondStart)
                 secondEnd = self.__addHalfHour(secondEnd)
                 print "startTime", secondStart
                 print "endTime", secondEnd

                 if not secondIsOver:
                     print "预约时长"
                     if self.__isOverHour(secondStart, secondEnd) >60:
                         self.loginAndUpdate(secondUser, secondPwd,  secondStart, secondEnd, )
                     else:
                         self.login(secondUser, secondPwd)
                         resvId = self.getReserveId()
                         self.delete(resvId)
                         secondIsOver=True
                         print "second is Over"
                         self.__save(secondUser + "\n" + secondPwd + "\n", "aw")
                         self.__reserveTom(1)
                      #  预约明天的
             if firstUser!="":
                 print "first",firstUser
                 print "startTime", firstStart
                 print "endTime", firstEnd
                 firstStart = self.__addHalfHour(firstStart)
                 firstEnd = self.__addHalfHour(firstEnd)
                 if not firstIsOver:
                     print "预约时长"
                     if self.__isOverHour(firstStart, firstEnd) > 60:

                         self.loginAndUpdate(firstUser, firstPwd,  firstStart, firstEnd)
                     else:
                         self.login(firstUser, firstPwd)
                         resvId =self. getReserveId()
                         self.delete(resvId)
                         firstIsOver=True
                         print "first is Over"
                         self.__save(firstUser + "\n" + firstPwd + "\n", "aw")
                         self.__reserveTom(2)
                         exit(0)
    #每天晚上程序退出,在早上手动运行
    def calculateSecondsTo0700(self):
         t=time.localtime()
         h=t.tm_hour
         m=t.tm_min
         s=t.tm_sec
        # dh=24-h+7
         dh=7-h
         dm=0-m
         if dm<0:
              dh-=1
              dm+=60
         return (dh*60+dm)*60
    def cancelAll(self):
        user=[firstUser,secondUser,thirdUser]
        pwd=[firstPwd,secondPwd,thirdPwd]
        for i in range(0,3):
            try:
                self.login(user[i],pwd[i])
                resvId=self.getReserveId()
                self.delete(resvId)
            except:
               pass


    #在此之前手动取消所有预约
    def reserveTom(self):#手动预约明天
        self.login(thirdUser,thirdPwd)
        self.__save(thirdUser + "\n" + thirdPwd + "\n", "w")
        self.__reserveTom(0)
        self.login(secondUser, secondPwd)
        self.__save(secondUser + "\n" + secondPwd + "\n", "aw")
        self.__reserveTom(1)
        self.login(firstUser, firstPwd)
        self.__save(firstUser + "\n" + firstPwd + "\n", "aw")
        self.__reserveTom(2)

    def reserveToday(self):#TODO
        fp = open("/Users/ZDQ/Documents/Develop/Python/toReserve", 'r')
        startTime = fp.readline().strip()
        endTime = fp.readline().strip()
        pass


if __name__=="__main__":
    cj = cookielib.LWPCookieJar()
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
    fp = open("/Users/ZDQ/Documents/Develop/Python/user", 'r')

    firstUser = fp.readline().strip()
    firstPwd = fp.readline().strip()
    secondUser = fp.readline().strip()
    secondPwd = fp.readline().strip()
    thirdUser = fp.readline().strip()
    thirdPwd = fp.readline().strip()
    fp.close()


    autoReserve=AutoReserve()
    # devId = "100457475"#78
    # start = "2016-05-30+08%3A00"  # 2016-05-29+14%3A50  2016-05-29 14:50
    # end = "2016-05-30+12%3A00"
    # resvId = ""  # 需要通过分析网页获取 或者 通过更新一次时间来获取

    #autoReserve.login(userId,pwd)
    autoReserve.updatePerHalfHour()
    #autoReserve.reserve(devId,start,end)
    #autoReserve.resvId=getReserveId()
    #autoReserve.update(resvId,start,end)
    #autoReserve.delete(resvId)
    # autoReserve.getReserveInfo("2016-05-30",devId)
    # n=calculateSecondsTo0700()
    # print  n
    print "睡眠中"
    #time.sleep(n)
    print "开始"
    # try :
    #      autoReserve.updatePerHalfHour()
    # except:
    #       autoReserve.cancelAll()






