#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# filename: iaaa.py
# modified: 2019-09-10

from urllib.parse import quote
from .client import BaseClient
# from .hook import get_hooks, debug_print_request, check_status_code, check_iaaa_success
from .const import IAAAURL, EpeURL

# _hooks_check_status_code = get_hooks(
#     debug_print_request,
#     check_status_code,
# )

# _hooks_check_iaaa_success = get_hooks(
#     debug_print_request,
#     check_status_code,
#     check_iaaa_success,
# )


class IAAAClient(BaseClient):

    # default_headers = {
    #     "Accept": "application/json, text/javascript, */*; q=0.01",
    #     "Accept-Encoding": "gzip, deflate, br",
    #     "Accept-Language": "en-US,en;q=0.9",
    #     "Host": IAAAURL.Host,
    #     "Origin": "https://%s" % IAAAURL.Host,
    #     "Connection": "keep-alive",
    # }

    def oauth_home(self, **kwargs):
        headers = kwargs.pop("headers", {})
        headers["Referer"] = EpeURL.HomePage
        headers["Upgrade-Insecure-Requests"] = "1"

        r = self._post(
            url=IAAAURL.OauthHomePage,
            params={
                "appID": "ty",
                "appName": "北京大学体测系统",
                "redirectUrl": EpeURL.SSOLoginRedirect,
                "redirectLogonUrl": EpeURL.SSOLoginRedirect,
            },
            headers=headers,
            # hooks=_hooks_check_status_code,
            **kwargs,
        )
        return r

    def oauth_login(self, username, password, **kwargs):
        headers = kwargs.pop("headers", {})
        headers["Referer"] = IAAAURL.OauthHomePage
        # headers["Referer"] = "%s?appID=syllabus&appName=%s&redirectUrl=%s" % (
        #     IAAAURL.OauthHomePage, quote("学生选课系统"), ElectiveURL.SSOLoginRedirect)
        headers["X-Requested-With"] = "XMLHttpRequest"
        r = self._post(
            url=IAAAURL.OauthLogin,
            data={
                "appid": "ty",
                "userName": username,
                "password": password,
                "randCode": "",
                "smsCode": "",
                "otpCode": "",
                "redirUrl": EpeURL.SSOLoginRedirect,
            },
            headers=headers,
            # hooks=_hooks_check_iaaa_success,
            **kwargs,
        )
        # print(headers)
        return r
