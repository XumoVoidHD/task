import requests as req
import time
from datetime import datetime
import hashlib
import hmac
import json
import uuid
import pandas as pd
import talib
import matplotlib.pyplot as plt
import talib
from backtesting import Backtest, Strategy
from backtesting.lib import crossover
from backtesting.test import SMA, GOOG

class Broker:

    def __init__(self):
        self.api_key = "x0eVUdWKCAnCUdEYw9"
        self.secret_key = "6HbJhpTSN0uuynsKpTy2I9tdmokdZqSCxmlC"
        self.url = "https://api-demo-testnet.bybit.com"
        self.recv_window = str(5000)

    def generate_response(self, endPoint, method, payload, Info=None):
        time_stamp = self.get_time()
        signature = self.genSignature(payload)
        headers = {
            'X-BAPI-API-KEY': self.api_key,
            'X-BAPI-SIGN': signature,
            'X-BAPI-SIGN-TYPE': '2',
            'X-BAPI-TIMESTAMP': time_stamp,
            'X-BAPI-RECV-WINDOW': self.recv_window,
            'Content-Type': 'application/json'
        }

        if (method == "POST"):
            #response = req.post(self.url + endPoint, headers=headers, data=payload)
            response = req.request(method, self.url + endPoint, headers=headers, data=payload)
        else:
            response = req.request(method, self.url + endPoint + "?" + str(payload), headers=headers)

        return response
        # print(response.text)
        # print(response.headers)
        # print(Info + " Elapsed Time : " + str(response.elapsed))

    def genSignature(self, payload):
        param_str = self.get_time() + self.api_key + str(self.recv_window) + str(payload)
        hash = hmac.new(bytes(self.secret_key, "utf-8"), param_str.encode("utf-8"), hashlib.sha256)
        signature = hash.hexdigest()
        return signature

    def get_time(self):
        x = str(int(time.time() * 10 ** 3))
        return x

    def buy(self, symbol, orderType, qty, price= 0, category= "spot", timeInForce= "GTC", orderLinkId=False):
        endpoint="/v5/order/create"
        method = "POST"
        params = {
            "category": category,
            "symbol": symbol,
            "side": "Buy",
            "orderType": orderType,
            "qty": str(qty),
            "price": str(price),
            "timeInForce": timeInForce
        }
        if orderLinkId:
            orderLinkId = uuid.uuid4().hex
            params['orderLinkId'] = orderLinkId

        params = json.dumps(params)
        print(params)
        res = self.generate_response(endPoint=endpoint, method=method, payload=params)

        return res.json()

    def sell(self, symbol, orderType, qty, price= 0, category= "spot", timeInForce= "GTC", orderLinkId=False):
        endpoint="/v5/order/create"
        method = "POST"
        params = {
            "category": category,
            "symbol": symbol,
            "side": "Sell",
            "orderType": orderType,
            "qty": f"{qty}",
            "marketUnit": "quoteCoin",
            #"reduceOnly": "true",
            #"closeOnTrigger": "true",
            # "price": str(price),
            #"timeInForce": timeInForce
        }

        if orderLinkId:
            orderLinkId = uuid.uuid4().hex
            params['orderLinkId'] = orderLinkId

        params = json.dumps(params)
        res = self.generate_response(endPoint=endpoint, method=method, payload=params)

        return res.json()

    def close_positions(self, symbol, category, orderType, orderLinkId=False):
        endpoint="/v5/order/create"
        method = "POST"
        info = self.position_info(symbol)
        size = info[0]
        type = info[1]

        params = {
            "category": category,
            "symbol": symbol,
            "orderType": orderType,
            "qty": f"{size}",
            "marketUnit": "quoteCoin",
            #"reduceOnly": "true",
            #"closeOnTrigger": "true",
            # "price": str(price),
            #"timeInForce": timeInForce
        }

        if orderLinkId:
            orderLinkId = uuid.uuid4().hex
            params['orderLinkId'] = orderLinkId

        if type == "Buy":
            params['side'] = "Sell"
        else:
            params['side'] = "Buy"

        params = json.dumps(params)
        res = self.generate_response(endPoint=endpoint, method=method, payload=params)

        return res.json()

    def positions(self, category="linear", symbol="BTCUSDT"):
        endpoint = "/v5/position/list"
        method = "GET"
        params = {
            "category": f"{category}",
            'symbol': f"{symbol}"
        }
        query_string = '&'.join([f"{key}={params[key]}" for key in params])

        res = self.generate_response(endPoint=endpoint, method=method, payload=query_string).json()

        return res['result']['list'][0]

    def position_info(self, symbol):
        res = self.positions(symbol=symbol)

        return res['size'], res['side']

    def get_balance(self):
        endpoint = "/v5/account/wallet-balance"
        method = "GET"
        params = {
            "accountType": "UNIFIED",
        }
        query_string = '&'.join([f"{key}={params[key]}" for key in params])

        res = self.generate_response(endPoint=endpoint, method=method, payload=query_string).json()

        return f"$ {res['result']['list'][0]['totalAvailableBalance']}"

    def get_server_time(self):
        endpoint = "/v5/market/time"
        method = "GET"
        params = None

        res = self.generate_response(endPoint=endpoint, method=method, payload=params).json()

        time_sec = int(res['result']['timeSecond'])
        struct_time = time.gmtime(time_sec)
        dt = datetime.fromtimestamp(time.mktime(struct_time))
        readable_time = dt.strftime("%Y-%m-%d %H:%M:%S")

        return readable_time

    def get_klines(self, category, symbol, interval="120", limit="100"):
        endpoint = "/v5/market/kline"
        method = "GET"
        params = {
            "category": f"{category}",
            "symbol": f"{symbol}",
            "interval": f"{interval}",
            "limit": f"{limit}"
        }

        query_string = '&'.join([f"{key}={params[key]}" for key in params])

        res = self.generate_response(endPoint=endpoint, method=method, payload=query_string).json()
        data = []
        for entry in res['result']['list']:
            temp_time = int(entry[0])/1000
            struct_time = time.gmtime(temp_time)
            dt = datetime.fromtimestamp(time.mktime(struct_time))
            readable_time = dt.strftime("%Y-%m-%d %H:%M:%S")

            temp = {
                "Date & Time": f"{readable_time}",
                "Open": float(entry[1]),
                "High": float(entry[2]),
                "Low": float(entry[3]),
                "Close": float(entry[4]),
            }
            data.append(temp)
        df = pd.DataFrame(data)

        return df


class RSI_EMA_Strategy(Strategy):
    def __init__(self, broker, data, params):
        super().__init__(broker, data, params)
        self.atr = None
        self.ma2 = None
        self.ma1 = None
        self.rsi = None

    def init(self):
        price = self.data.Close
        self.rsi = self.I(talib.RSI, price)
        self.ma1 = self.I(talib.EMA, price, 20)
        self.ma2 = self.I(talib.EMA, price, 50)
        self.atr = self.I(talib.ATR, self.data['High'], self.data['Low'], self.data['Close'], timeperiod=14)

    def next(self):
        price = self.data.Close[-1]
        atr_value = self.atr[-1]

        take_profit = price + 3 * atr_value
        stop_loss = price - 1.5 * atr_value
        if crossover(30, self.rsi) or crossover(self.ma1, self.ma2):
            self.buy(tp=take_profit, sl=stop_loss)
        elif crossover(self.rsi, 50) or crossover(self.ma2, self.ma1):
            self.position.close()

if __name__ == "__main__":
    # print(GOOG)
    wrap = Broker()
    data = wrap.get_klines(category="linear", symbol="BTCUSDT", interval="120", limit="1000")
    data['Date & Time'] = pd.to_datetime(data['Date & Time'])
    # print(len(data))
    data.set_index('Date & Time', inplace=True)
    # with pd.option_context('display.max_rows', None, 'display.max_columns', None):
    #     print(data)
    backtest = Backtest(data, RSI_EMA_Strategy, commission=0.002, exclusive_orders=True, cash= 1000000)
    stats = backtest.run()
    print(stats)
    backtest.plot()

# class MySMAStrategy(Strategy):
#
#     def init(self):
#         price = self.data['Close']
#         self.ma1 = self.I(SMA, price, 20)
#         self.ma2 = self.I(SMA, price, 50)
#
#     def next(self):
#         if crossover(self.ma1, self.ma2):
#             self.buy()
#         elif crossover(self.ma2, self.ma1):
#             self.sell()
#
#
# backtest = Backtest(data, MySMAStrategy, commission=0.002, exclusive_orders=True, cash=1000000)
# stats = backtest.run()
# print(stats)
# backtest.plot()