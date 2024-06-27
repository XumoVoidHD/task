import requests
from binance.client import Client
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

    def get_klines(self, symbol, interval="1m", limit=100):

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


class Strategy:

    def __init__(self, symbol):
        self.data = None
        self.length = 0
        self.symbol = symbol

    def show_data(self):
        with pd.option_context('display.max_rows', None, 'display.max_columns', None):
            print(self.data)

    def get_data(self):
        data = wrap.get_klines(self.symbol, limit=500)

        return data

    def generateEMA(self):
        self.length = len(self.data)

        price = self.data['Close']
        self.data['ema20'] = talib.EMA(price, timeperiod=20)
        self.data['ema50'] = talib.EMA(price, timeperiod=50)
        self.data['bullish'] = [0] * self.length

        for i in range(ema_long, self.length):
            if self.data.loc[i, 'ema20'] > self.data.loc[i, 'ema50']:
                self.data.loc[i, 'bullish'] = 1
            else:
                self.data.loc[i, 'bullish'] = -1

        return self.data

    def execute_strategy(self):
        run = 0
        hours = 120
        wrap.place_order(symbol='BTCUSDT', side='BUY', type='MARKET', quantity=0.03)
        while run != hours:
            self.data = self.get_data()
            self.generateEMA()
            print(f"Iteration: {run}")
            if self.data.iloc[-2]['bullish'] == -1 and self.data.iloc[-1]['bullish'] == 1:
                print("Buy Order")
                wrap.place_order(symbol='BTCUSDT',side='BUY', type='MARKET', quantity=0.02)
            elif self.data.iloc[-2]['bullish'] == 1 and self.data.iloc[-1]['bullish'] == -1:
                print("Close Position")
                wrap.close_pos("BTCUSDT")
            else:
                pass

            time.sleep(60)
            run += 1


if __name__ == "__main__":
    api_key = "72230b0e2a222e592bf49815d1ccd1ef06469a6bcbc83a6081118cc6ec771270"
    api_secret = "96eb5cda871fb203cd9b082830b2c264acdbd5822c1873d86db5d7149009666d"

    wrap = Broker(api_key, api_secret)
    strat = Strategy("BTCUSDT")
    # df = strat.generateEMA()
    # strat.show_data()
    strat.execute_strategy()


    # plt.figure(figsize=(12, 6))
    # plt.plot(df.index, df['ema50'], label='ema50')
    # plt.plot(df.index, df['ema20'], label='ema20')
    # plt.title('BTCUSDT Close Price')
    # plt.xlabel('Date')
    # plt.ylabel('Price')
    # plt.legend()
    # plt.grid(True)
    # plt.show()

