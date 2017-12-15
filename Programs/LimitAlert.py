import datetime
import requests
import smtplib
import time


def send_email():
    pass


def limit_alert():
    base_url = "https://coincheck.com"
    api_rate = "/api/rate/"
    proxies = {
        'http': '',
        'https': '',
    }
    interval = 60   # sec
    upper_limit = 760000    # JPY
    lower_limit = 750000

    try:
        while True:
            current_time = datetime.datetime.now()
            print(current_time)

            r = requests.get(base_url + api_rate + "btc_jpy", proxies=proxies)
            rate = r.json()['rate']
            print('1BTC = \\' + rate)

            if float(rate) <= lower_limit:
                print('下限きった')
                send_email()

            if float(rate) >= upper_limit:
                print('上限こえた')
                send_email()

            print('===\n')
            time.sleep(interval)

    except KeyboardInterrupt:
        return


if __name__ == '__main__':
    limit_alert()
