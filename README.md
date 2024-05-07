# paypay.py
PayPay(paypay.ne.jp)用の非公式APIライブラリ

## 可能な操作
- アプリバージョンを取得(`get_paypay_version()`)
- ログインを開始する(`login_start("08012345678", "qwerty")`)
- ログインを完了する(`login_confirm("1234")`)
- 残高を取得(`get_balance()`)
- 履歴を確認(`get_history()`)
- プロフィールを確認(`get_profile()`)
- QRコードを取得(`get_p2p_code()`)
- 送金リンクを確認(`get_link("XXXXXXXXXXXXXXXX")`)
- 送金リンクを作成(`create_link(10)`)
- 送金リンクを受け取る(`accept_link("XXXXXXXXXXXXXXXX")`)
- 送金リンクを辞退する(`reject_link("XXXXXXXXXXXXXXXX")`)

## サンプル
### INIT
```py
from paypay import PayPay

paypay = PayPay(
    access_token="TOKEN HERE"
)
```
### Login
```py
from paypay import PayPay

paypay = PayPay()

paypay.login_start("08019816837", "P3ssW0rd")
link = input("Link: ")
paypay.login_confirm(link)
```

## インストール
### 必要環境
- Python 3.9.13
- pip 22.0.4
- git 2.42.0
### インストール
`pip install -U git+https://github.com/yuki-1729/paypay.py.git`

## ライセンス
```
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
```