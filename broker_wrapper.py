# Secret Key: 96eb5cda871fb203cd9b082830b2c264acdbd5822c1873d86db5d7149009666d
# Public Key: 72230b0e2a222e592bf49815d1ccd1ef06469a6bcbc83a6081118cc6ec771270
import datetime
import pandas as pd
from dotenv import load_dotenv
import requests
import os
from binance.client import Client
import json
import time
import hmac
import hashlib
# client = Client(api_key, api_secret, testnet=True)
# tickers = client.get_all_tickers()
# tickers = pd.DataFrame(tickers)
# print(tickers)

# url = 'https://testnet.binancefuture.com'
# api_call = '/fapi/v2/ticker/price'
# headers = {'content-type': 'application/json', 'X-MBX-APIKEY': api_key}

# response = requests.get(url + api_call, headers=headers)
# response = pd.DataFrame(json.loads(response.text))

# res = client.get_server_time()
# ts = res['serverTime']/1000
# your_dt = datetime.datetime.fromtimestamp(ts)


class Broker:

    def __init__(self, api_key, api_secret, url="https://testnet.binancefuture.com"):
        self.api_key = api_key
        self.api_secret = api_secret
        self.url = url
        self.api_call = None
        self.login()

    def login(self):
        api_call = '/fapi/v2/balance'
        params = {'timestamp': self.get_server_time()}
        response = self.get_response(api_call=api_call, params=params)

        if response.status_code == 200:
            print("Login Successful")
        else:
            print("Login Failed")
            print(response.json())

    def generate_signature(self, query_string):
        return hmac.new(self.api_secret.encode('utf-8'), query_string.encode('utf-8'), hashlib.sha256).hexdigest()

    def get_server_time(self):
        client = Client(self.api_key, self.api_secret, testnet=True)
        time = client.get_server_time()

        return time['serverTime']

    def get_response(self, api_call="/fapi/v2/balance", params=None):
        self.api_call = api_call
        if params is None:
            params = {}
        headers = {'X-MBX-APIKEY': api_key}
        query_string = ""
        # for key in params:
        #     query_string = '&'.join([f"{key}={params[key]}"])
        query_string = '&'.join([f"{key}={params[key]}" for key in params])

        signature = self.generate_signature(query_string)
        params["signature"] = signature

        response = requests.get(self.url + self.api_call, headers=headers, params=params)
        return response

    def post_response(self, api_call="/fapi/v2/balance", params=None):
        self.api_call = api_call
        if params is None:
            params = {}
        headers = {'X-MBX-APIKEY': api_key}
        query_string = ""
        # for key in params:
        #     query_string = '&'.join([f"{key}={params[key]}"])
        query_string = '&'.join([f"{key}={params[key]}" for key in params])

        signature = self.generate_signature(query_string)
        params["signature"] = signature

        response = requests.post(self.url + self.api_call, headers=headers, params=params)
        return response

    def get_quantity(self, symbol=None):
        api_call = "/fapi/v2/positionRisk"
        params = {
            'timestamp': self.get_server_time()
        }

        response = self.get_response(api_call=api_call, params=params)
        data_list = response.json()
        data_dict = {item['symbol']: item for item in data_list}

        return data_dict[symbol]['positionAmt']

    def positions(self, pos="BTCUSDT"):
        # api_call = '/fapi/v2/account'
        # headers = {'X-MBX-APIKEY': api_key}
        # params = {'timestamp': self.get_server_time()}
        # query_string = ""
        # for key in params:
        #     query_string = '&'.join([f"{key}={params[key]}"])
        #
        # signature = self.generate_signature(query_string)
        # params["signature"] = signature
        #
        # response = requests.get(self.url + api_call, headers=headers, params=params)
        # res = response.json()
        # data_list = res['positions']
        # data_dict = {item['symbol']: item for item in data_list}
        #
        # return data_dict[pos]

        api_call = '/fapi/v2/account'
        params = {'timestamp': self.get_server_time()}
        response = self.get_response(api_call=api_call, params=params).json()
        data_list = response['positions']
        data_dict = {item['symbol']: item for item in data_list}

        return data_dict[pos]

    def balance(self):
        api_call = '/fapi/v2/balance'
        params = {'timestamp': self.get_server_time()}
        response = self.get_response(api_call=api_call, params=params).json()

        return response

    def place_order(self, symbol, side, type, quantity=None, timeInForce='GTC', price=None, stopPrice=None):
        api_call = '/fapi/v1/order'
        timestamp = self.get_server_time()
        params = {
            'symbol': symbol,
            'side': side,
            'type': type,
            'timestamp': timestamp,
            'quantity': quantity,
            # 'timeInForce': timeInForce,
            # 'price': price,
            # 'stopPrice': stopPrice
        }
        response = self.post_response(api_call=api_call, params=params)

        return response

    # def get_asset(self, symbol):
    #     client = Client(api_key, api_secret, testnet=True)
    #     return client.get_my_trades(symbol=symbol)

    def get_income(self):
        api_call = "/fapi/v1/income"
        params = {'timestamp': self.get_server_time()}
        response = self.get_response(api_call=api_call, params=params)

        return response

    def get_klines(self, symbol, interval="2h", limit=50):
        api_call = "/fapi/v1/klines"
        params = {
            'symbol': symbol,
            'interval': interval,
            'limit': limit
        }

        response = self.get_response(api_call=api_call, params=params)

        return response

    def close_pos(self, symbol, quantity=None):
        api_call = "/fapi/v1/order"
        timestamp = self.get_server_time()
        params = {
            'symbol': symbol,
            'side': 'SELL',
            'type': 'MARKET',
            'timestamp': timestamp,
            # 'closePosition': True,
            # 'stopprice': 29000
            # 'timeInForce': timeInForce,
            # 'price': price,
            # 'stopPrice': stopPrice
        }
        if quantity is None:
            params['quantity'] = self.get_quantity(symbol)
        else:
            params['quantity'] = quantity
        response = self.post_response(api_call=api_call, params=params)

        return response



# x = client.get_server_time()
# print(x)
# ts = x['serverTime']
# print(ts)


if __name__ == "__main__":
    api_key = "72230b0e2a222e592bf49815d1ccd1ef06469a6bcbc83a6081118cc6ec771270"
    api_secret = "96eb5cda871fb203cd9b082830b2c264acdbd5822c1873d86db5d7149009666d"

    wrap = Broker(api_key, api_secret)
    print(wrap.place_order(symbol='BTCUSDT',side='BUY', type='MARKET', quantity=0.02).json())
    # print(wrap.get_asset("BTCUSDT"))
    # df = pd.DataFrame(wrap.get_klines("BTCUSDT").json())
    # print(df)
    print(wrap.close_pos("BTCUSDT").json())
    #print(wrap.get_quantity("BTCUSDT"))


