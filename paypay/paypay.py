"""
MIT License

Copyright (c) 2024 Yuki

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import json
import pkce
import uuid
import datetime
import requests
import urllib.parse

from bs4 import BeautifulSoup

class PayPayError(Exception):
    pass

class PayPay:
    def __init__(self, access_token: str = None, device_uuid: str = str(uuid.uuid4()), client_uuid: str = str(uuid.uuid4()), proxy_conf: str = None) -> None:
        if proxy_conf != None:
            self.proxy_conf = {
                "http": proxy_conf,
                "https": proxy_conf
            }
        else:
            self.proxy_conf = None

        self.device_uuid = device_uuid
        self.client_uuid = client_uuid
        
        self.paypay_version = self.get_paypay_version()
        self.session = requests.Session()
        self._session = requests.Session()

        self.params = {
            "payPayLang": "ja"
        }

        self.headers = {
            "Host": "app4.paypay.ne.jp",
            "Client-Os-Type": "ANDROID",
            "Device-Acceleration-2": "NULL",
            "Device-Name": "SM-G955N",
            "Is-Emulator": "false",
            "Device-Rotation": "NULL",
            "Device-Manufacturer-Name": "samsung",
            "Client-Os-Version": "28.0.0",
            "Device-Brand-Name": "samsung",
            "Device-Orientation": "NULL",
            "Device-Uuid": device_uuid,
            "Device-Acceleration": "NULL",
            "Device-Rotation-2": "NULL",
            "Client-Os-Release-Version": "9",
            "Client-Type": "PAYPAYAPP",
            "Client-Uuid": client_uuid,
            "Device-Hardware-Name": "samsungexynox8895",
            "Device-Orientation-2": "NULL",
            "Network-Status": "WIFI",
            "Client-Mode": "NORMAL",
            "System-Locale": "ja",
            "Timezone": "Asia/Tokyo",
            "Accept-Charset": "UTF-8",
            "Accept": "*/*",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "close",
            "Client-Version": self.paypay_version,
            "User-Agent": f"PaypayApp/{self.paypay_version} Android9"
        }

        if access_token != None:
            self.headers["Authorization"] = f"Bearer {access_token}"

    def get_paypay_version(self) -> str:
        response = requests.get("https://apps.apple.com/jp/app/paypay-%E3%83%9A%E3%82%A4%E3%83%9A%E3%82%A4/id1435783608")
        soup = BeautifulSoup(response.text, "html.parser")
        base_element = json.loads(list(json.loads(soup.find("script", attrs={"id": "shoebox-media-api-cache-apps"}).text).values())[0])
        version = base_element["d"][0]["attributes"]["platformAttributes"]["ios"]["versionHistory"][0]["versionDisplay"]
        return version
    
    def login_start(self, phone_number: str, password: str) -> None:
        self.verifier, self.challenge = pkce.generate_pkce_pair(code_verifier_length=43)

        response = self.session.post(
            "https://app4.paypay.ne.jp/bff/v2/oauth2/par",
            params=self.params,
            headers=self.headers,
            data={
                "clientId": "pay2-mobile-app-client",
                "clientAppVersion": self.paypay_version,
                "clientOsVersion": "28.0.0",
                "clientOsType": "ANDROID",
                "responseType": "code",
                "redirectUri": "paypay://oauth2/callback",
                "state": pkce.generate_code_verifier(length=43),
                "codeChallenge": self.challenge,
                "codeChallengeMethod": "S256",
                "scope": "REGULAR",
                "tokenVersion": "v2",
                "prompt": "",
                "uiLocales": "ja"
            },
            proxies=self.proxy_conf
        ).json()
        if response["header"]["resultCode"] != "S0000":
            raise PayPayError(response["header"]["resultCode"], response["header"]["resultMessage"])
        request_uri = response["payload"]["requestUri"]

        self.session.get(
            "https://www.paypay.ne.jp/portal/api/v2/oauth2/authorize",
            params={
                "client_id": "pay2-mobile-app-client",
                "request_uri": request_uri
            },
            headers={
                "Host": "www.paypay.ne.jp",
                "Pragma": "no-cache",
                "Cache-Control": "no-cache",
                "Upgrade-Insecure-Requests": "1",
                "User-Agent": f"Mozilla/5.0 (Linux; Android 9; SM-G955N Build/NRD90M.G955NKSU1AQDC; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/92.0.4515.131 Mobile Safari/537.36 jp.pay2.app.android/{self.paypay_version}",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
                "X-Requested-With": "jp.ne.paypay.android.app",
                "Sec-Fetch-Site": "none",
                "Sec-Fetch-Mode": "navigate",
                "Sec-Fetch-User": "?1",
                "Sec-Fetch-Dest": "document",
                "Accept-Encoding": "gzip, deflate",
                "Accept-Language": "ja-JP,ja;q=0.9,en-US;q=0.8,en;q=0.7",
                "Connection": "close"
            },
            proxies=self.proxy_conf
        )

        response = self.session.get(
            "https://www.paypay.ne.jp/portal/api/v2/oauth2/par/check",
            headers={
                "Host": "www.paypay.ne.jp",
                "Pragma": "no-cache",
                "Cache-Control": "no-cache",
                "User-Agent": f"Mozilla/5.0 (Linux; Android 9; SM-G955N Build/NRD90M.G955NKSU1AQDC; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/92.0.4515.131 Mobile Safari/537.36 jp.pay2.app.android/{self.paypay_version}",
                "Accept": "application/json, text/plain, */*",
                "Client-Os-Version": "28.0.0",
                "Client-Version": self.paypay_version,
                "Client-Type": "PAYPAYAPP",
                "Client-App-Load-Start": str(round(datetime.datetime.now().timestamp())),
                "Client-Id": "pay2-mobile-app-client",
                "Sentry-Trace": "NULL",
                "Baggage": "NULL",
                "X-Requested-With": "jp.ne.paypay.android.app",
                "Sec-Fetch-Site": "same-origin",
                "Sec-Fetch-Mode": "cors",
                "Sec-Fetch-User": "empty",
                "Referer": "https://www.paypay.ne.jp/portal/oauth2/sign-in?client_id=pay2-mobile-app-client&mode=landing",
                "Accept-Encoding": "gzip, deflate",
                "Accept-Language": "ja-JP,ja;q=0.9,en-US;q=0.8,en;q=0.7"
            },
            proxies=self.proxy_conf
        ).json()
        if response["header"]["resultCode"] != "S0000":
            raise PayPayError(response["header"]["resultCode"], response["header"]["resultMessage"])

        response = self.session.post(
            "https://www.paypay.ne.jp/portal/api/v2/oauth2/sign-in/password",
            headers={
                "Host": "www.paypay.ne.jp",
                "Pragma": "no-cache",
                "Cache-Control": "no-cache",
                "Client-Os-Version": "28.0.0",
                "Client-Version": self.paypay_version,
                "User-Agent": f"Mozilla/5.0 (Linux; Android 9; SM-G955N Build/NRD90M.G955NKSU1AQDC; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/92.0.4515.131 Mobile Safari/537.36 jp.pay2.app.android/{self.paypay_version}",
                "Content-Type": "application/json",
                "Accept": "application/json, text/plain, */*",
                "Client-App-Load-Start": str(round(datetime.datetime.now().timestamp())),
                "Client-Type": "PAYPAYAPP",
                "Sentry-Trace": "NULL",
                "Baggage": "NULL",
                "Origin": "https://www.paypay.ne.jp",
                "X-Requested-With": "jp.ne.paypay.android.app",
                "Sec-Fetch-Site": "same-origin",
                "Sec-Fetch-Mode": "cors",
                "Sec-Fetch-Dest": "empty",
                "Referer": "https://www.paypay.ne.jp/portal/oauth2/sign-in?client_id=pay2-mobile-app-client&mode=landing",
                "Accept-Encoding": "gzip, deflate",
                "Accept-Language": "ja-JP,ja;q=0.9,en-US;q=0.8,en;q=0.7",
            },
            json={
                "username": phone_number,
                "password": password,
                "signInAttemptCount": 1
            },
            proxies=self.proxy_conf
        ).json()
        if response["header"]["resultCode"] != "S0000":
            raise PayPayError(response["header"]["resultCode"], response["header"]["resultMessage"])
        
        response = self.session.post(
            "https://www.paypay.ne.jp/portal/api/v2/oauth2/extension/code-grant/update",
            headers={
                "Host": "www.paypay.ne.jp",
                "Pragma": "no-cache",
                "Cache-Control": "no-cache",
                "Client-Os-Version": "28.0.0",
                "Client-Version": self.paypay_version,
                "User-Agent": f"Mozilla/5.0 (Linux; Android 9; SM-G955N Build/NRD90M.G955NKSU1AQDC; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/92.0.4515.131 Mobile Safari/537.36 jp.pay2.app.android/{self.paypay_version}",
                "Content-Type": "application/json",
                "Accept": "application/json, text/plain, */*",
                "Client-Type": "PAYPAYAPP",
                "Client-App-Load-Start": str(round(datetime.datetime.now().timestamp())),
                "Sentry-Trace": "NULL",
                "Baggage": "NULL",
                "Origin": "https://www.paypay.ne.jp",
                "X-Requested-With": "jp.ne.paypay.android.app",
                "Sec-Fetch-Site": "same-origin",
                "Sec-Fetch-Mode": "cors",
                "Sec-Fetch-Dest": "empty",
                "Referer": "https://www.paypay.ne.jp/portal/oauth2/sign-in?client_id=pay2-mobile-app-client&mode=landing",
                "Accept-Encoding": "gzip, deflate, br",
                "Accept-Language": "ja-JP,ja;q=0.9,en-US;q=0.8,en;q=0.7"
            },
            json={},
            proxies=self.proxy_conf
        ).json()
        if response["header"]["resultCode"] != "S0000":
            raise PayPayError(response["header"]["resultCode"], response["header"]["resultMessage"])
        self.ext_id = response["payload"]["request"]["extension_id"]

        response = self.session.post(
            "https://www.paypay.ne.jp/portal/api/v2/oauth2/extension/code-grant/update",
            headers={
                "Host": "www.paypay.ne.jp",
                "Pragma": "no-cache",
                "Cache-Control": "no-cache",
                "Client-Os-Version": "28.0.0",
                "Client-Version": self.paypay_version,
                "User-Agent": f"Mozilla/5.0 (Linux; Android 9; SM-G955N Build/NRD90M.G955NKSU1AQDC; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/92.0.4515.131 Mobile Safari/537.36 jp.pay2.app.android/{self.paypay_version}",
                "Content-Type": "application/json",
                "Accept": "application/json, text/plain, */*",
                "Client-Type": "PAYPAYAPP",
                "Client-App-Load-Start": str(round(datetime.datetime.now().timestamp())),
                "Sentry-Trace": "NULL",
                "Baggage": "NULL",
                "Origin": "https://www.paypay.ne.jp",
                "X-Requested-With": "jp.ne.paypay.android.app",
                "Sec-Fetch-Site": "same-origin",
                "Sec-Fetch-Mode": "cors",
                "Sec-Fetch-Dest": "empty",
                "Referer": "https://www.paypay.ne.jp/portal/oauth2/sign-in?client_id=pay2-mobile-app-client&mode=landing",
                "Accept-Encoding": "gzip, deflate, br",
                "Accept-Language": "ja-JP,ja;q=0.9,en-US;q=0.8,en;q=0.7"
            },
            json={
                "params": {
                    "extension_id": self.ext_id,
                    "data": {
                        "type": "SELECT_FLOW",
                        "payload": {
                            "flow": "OTL",
                            "sign_in_method": "MOBILE",
                            "base_url": "https://www.paypay.ne.jp/portal/oauth2/l"
                        }
                    }
                }
            },
            proxies=self.proxy_conf
        ).json()
        if response["header"]["resultCode"] != "S0000":
            raise PayPayError(response["header"]["resultCode"], response["header"]["resultMessage"])

    def login_confirm(self, login_accept_url: str) -> dict:
        if not all(key in self.session.cookies for key in ["Lang", "__Secure-request_uri"]):
            raise PayPayError(None, "先にログインを開始してください")
        
        code = dict(urllib.parse.parse_qsl(urllib.parse.urlparse(login_accept_url).query))["id"]

        response = self._session.post(
            "https://www.paypay.ne.jp/portal/api/v2/oauth2/extension/sign-in/2fa/otl/verify",
            headers={
                "Host": "www.paypay.ne.jp",
                "Pragma": "no-cache",
                "Cache-Control": "no-cache",
                "Client-Os-Version": "28.0.0",
                "User-Agent": f"Mozilla/5.0 (Linux; Android 9; SM-G955N Build/NRD90M.G955NKSU1AQDC; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/92.0.4515.131 Mobile Safari/537.36 jp.pay2.app.android/{self.paypay_version}",
                "Content-Type": "application/json",
                "Accept": "application/json, text/plain, */*",
                "Client-Type": "PAYPAYWEB",
                "Sentry-Trace": "NULL",
                "Baggage": "NULL",
                "Origin": "https://www.paypay.ne.jp",
                "Sec-Fetch-Site": "same-origin",
                "Sec-Fetch-Mode": "cors",
                "Sec-Fetch-Dest": "empty",
                "Referer": login_accept_url,
                "Accept-Encoding": "gzip, deflate, br, zstd",
                "Accept-Language": "ja-JP,ja;q=0.9,en-US;q=0.8,en;q=0.7",
            },
            json={
                "code": code,
            },
            proxies=self.proxy_conf
        ).json()
        if response["header"]["resultCode"] != "S0000":
            raise PayPayError(response["header"]["resultCode"], response["header"]["resultMessage"])
        
        otl_code = response["payload"]["otlCode"]
        
        response = self._session.post(
            "https://www.paypay.ne.jp/portal/api/v2/oauth2/extension/sign-in/2fa/otl/verify",
            headers={
                "Host": "www.paypay.ne.jp",
                "Pragma": "no-cache",
                "Cache-Control": "no-cache",
                "Client-Os-Version": "28.0.0",
                "User-Agent": f"Mozilla/5.0 (Linux; Android 9; SM-G955N Build/NRD90M.G955NKSU1AQDC; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/92.0.4515.131 Mobile Safari/537.36 jp.pay2.app.android/{self.paypay_version}",
                "Content-Type": "application/json",
                "Accept": "application/json, text/plain, */*",
                "Client-Type": "PAYPAYWEB",
                "Sentry-Trace": "NULL",
                "Baggage": "NULL",
                "Origin": "https://www.paypay.ne.jp",
                "Sec-Fetch-Site": "same-origin",
                "Sec-Fetch-Mode": "cors",
                "Sec-Fetch-Dest": "empty",
                "Referer": login_accept_url,
                "Accept-Encoding": "gzip, deflate, br, zstd",
                "Accept-Language": "ja-JP,ja;q=0.9,en-US;q=0.8,en;q=0.7",
            },
            json={
                "code": otl_code
            },
            proxies=self.proxy_conf
        ).json()
        if response["header"]["resultCode"] != "S0000":
            raise PayPayError(response["header"]["resultCode"], response["header"]["resultMessage"])

        otp = response["payload"]["otp"]

        self.session.get(
            "https://www.paypay.ne.jp/portal/oauth2/extension-select-otp",
            headers={
                "Host": "www.paypay.ne.jp",
                "Pragma": "no-cache",
                "Cache-Control": "no-cache",
                "Upgrade-Insecure-Requests": "1",
                "User-Agent": f"Mozilla/5.0 (Linux; Android 9; SM-G955N Build/NRD90M.G955NKSU1AQDC; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/92.0.4515.131 Mobile Safari/537.36 jp.pay2.app.android/{self.paypay_version}",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
                "X-Requested-With": "jp.ne.paypay.android.app",
                "Sec-Fetch-Site": "none",
                "Sec-Fetch-Mode": "navigate",
                "Sec-Fetch-User": "?1",
                "Sec-Fetch-Dest": "document",
                "Accept-Encoding": "gzip, deflate, br",
                "Accept-Language": "ja-JP,ja;q=0.9,en-US;q=0.8,en;q=0.7"
            },
            proxies=self.proxy_conf
        )
        
        response = self.session.get(
            "https://www.paypay.ne.jp/portal/api/v2/oauth2/par/check",
            headers={
                "Host": "www.paypay.ne.jp",
                "Pragma": "no-cache",
                "Cache-Control": "no-cache",
                "User-Agent": f"Mozilla/5.0 (Linux; Android 9; SM-G955N Build/NRD90M.G955NKSU1AQDC; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/92.0.4515.131 Mobile Safari/537.36 jp.pay2.app.android/{self.paypay_version}",
                "Accept": "application/json, text/plain, */*",
                "Client-Os-Version": "28.0.0",
                "Client-Version": self.paypay_version,
                "Client-Type": "PAYPAYAPP",
                "Client-App-Load-Start": str(round(datetime.datetime.now().timestamp())),
                "Client-Id": "pay2-mobile-app-client",
                "Sentry-Trace": "NULL",
                "Baggage": "NULL",
                "X-Requested-With": "jp.ne.paypay.android.app",
                "Sec-Fetch-Site": "same-origin",
                "Sec-Fetch-Mode": "cors",
                "Sec-Fetch-User": "empty",
                "Referer": "https://www.paypay.ne.jp/portal/oauth2/sign-in?client_id=pay2-mobile-app-client&mode=landing",
                "Accept-Encoding": "gzip, deflate",
                "Accept-Language": "ja-JP,ja;q=0.9,en-US;q=0.8,en;q=0.7"
            },
            proxies=self.proxy_conf
        ).json()
        if response["header"]["resultCode"] != "S0000":
            raise PayPayError(response["header"]["resultCode"], response["header"]["resultMessage"])
        
        response = self.session.post(
            "https://www.paypay.ne.jp/portal/api/v2/oauth2/extension/code-grant/update",
            headers={
                "Host": "www.paypay.ne.jp",
                "Pragma": "no-cache",
                "Cache-Control": "no-cache",
                "User-Agent": f"Mozilla/5.0 (Linux; Android 9; SM-G955N Build/NRD90M.G955NKSU1AQDC; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/92.0.4515.131 Mobile Safari/537.36 jp.pay2.app.android/{self.paypay_version}",
                "Content-Type": "application/json",
                "Accept": "application/json, text/plain, */*",
                "Client-Os-Version": "28.0.0",
                "Client-Version": self.paypay_version,
                "Client-Type": "PAYPAYAPP",
                "Client-App-Load-Start": str(round(datetime.datetime.now().timestamp())),
                "Sentry-Trace": "NULL",
                "Baggage": "NULL",
                "X-Requested-With": "jp.ne.paypay.android.app",
                "Sec-Fetch-Site": "same-origin",
                "Sec-Fetch-Mode": "cors",
                "Sec-Fetch-User": "empty",
                "Referer": "https://www.paypay.ne.jp/portal/oauth2/sign-in?client_id=pay2-mobile-app-client&mode=landing",
                "Accept-Encoding": "gzip, deflate",
                "Accept-Language": "ja-JP,ja;q=0.9,en-US;q=0.8,en;q=0.7"
            },
            json={
                "params": {
                    "extension_id": self.ext_id,
                    "data": {
                        "type": "CANCEL_QR_VIA_OTL_AND_PREPARE_OTP",
                        "payload": None
                    }
                }
            },
            proxies=self.proxy_conf
        ).json()
        if response["header"]["resultCode"] != "S0000":
            raise PayPayError(response["header"]["resultCode"], response["header"]["resultMessage"])
        
        response = self.session.post(
            "https://www.paypay.ne.jp/portal/api/v2/oauth2/extension/code-grant/update",
            headers={
                "Host": "www.paypay.ne.jp",
                "Pragma": "no-cache",
                "Cache-Control": "no-cache",
                "User-Agent": f"Mozilla/5.0 (Linux; Android 9; SM-G955N Build/NRD90M.G955NKSU1AQDC; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/92.0.4515.131 Mobile Safari/537.36 jp.pay2.app.android/{self.paypay_version}",
                "Content-Type": "application/json",
                "Accept": "application/json, text/plain, */*",
                "Client-Os-Version": "28.0.0",
                "Client-Version": self.paypay_version,
                "Client-Type": "PAYPAYAPP",
                "Client-App-Load-Start": str(round(datetime.datetime.now().timestamp())),
                "Sentry-Trace": "NULL",
                "Baggage": "NULL",
                "X-Requested-With": "jp.ne.paypay.android.app",
                "Sec-Fetch-Site": "same-origin",
                "Sec-Fetch-Mode": "cors",
                "Sec-Fetch-User": "empty",
                "Referer": "https://www.paypay.ne.jp/portal/oauth2/sign-in?client_id=pay2-mobile-app-client&mode=landing",
                "Accept-Encoding": "gzip, deflate",
                "Accept-Language": "ja-JP,ja;q=0.9,en-US;q=0.8,en;q=0.7"
            },
            json={
                "params": {
                    "extension_id": self.ext_id,
                    "data": {
                        "type": "VERIFY_OTP",
                        "payload": {
                            "otp": otp
                        }
                    }
                }
            },
            proxies=self.proxy_conf
        ).json()
        if response["header"]["resultCode"] != "S0000":
            raise PayPayError(response["header"]["resultCode"], response["header"]["resultMessage"])
        code = dict(urllib.parse.parse_qsl(urllib.parse.urlparse(response["payload"]["redirect_uri"]).query))["code"]

        response = self.session.post(
            "https://app4.paypay.ne.jp/bff/v2/oauth2/token",
            params=self.params,
            headers=self.headers,
            data={
                "clientId": "pay2-mobile-app-client",
                "redirectUri": "paypay://oauth2/callback",
                "code": code,
                "codeVerifier": self.verifier
            },
            proxies=self.proxy_conf
        ).json()
        if response["header"]["resultCode"] != "S0000":
            raise PayPayError(response["header"]["resultCode"], response["header"]["resultMessage"])
        
        token = response["payload"]["accessToken"]
        self.headers["Authorization"] = f"Bearer {token}"

        return response
    
    def get_balance(self) -> dict:
        if not "Authorization" in self.headers:
            raise PayPayError(None, "先にログインを行ってください")

        response = self.session.get(
            "https://app4.paypay.ne.jp/bff/v1/getBalanceInfo",
            params={
                "includePendingBonusLite": "false",
                "includePending": "true",
                "includePreAuth": "true",
                "noCache": "true",
                "includeKycInfo": "true",
                "payPayLang": "ja"
            },
            headers=self.headers,
            proxies=self.proxy_conf
        ).json()
        if response["header"]["resultCode"] != "S0000":
            raise PayPayError(response["header"]["resultCode"], response["header"]["resultMessage"])
        
        return response
    
    def get_history(self, size: int = 20, cashback: bool = False) -> dict:
        if not "Authorization" in self.headers:
            raise PayPayError(None, "先にログインを行ってください")
        
        params={
            "pageSize": str(size),
            "payPayLang": "ja"
        }
        if cashback:
            params["orderTypes"] = "CASHBACK"

        response = self.session.get(
            f"https://app4.paypay.ne.jp/bff/v3/getPaymentHistory",
            params=params,
            headers=self.headers,
            proxies=self.proxy_conf
        ).json()
        if response["header"]["resultCode"] != "S0000":
            raise PayPayError(response["header"]["resultCode"], response["header"]["resultMessage"])
        
        return response
    
    def get_profile(self) -> dict:
        if not "Authorization" in self.headers:
            raise PayPayError(None, "先にログインを行ってください")

        response = self.session.get(
            "https://app4.paypay.ne.jp/bff/v2/getProfileDisplayInfo",
            params={
                "includeExternalProfileSync": "true",
                "payPayLang": "ja"
            },
            headers=self.headers,
            proxies=self.proxy_conf
        ).json()
        if response["header"]["resultCode"] != "S0000":
            raise PayPayError(response["header"]["resultCode"], response["header"]["resultMessage"])

        return response
    
    def get_p2p_code(self, session_id: str = None) -> dict:
        if not "Authorization" in self.headers:
            raise PayPayError(None, "先にログインを行ってください")

        response = self.session.post(
            f"https://app4.paypay.ne.jp/bff/v1/createP2PCode",
            params={
                "payPayLang": "ja"
            },
            headers=self.headers,
            json={
                "amount": None,
                "sessionId": session_id
            },
            proxies=self.proxy_conf
        ).json()
        if response["header"]["resultCode"] != "S0000":
            raise PayPayError(response["header"]["resultCode"], response["header"]["resultMessage"])
        
        return response
    
    def get_link(self, code: str) -> dict:
        if not "Authorization" in self.headers:
            raise PayPayError(None, "先にログインを行ってください")
        
        response = requests.get(
            "https://app4.paypay.ne.jp/bff/v2/getP2PLinkInfo",
            params={
                "verificationCode": code,
                "payPayLang": "ja"
            },
            headers=self.headers,
            proxies=self.proxy_conf
        ).json()
        if response["header"]["resultCode"] != "S0000":
            raise PayPayError(response["header"]["resultCode"], response["header"]["resultMessage"])
        
        return response
    
    def create_link(self, amount: int = 1, password: str = None) -> dict:
        if not "Authorization" in self.headers:
            raise PayPayError(None, "先にログインを行ってください")

        payload = {
            "requestId": str(uuid.uuid4()),
            "amount": amount,
            "theme": "default-sendmoney",
            "requestAt": datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
        }
        if password != None:
            payload["passcode"] = password

        response = requests.post(
            "https://app4.paypay.ne.jp/bff/v2/executeP2PSendMoneyLink",
            params=self.params,
            headers=self.headers,
            json=payload,
            proxies=self.proxy_conf
        ).json()
        if response["header"]["resultCode"] != "S0000":
            raise PayPayError(response["header"]["resultCode"], response["header"]["resultMessage"])
        
        return response
    
    def accept_link(self, code: str, password: str = None) -> dict:
        if not "Authorization" in self.headers:
            raise PayPayError(None, "先にログインを行ってください")
        
        response = requests.get(
            "https://app4.paypay.ne.jp/bff/v2/getP2PLinkInfo",
            params={
                "verificationCode": code,
                "payPayLang": "ja"
            },
            headers=self.headers,
            proxies=self.proxy_conf
        ).json()
        if response["header"]["resultCode"] != "S0000":
            raise PayPayError(response["header"]["resultCode"], response["header"]["resultMessage"])
        if response["payload"]["orderStatus"] != "PENDING":
            raise PayPayError(None, "リンクは既に受け取り済みであるか辞退済みです")
        elif response["payload"]["pendingP2PInfo"]["isSetPasscode"] and password == None:
            raise PayPayError(None, "パスワードが必要です")
        
        payload = {
            "verificationCode": code,
            "requestId": str(uuid.uuid4()),
            "requestAt": datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
            "orderId": response["payload"]["message"]["data"]["orderId"],
            "senderChannelUrl": response["payload"]["message"]["chatRoomId"],
            "senderMessageId": response["payload"]["message"]["messageId"]
        }
        if response["payload"]["pendingP2PInfo"]["isSetPasscode"]:
            payload["passcode"] = password
        
        response = requests.post(
            "https://app4.paypay.ne.jp/bff/v2/acceptP2PSendMoneyLink",
            params=self.params,
            headers=self.headers,
            json=payload,
            proxies=self.proxy_conf
        ).json()
        if response["header"]["resultCode"] != "S0000":
            raise PayPayError(response["header"]["resultCode"], response["header"]["resultMessage"])
        
        return response
    
    def reject_link(self, code: str) -> dict:
        if not "Authorization" in self.headers:
            raise PayPayError(None, "先にログインを行ってください")
        
        response = requests.get(
            "https://app4.paypay.ne.jp/bff/v2/getP2PLinkInfo",
            params={
                "verificationCode": code,
                "payPayLang": "ja"
            },
            headers=self.headers,
            proxies=self.proxy_conf
        ).json()
        if response["header"]["resultCode"] != "S0000":
            raise PayPayError(response["header"]["resultCode"], response["header"]["resultMessage"])
        if response["payload"]["orderStatus"] != "PENDING":
            raise PayPayError(None, "リンクは既に受け取り済みであるか辞退済みです")
        
        response = requests.post(
            "https://app4.paypay.ne.jp/bff/v2/rejectP2PSendMoneyLink",
            params=self.params,
            headers=self.headers,
            json={
                "verificationCode": code,
                "requestId": str(uuid.uuid4()),
                "requestAt": datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
                "orderId": response["payload"]["message"]["data"]["orderId"],
                "senderChannelUrl": response["payload"]["message"]["chatRoomId"],
                "senderMessageId": response["payload"]["message"]["messageId"]
            },
            proxies=self.proxy_conf
        ).json()
        if response["header"]["resultCode"] != "S0000":
            raise PayPayError(response["header"]["resultCode"], response["header"]["resultMessage"])
        
        return response