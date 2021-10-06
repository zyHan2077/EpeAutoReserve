from network.iaaa import IAAAClient
from network.epe import EpeClient
import time
import random
import configparser

config = configparser.ConfigParser()
config.read("config.ini")

ua = config["loop"]["ua"]
prefer_site = eval(config["target"]["prefer_site"])
prefer_time = eval(config["target"]["prefer_time"])
game_interval = int(config["target"]["interval"])
slt = float(config["loop"]["sleepTime"])
sltNA = float(config["loop"]["sleepTimeIfNotAvail"])

def asciiTime():
    return time.asctime( time.localtime(time.time()) )

def searchForAppropSite(r, date, ts, sites, length):
    data = r.json()["data"]
    timeMap = data["spaceTimeInfo"]
    spaceMap = data["reservationDateSpaceInfo"][date]
    timeId = []
    avails = []
    for t in ts:
        timeId.append(timeMap[t]["id"])
    for tId in timeId:
        for s in sites:
            ls = spaceMap[s]
            if ls[str(tId)]["reservationStatus"] == 1:
                flag = True
                for i in range(1, length):
                    if ls[str(tId + i)]["reservationStatus"] != 1:
                        flag = False
                if flag:
                    tIds = [str(i) for i in range(tId, tId+length)]
                    avails.append((ls["id"], tIds))
    return avails


# Epe login to get cgAuthorization
epe = EpeClient(1, timeout=1000)
epe.set_user_agent(ua)
r = epe.redirectVenue()

iaaa = IAAAClient(timeout=30)
iaaa.set_user_agent(ua)
r1 = iaaa.oauth_home()
r1 = iaaa.oauth_login(config["user"]["user_id"], config["user"]["passwd"])
# print("token: ", r1.json())
try:
    if not "token" in r1.json():
        raise Exception("get token error")
    token = r1.json()["token"]
except Exception as e:
    print(r1)

r2 = epe.get_ticket(token)
sso_pku_token = epe._session.cookies.get_dict()["sso_pku_token"]
# print("sso pku token ", sso_pku_token)
r3 = epe.beforeRoleLogin(sso_pku_token)
access_token = r3.json()["data"]["token"]["access_token"]

r  = epe.roleLogin(access_token)

cgAuth = r.json()["data"]["token"]["access_token"]


## start looking for available fields
while True:
    r = epe.infoLookup(cgAuth, (config["target"]["gym"], config["target"]["date"]))
    try:
        if r.json()["message"] != "OK":
            raise Exception(r.text)
    except Exception as e:
        print(asciiTime(), ": ", e)
        time.sleep(slt + random.random())
        continue
    avails = searchForAppropSite(r, config["target"]["date"], prefer_time, prefer_site, game_interval)
    if len(avails) == 0:
        print(asciiTime(), " ", "所选时段暂无可用场地")
        time.sleep(sltNA + random.random())
        continue

    for x in avails:
        try:
            orderLs = []
            spaceId = str(x[0])
            for tId in x[1]:
                orderLs.append(
                    {
                        "spaceId": spaceId,
                        "timeId": tId,
                        "venueSpaceGroupId":None
                        }
                    )
            r2 = epe.makeOrder(cgAuth, [config["target"]["gym"], config["target"]["date"]], orderLs)
            if r2.json()["message"] != "OK":
                raise Exception(r2.text)
                time.sleep(0.5)
                continue
            
            r3 = epe.submit(cgAuth, [config["target"]["gym"], config["target"]["date"]], orderLs, config["user"]["phonenumber"])
            if r3.json()["message"] != "OK":
                raise Exception(r3.text)
                time.sleep(0.5)
                continue
            print("预订成功！记得去智慧场馆付款\n", r3.text)
            break
        except Exception as e:
            print(asciiTime(), " ", e)
            continue
    break
    

epe.logout()
