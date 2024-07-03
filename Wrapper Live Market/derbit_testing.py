import time
from datetime import datetime
import hashlib
import hmac
import json
import requests
import time as t
import pandas as pd
import talib
import matplotlib.pyplot as plt

class Broker:

    def __init__(self, api_key, api_secret):
        self.base_url = "https://test.deribit.com"
        self.api_key = api_key
        self. api_secret = api_secret

    def post_response(self, api_call, params=None):
        time = str(int(t.time() * 10 ** 3))
        nonce = "1231234"
        body = {
            "jsonrpc": "2.0",
            "id": "69420",
            "method": f"{api_call}"
        }

        if params is not None:
            body['params'] = params

        body = json.dumps(body)

        request_data = "POST" + "\n" + "/api/v2" + api_call + "\n" + body + "\n"
        base_signature_string = time + "\n" + nonce + "\n" + request_data
        byte_key = self.api_secret.encode()
        message = base_signature_string.encode()
        sig = hmac.new(byte_key, message, hashlib.sha256).hexdigest()

        authorization = "deri-hmac-sha256 id=" + api_key + ",ts=" + time + ",sig=" + sig + ",nonce=" + nonce
        headers = {"Authorization": authorization}

        response = requests.post((self.base_url + "/api/v2" + api_call + "?"), headers=headers, data=body)


        return response

    def get_response(self, api_call, params=None):
        api_call = "/api/v2" + api_call

        query_string = None
        if params is not None:
            query_string = '&'.join([f"{key}={params[key]}" for key in params])

        response = requests.get((self.base_url + api_call + "?"), params=query_string)

        return response

    def login(self):
        api_call = "/public/auth"
        params = {
            "grant_type": "client_credentials",
            "client_id": f"{self.api_key}",
            "client_secret": f"{self.api_secret}"
        }
        response = self.get_response(api_call, params)

        if response.status_code == 200:
            print("Login Sucessful")
            return 1
        else:
            print("Login Failed")
            return 0

    def get_server_time(self):
        api_call = "/public/get_time"
        response = self.get_response(api_call).json()

        return response['usOut']

    def buy(self, type, instrument_name="BTC-PERPETUAL", price=1):
        api_call = "/private/buy"
        params = {
            "instrument_name": f"{instrument_name}",
            "amount": f"{price}",
            "type": f"{type}",
        }

        res = self.post_response(api_call=api_call, params=params)

        return res

    def sell(self, type, instrument_name="BTC-PERPETUAL", price=1):
        api_call = "/private/sell"
        params = {
            "instrument_name": f"{instrument_name}",
            "amount": f"{price}",
            "type": f"{type}",
        }

        res = self.post_response(api_call=api_call, params=params)

        return res

    def close_pos(self, type, instrument_name="BTC-PERPETUAL"):
        api_call = "/private/close_position"
        params = {
            "instrument_name": f"{instrument_name}",
            "type": f"{type}"
        }

        res = self.post_response(api_call=api_call, params=params)

        return res

    def positions(self, instrument_name):
        api_call = "/private/get_position"
        params = {
            "instrument_name": f"{instrument_name}"
        }

        res = self.post_response(api_call=api_call, params=params)

        return res

    def get_klines(self, instrument_name, interval):
        api_call = "/public/get_tradingview_chart_data"
        days = 1
        hours = 24 * days
        current_time = int(t.time()) * 1000
        starting_time = current_time - hours*3600*1000

        params = {
            "instrument_name": f"{instrument_name}",
            "start_timestamp": f"{starting_time}",
            "end_timestamp": f"{current_time}",
            "resolution": f"{interval}"
        }

        response = self.get_response(api_call= api_call, params=params).json()
        res = response['result']
        length = len(res['ticks'])

        data = pd.DataFrame()
        data['Open'] = [0.0] * length
        data['Low'] = [0.0] * length
        data['High'] = [0.0] * length
        data['Close'] = [0.0] * length

        for i in range(0, length):
            data.loc[i, 'Open'] = float(res['open'][i])
            data.loc[i, 'High'] = float(res['high'][i])
            data.loc[i, 'Low'] = float(res['low'][i])
            data.loc[i, 'Close'] = float(res['close'][i])

        return data


class Strategy(Broker):

    def __init__(self, api_key, api_secret):
        super().__init__(api_key, api_secret)
        self.data = pd.DataFrame
        self.length = 0

    def MACD(self):
        self.data = self.get_klines(instrument_name="BTC-PERPETUAL", interval=5)
        self.length = len(self.data)
        prices = self.data['Close']
        self.data['Moving Average'] = talib.EMA(prices, timeperiod=100)
        macd = talib.MACD(prices)
        self.data["macd_line"] = macd[0]
        self.data["signal_line"] = macd[1]
        self.data["macdhist"] = macd[2]
        self.data["Bullish"] = 0 * self.length

    def generate_signal(self):

        while True:
            while datetime.now().second != 0:
                time.sleep(0.1)
            self.MACD()
            if self.data.iloc[-2]["macd_line"] < 0 and self.data.iloc[-2]["signal_line"] < 0 and self.data.iloc[-2]['Moving Average'] < self.data.iloc[-2][ "Close"]:
                if self.data.iloc[-3]["macd_line"] < self.data.iloc[-3]["signal_line"] and self.data.iloc[-2]["macd_line"] > self.data.iloc[-2]["signal_line"]:
                    print("Buy")
                    self.buy(type="market")

            if self.data.iloc[-2][ "macd_line"] > 0 and self.data.iloc[-2][ "signal_line"] > 0 and self.data.iloc[-2][ 'Moving Average'] > self.data.iloc[-2][ "Close"]:
                if self.data.iloc[-3][ "macd_line"] > self.data.iloc[-3][ "signal_line"] and self.data.iloc[-2][ "macd_line"] < self.data.iloc[-2][ "signal_line"]:
                    print("Sell")
                    self.sell(type="market")
            time.sleep(1)

        # plt.figure(figsize=(12, 8))
        # plt.plot(self.data.index, self.data["signal_line"], label='MACD', color='b')
        # plt.plot(self.data.index, self.data["macd_line"], label='Signal Line', color='r')
        # plt.bar(self.data.index,  self.data["macdhist"], label='MACD Histogram', color='g', alpha=0.5)
        # plt.title('MACD Chart')
        # plt.xlabel('Date')
        # plt.ylabel('MACD')
        # plt.legend(loc='best')
        # plt.show()

        # with pd.option_context('display.max_rows', None, 'display.max_columns', None):
        #     print(self.data)

if __name__ == "__main__":
    api_key = "57slbLl5"
    api_secret = "hj1farnku3vQbdvgyFlNnpYm2URY40tqnLNlPOlABE4"

    wrap = Strategy(api_key, api_secret)
    wrap.generate_signal()
