import hashlib
import hmac
import math
import pprint
import requests
import time
import Settings
import sys
from datetime import datetime
pp = pprint.PrettyPrinter(indent=4)

base_url = 'https://coincheck.com'
api_transactions = '/api/exchange/orders/transactions'
api_buy_rate = '/ja/buys/rate?amount=1.0&pair='

def get_rate(pair):
    """ 販売レート取得

        販売所のレートを取得します。

        PARAMETERS
            *pair 通貨ペア (例 "btc_jpy" )
    """
    r = requests.get(base_url + '/api/rate/' + pair)
    return r.json()

def get_ticker():
    """ ティッカー

        各種最新情報を簡易に取得することができます。

        RESPONSE ITEMS
            last 最後の取引の価格
            bid 現在の買い注文の最高価格
            ask 現在の売り注文の最安価格
            high 24時間での最高取引価格
            low 24時間での最安取引価格
            volume 24時間での取引量
            timestamp 現在の時刻
    """
    r = requests.get(base_url + '/api/ticker')
    return r.json()

def private_api(url, body=''):
    """ CoincheckのプライベートAPIを使う
    """
    nonce = str(int(datetime.now().timestamp() * 1000000000))

    message = nonce + url + body
    signature = hmac.new(Settings.coincheck['Secret_Key'].encode('utf-8'), message.encode('utf-8'), hashlib.sha256).hexdigest()

    headers = {
        "ACCESS-KEY": Settings.coincheck['Access_Key'],
        "ACCESS-NONCE": nonce,
        "ACCESS-SIGNATURE": signature
    }

    r = requests.get(url, headers=headers)

    return r

def get_balance():
    """ 残高

        アカウントの残高を確認できます。
        jpy, btc には未決済の注文に利用している jpy_reserved, btc_reserved は含まれていません。
    """
    r = private_api(base_url + '/api/accounts/balance')
    return r

def post_order(order_type, rate, amount, pair='btc_jpy'):
    payload = {
        "pair": pair,
        "order_type": order_type,
        "rate": rate,
        "amount": amount
    }

    nonce = str(int(datetime.now().timestamp() * 1000000000))
    url = base_url + '/api/exchange/orders'
    body = 'pair=' + pair + '&order_type=' + order_type + '&rate=' + str(rate) + '&amount=' + str(amount)

    message = nonce + url + body
    signature = hmac.new(Settings.coincheck['Secret_Key'].encode('utf-8'), message.encode('utf-8'), hashlib.sha256).hexdigest()

    headers = {
        "ACCESS-KEY": Settings.coincheck['Access_Key'],
        "ACCESS-NONCE": nonce,
        "ACCESS-SIGNATURE": signature
    }

    r = requests.post(url, headers=headers, data=payload)
    print(r.json())

def get_orders_opens():
    """ 未決済の注文一覧

        アカウントの未決済の注文を一覧で表示します。

        RESPONSE ITEMS
            id 注文のID（新規注文でのIDと同一です）
            rate 注文のレート（ null の場合は成り行き注文です）
            pending_amount 注文の未決済の量
            pending_market_buy_amount 注文の未決済の量（現物成行買いの場合のみ）
            order_type 注文のタイプ（"sell" or "buy"）
            stop_loss_rate 逆指値レート
            pair 取引ペア
            created_at 注文の作成日時
    """
    r = private_api(base_url + '/api/exchange/orders/opens')
    return r.json()

if __name__ == '__main__':
    phase = "buy"
    principal = 13000 # 取引に使う元本（円）
    spread = 0.017  # 販売所のだいたいの売値の見積もるためのスプレッド（非公開APIを叩けば真値は得られるが・・・）
    profit_rate = 1.01   # 販売時の目標倍率

    try:
        while True:
            print(datetime.now())

            ticker = get_ticker()
            open_orders = get_orders_opens()
            order_num = len(open_orders['orders'])

            if phase is "buy":
                ask = ticker['ask']
                print("売り注文の最安値：" + str(ask) + " JPY/BTC")

                rate = math.floor(float(get_rate('btc_jpy')['rate']) * (1 + spread))
                print("販売所のレート：約" + str(rate) + " JPY/BTC")

                if ask < rate:
                    print("！現物で買う方がたぶん得！")
                    buy_rate = ask
                else:
                    print("！販売所で買う方がたぶん得！")
                    buy_rate = rate

                print(str(principal) + "円で最大" + str(principal / buy_rate) + " BTCを購入できます。")
                buy_amount = round(principal / buy_rate - 0.0001, 4)
                payment = buy_amount * buy_rate

                if order_num == 0:
                    post_order("buy", buy_rate, buy_amount)
                    print(str(payment) + "円分の買い注文（" + str(buy_amount) + " BTC）を発行しました。")
                    phase = "sell"
                elif order_num > 0:
                    print("売り注文の決済を待っています。")
                    pp.pprint(open_orders)


            elif phase is "sell":
                bid = ticker['bid']
                print("買い注文の最高値：" + str(bid) + " JPY/BTC")

                rate = math.floor(float(get_rate('btc_jpy')['rate']) * (1 - spread))
                print("販売所のレート：約" + str(rate) + " JPY/BTC")

                if bid > rate:
                    print("！現物で売る方がたぶん得！")
                else:
                    print("！販売所で売る方がたぶん得！")

                if order_num > 0:
                    print("買い注文の決済を待っています。")
                    pp.pprint(open_orders)
                elif order_num == 0:
                    target_price = payment * profit_rate
                    sell_rate = round(target_price / buy_amount)
                    print(str(buy_amount) + "BTCを" + str(target_price) + "円（" + str(sell_rate) + " JPY/BTC）で売ります。")
                    post_order("sell", sell_rate, buy_amount)
                    print("売り注文を発行しました。")
                    phase = "buy"

            time.sleep(15)
            print("---\n")

    except KeyboardInterrupt:
        print("終了します。")
        sys.exit()
