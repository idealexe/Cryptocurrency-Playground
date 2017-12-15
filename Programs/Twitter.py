import json
from requests_oauthlib import OAuth1Session # OAuth認証用

# 認証情報
KEY = {
    "Consumer_Key": "",
    "Consumer_Secret": "",
    "Access_Token": "",
    "Access_Token_Secret": ""
}

# 各種URL
URL = {
    "UPDATE": "https://api.twitter.com/1.1/statuses/update.json",            # ツイート用
    "SEARCH": "https://api.twitter.com/1.1/search/tweets.json",              # 検索用
    "HOME_TL": "https://api.twitter.com/1.1/statuses/home_timeline.json",    # ホームタイムライン
    "LISTS_STATUS": "https://api.twitter.com/1.1/lists/statuses.json"
}

# 認証情報を使ってセッションを作成
twitter = OAuth1Session(KEY["Consumer_Key"], KEY["Consumer_Secret"], KEY["Access_Token"], KEY["Access_Token_Secret"])


def get_json(url, params=None):
    req = twitter.get(url, params=params)
    result = None

    if req.status_code == 200:
        result = req.json()

    else:
        print('リクエストエラー：' + str(req.status_code))

    return result


def get_home_timeline():
    tweets = get_json(URL["HOME_TL"])

    for tweet in tweets:
        print_tweet(tweet)


def get_list_timeline():
    params = {
        'owner_screen_name': 'ideal_exe',
        'slug': 'main'
    }
    tweets = get_json(URL["LISTS_STATUS"], params)

    for tweet in tweets:
        print_tweet(tweet)


def print_tweet(tweet):
    user = tweet["user"]

    print((user["name"] + "  @" + user["screen_name"] + "  - " + tweet["created_at"]))
    print("----" * 30)
    print(tweet["text"] + "\n")
    print("RT: " + str(tweet["retweet_count"]))
    print("====" * 30 + "\n")


def search_tweet(keyword):
    # https://developer.twitter.com/en/docs/tweets/search/api-reference/get-search-tweets.html

    params = {
        "q": keyword,  # 検索ワード
        "count": "30"   # 取得件数
    }

    tweets = get_json(URL["SEARCH"], params=params)
    for tweet in tweets["statuses"]:
        print_tweet(tweet)


if __name__ == '__main__':
    # get_home_timeline()
    # get_list_timeline()
    search_tweet("LISK")
