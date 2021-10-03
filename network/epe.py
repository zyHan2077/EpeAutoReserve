import time
import json
import string
import random
import hashlib
from .client import BaseClient
from .const import IAAAURL, EpeURL


def calcSign(path, timestamp, params):
    S = EpeURL.S
    result = S + path
    for key in sorted(params):
        result = result + key
        result = result + params[key]
    result += timestamp + " " + S
    return result


class EpeClient(BaseClient):

    def __init__(self, id, **kwargs):
        super().__init__(**kwargs)
        self._id = id
        self._expired_time = -1

    @property
    def id(self):
        return self._id

    @property
    def expired_time(self):
        return self._expired_time

    @property
    def is_expired(self):
        if self._expired_time == -1:
            return False
        return int(time.time()) > self._expired_time

    @property
    def has_logined(self):
        return len(self._session.cookies) > 0

    def set_expired_time(self, expired_time):
        self._expired_time = expired_time


    def redirectVenue(self, **kwargs):
        headers = kwargs.pop("headers", {})
        r = self._get(
            url=EpeURL.ggyptLogin,
            params={
                "service": EpeURL.venueLogin,
            },
            headers=headers,
            # hooks=_hooks_check_title,
            **kwargs,
        )
        return r
    
    def beforeRoleLogin(self, sso_token, **kwargs):
        headers = kwargs.pop("headers", {})
        timestamp = str(int(time.time()))
        headers["sso-token"] = sso_token
        sign = calcSign("/api/login", timestamp, {})
        # print(sign)
        headers["sign"] = hashlib.md5(sign.encode()).hexdigest()
        headers["timestamp"] = timestamp
        headers["app-key"] = EpeURL.appKey

        r = self._post(
            url=EpeURL.beforeRoleLogin,
            headers=headers,
            # hooks=_hooks_check_title,
            **kwargs,
        )
        return r
    
    def roleLogin(self, acc_token, **kwargs):
        headers = kwargs.pop("headers", {})
        timestamp = str(int(time.time()))
        headers["cgAuthorization"] = acc_token
        params = {
            "roleid": "3",
        }
        sign = calcSign("/roleLogin", timestamp, params)
        # print(sign)
        headers["sign"] = hashlib.md5(sign.encode()).hexdigest()
        headers["timestamp"] = timestamp
        headers["app-key"] = EpeURL.appKey

        r = self._post(
            url=EpeURL.RoleLogin,
            headers=headers,
            params = params,
            # hooks=_hooks_check_title,
            **kwargs,
        )
        return r
    
    def infoLookup(self, cgAuth, info, **kwargs):
        headers = kwargs.pop("headers", {})
        timestamp = str(int(time.time()))
        headers["cgAuthorization"] = cgAuth
        params = {
            "venueSiteId": info[0],
            "searchDate": info[1],
            "nocache":timestamp
        }
        sign = calcSign("/api/reservation/day/info", timestamp, params)
        # print(sign)
        headers["sign"] = hashlib.md5(sign.encode()).hexdigest()
        headers["timestamp"] = timestamp
        headers["app-key"] = EpeURL.appKey

        r = self._get(
            url=EpeURL.ReservationInfo,
            headers=headers,
            params = params,
            # hooks=_hooks_check_title,
            **kwargs,
        )
        return r

    def makeOrder(self, cgAuth, info, orderLs, **kwargs):
        headers = kwargs.pop("headers", {})
        timestamp = str(int(time.time()))
        headers["cgAuthorization"] = cgAuth
        params = {
            "venueSiteId": info[0],
            "reservationDate": info[1],
            "weekStartDate": info[1],
            "reservationOrderJson": json.dumps(orderLs)
        }
        sign = calcSign("/api/reservation/order/info", timestamp, params)
        # print(sign)
        headers["sign"] = hashlib.md5(sign.encode()).hexdigest()
        headers["timestamp"] = timestamp
        headers["app-key"] = EpeURL.appKey

        r = self._post(
            url=EpeURL.orderInfo,
            headers=headers,
            params = params,
            # hooks=_hooks_check_title,
            **kwargs,
        )
        return r
    
    def submit(self, cgAuth, info, orderLs, phone, **kwargs):
        headers = kwargs.pop("headers", {})
        timestamp = str(int(time.time()))
        headers["cgAuthorization"] = cgAuth
        params = {
            "venueSiteId": info[0],
            "reservationDate": info[1],
            "weekStartDate": info[1],
            "reservationOrderJson": json.dumps(
                orderLs
            ),
            "phone": phone,
            "isOfflineTicket": "1",
        }
        sign = calcSign("/api/reservation/order/submit", timestamp, params)
        # print(sign)
        headers["sign"] = hashlib.md5(sign.encode()).hexdigest()
        headers["timestamp"] = timestamp
        headers["app-key"] = EpeURL.appKey

        r = self._post(
            url=EpeURL.oderSubmit,
            headers=headers,
            params = params,
            # hooks=_hooks_check_title,
            **kwargs,
        )
        return r


    def logout(self, **kwargs):
        headers = kwargs.pop("headers", {})
        # headers = _get_headers_with_referer(kwargs)
        r = self._get(
            url=EpeURL.Logout,
            params={
                "service": "https://epe.pku.edu.cn/venue",
            },
            headers=headers,
            # hooks=_hooks_check_title,
            **kwargs,
        )
        # print("actual header", r.headers)
        return r

    def get_ticket(self, token, **kwargs):
        headers = kwargs.pop("headers", {})
        r = self._get(
            url = EpeURL.SSOLogin,
            params = {
                "_rand": str(random.random()),
                "token": token,
            },
            headers = headers,
            **kwargs
        )
        # print("ticket header", headers)
        return r