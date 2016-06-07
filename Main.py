#coding:utf-8
import urllib,urllib2,cookielib,time,AutoReserve
if __name__=="__main__":
    userUrl="/Users/ZDQ/Documents/Develop/Python/user"
    tomTimeUrl="/Users/ZDQ/Documents/Develop/Python/tomTime"
    reserveUrl="/Users/ZDQ/Documents/Develop/Python/reserve"
    autoReserve=AutoReserve.AutoReserve(userUrl,tomTimeUrl,reserveUrl)
    try :
        autoReserve.updatePerHalfHour()
    except Exception,v:
        print v
        autoReserve.cancelAll()


    

