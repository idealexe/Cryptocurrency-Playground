import datetime
import hashlib
import hmac
import requests
import time


base_url = 'https://coincheck.com'
api_rate = '/api/rate/'
api_transactions = '/api/exchange/orders/transactions'
api_buy_rate = '/ja/buys/rate?amount=1.0&pair='


def get_rate(pair):
    r = requests.get(base_url + api_rate + pair)
    print(r.json())
    return r.json()


if __name__ == '__main__':
    pass
