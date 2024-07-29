import numpy as np
import requests
from binance.client import Client
from datetime import datetime
import json
import time
import hmac
import hashlib
import pandas as pd
import talib
import matplotlib.pyplot as plt

# start_date = "2016-03-22"
# end_date = "2024-06-07"
# symbol = "AAPL"
# rsi_buy_threshold = 30
# rsi_sell_threshold = 70
ema_short = 20
ema_long = 50
# buy_weight = 10
# capital = 10000

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
        query_string = '&'.join([f"{key}={params[key]}" for key in params])

        signature = self.generate_signature(query_string)
        params["signature"] = signature

        response = requests.post(self.url + self.api_call, headers=headers, data=params)
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

        api_call = '/fapi/v2/account'
        params = {'timestamp': self.get_server_time()}
        response = self.get_response(api_call=api_call, params=params).json()
        data_list = response['positions']
        data_dict = {item['symbol']: item for item in data_list}

        return data_dict[pos]

    def balance(self):

        api_call = '/fapi/v2/balance'
        params = {'timestamp': self.get_server_time()}
        response = self.get_response(api_call=api_call, params=params)

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

    def get_income(self):

        api_call = "/fapi/v1/income"
        params = {'timestamp': self.get_server_time()}
        response = self.get_response(api_call=api_call, params=params)

        return response

    def get_klines(self, symbol, interval="1m", limit=200):

        api_call = "/fapi/v1/klines"
        params = {
            'symbol': symbol,
            'interval': interval,
            'limit': limit
        }

        response = self.get_response(api_call=api_call, params=params).json()
        data = []
        for entry in response:
            temp = {
                "Open": float(entry[1]),
                "High": float(entry[2]),
                "Low": float(entry[3]),
                "Close": float(entry[4]),
            }
            data.append(temp)
        df = pd.DataFrame(data)

        return df

    def close_pos(self, symbol, quantity=None):

        api_call = "/fapi/v1/order"
        timestamp = self.get_server_time()
        params = {
            'symbol': symbol,
            'side': 'SELL',
            'type': 'MARKET',
            'timestamp': timestamp,
        }
        if quantity is None:
            params['quantity'] = self.get_quantity(symbol)
        else:
            params['quantity'] = quantity
        response = self.post_response(api_call=api_call, params=params)

        return response


class Strategy(Broker):

    def __init__(self, api_key, api_secret):
        super().__init__(api_key, api_secret)
        self.data = self.get_klines(symbol="BTCUSDT")

    def show_data(self):
        with pd.option_context('display.max_rows', None, 'display.max_columns', None):
            print(self.data)


    def generate_BBands(self):
        self.length = len(self.data)

        price = self.data['Close']
        bbands = talib.BBANDS(price, timeperiod=15)
        self.data['Upperband'] = bbands[0]
        self.data['Middleband'] = bbands[1]
        self.data['Lowerband'] = bbands[2]
        self.data['Bullish'] = 0 * self.length
        # self.dataa['Buy_Signal'] = np.nan * self.length
        # self.dataa['Sell_Signal'] = np.nan * self.length

        for i in range(30, self.length):
            if self.data.at[i, 'Close'] > self.data.at[i, 'Upperband'] and self.data.at[i-1, 'Close'] < self.data.at[i-1, 'Upperband']:
                # self.dataa.at[i, 'Buy_Signal'] = 1 * self.dataa.at[i, 'Close']
                self.data.at[i, 'Bullish'] = 1
            if self.data.at[i, 'Close'] < self.data.at[i, 'Lowerband'] and self.data.at[i-1, 'Close'] > self.data.at[i-1, 'Lowerband']:
                # self.dataa.at[i, 'Sell_Signal'] = 1 * self.dataa.at[i, 'Close']
                self.data.at[i, 'Bullish'] = -1
        # with pd.option_context('display.max_rows', None, 'display.max_columns', None):
        #     print(self.dataa)

        # df = self.dataa
        # plt.figure(figsize=(10, 5))
        # plt.plot(df.index, df["Upperband"], label="Upperband", marker='o')
        # plt.plot(df.index, df["Middleband"], label="Middleband", marker='x')
        # plt.plot(df.index, df["Lowerband"], label="Lowerband", marker='+')
        # plt.plot(df.index, df["Close"], label="Close", marker='H')
        # plt.plot(df.index, df["Buy_Signal"], label="Bullish", marker='^')
        # plt.plot(df.index, df["Sell_Signal"], label="Bullish", marker='v')
        # plt.title("RSI_Bullish vs EMA_Bullish")
        # plt.xlabel("Index")
        # plt.ylabel("Values")
        # plt.legend()
        # plt.show()

    def execute_strategy(self):

        run = 0
        while True:
            while datetime.now().second != 0:
                time.sleep(0.1)
            self.generate_BBands()
            print(f"Iteration: {run}")
            if self.data.iloc[-1]['Bullish'] == 1:
                print("Buy Order")
                wrap.place_order(symbol='BTCUSDT',side='BUY', type='MARKET', quantity=0.02)
            elif self.data.iloc[-1]['Bullish'] == -1:
                print("Short Position")
                wrap.place_order(symbol='BTCUSDT',side='SELL', type='MARKET', quantity=0.02)
            else:
                pass
            run += 1
            time.sleep(1)

        # run = 0
        # hours = 120
        # wrap.place_order(symbol='BTCUSDT', side='BUY', type='MARKET', quantity=0.03)
        # while run != hours:
        #     self.generate_BBands()
        #     print(f"Iteration: {run}")
        #     if self.dataa.iloc[-1]['Bullish'] == 1:
        #         print("Buy Order")
        #         wrap.place_order(symbol='BTCUSDT',side='BUY', type='MARKET', quantity=0.02)
        #     elif self.dataa.iloc[-1]['Bullish']  == -1:
        #         print("Short Position")
        #         wrap.place_order(symbol='BTCUSDT',side='SELL', type='MARKET', quantity=0.02)
        #     else:
        #         pass
        #
        #     time.sleep(60)
        #     run += 1


if __name__ == "__main__":
    api_key = "72230b0e2a222e592bf49815d1ccd1ef06469a6bcbc83a6081118cc6ec771270"
    api_secret = "96eb5cda871fb203cd9b082830b2c264acdbd5822c1873d86db5d7149009666d"

    wrap = Strategy(api_key, api_secret)
    wrap.execute_strategy()


    # plt.figure(figsize=(12, 6))
    # plt.plot(df.index, df['ema50'], label='ema50')
    # plt.plot(df.index, df['ema20'], label='ema20')
    # plt.title('BTCUSDT Close Price')
    # plt.xlabel('Date')
    # plt.ylabel('Price')
    # plt.legend()
    # plt.grid(True)
    # plt.show()

