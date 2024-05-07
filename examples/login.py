from paypay import PayPay

def normal_login(phone_number, password): # 通常ログイン
    paypay = PayPay()

    paypay.login_start(phone_number, password)
    login_url = input("Login URL: ")
    result = paypay.login_confirm(login_url)
    
    token = result["payload"]["accessToken"]
    return token # アクセストークンを返す

def token_login(token): # アクセストークンを使ったログイン
    paypay = PayPay(token) # これだけ