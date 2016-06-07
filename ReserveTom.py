from AutoReserve import AutoReserve

if __name__=="__main__":
    userUrl="/Users/ZDQ/Documents/Develop/Python/user"
    tomTimeUrl="/Users/ZDQ/Documents/Develop/Python/tomTime"
    reserveUrl="/Users/ZDQ/Documents/Develop/Python/reserve"
    autoReserve=AutoReserve(userUrl,tomTimeUrl,reserveUrl)
    autoReserve.reserveTom()
