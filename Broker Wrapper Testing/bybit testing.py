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

    def buy(self, symbol, orderType, qty, price= 0, category= "linear", timeInForce= "GTC", orderLinkId=False):
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
        res = self.generate_response(endPoint=endpoint, method=method, payload=params)

        # print(res.json())

        return res.json()

    def sell(self, symbol, orderType, qty, price= 0, category= "linear", timeInForce= "GTC", orderLinkId=False):
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

        # print(res.json())

        return res.json()

    def close_positions(self, symbol, category, orderType, orderLinkId=False):
        endpoint="/v5/order/create"
        method = "POST"
        info = self.position_info(symbol)
        print(info)
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
        # print(params)
        res = self.generate_response(endPoint=endpoint, method=method, payload=params)

        # print(res.json())

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

class Strategy(Broker):

    def __init__(self):
        self.data = pd.DataFrame
        super().__init__()

    def generate_data(self,category="linear", symbol="BTCUSDT", interval="1", limit="100"):
        self.data = self.get_klines(category=category, symbol=symbol, interval=interval, limit=limit)

    def generating_rsi_ema(self,period=14, buy_threshold=55, sell_threshold=45, ema_short=5, ema_long=9):
        self.generate_data()
        ema_long_header = f"EMA{ema_long}"
        ema_short_header = f"EMA{ema_short}"
        length = len(self.data)
        self.data['EMA_Bullish'] = 0 * length
        self.data['RSI_Bullish'] = 0 * length
        self.data[ema_short_header] = talib.EMA(self.data['Close'], timeperiod=ema_short)
        self.data[ema_long_header] = talib.EMA(self.data['Close'], timeperiod=ema_long)
        self.data['RSI'] = talib.RSI(self.data['Close'], timeperiod=period)

        for i in range(ema_long,length):
            if self.data.loc[i, ema_short_header] > self.data.loc[i, ema_long_header] and self.data.loc[i-1, ema_short_header] < self.data.loc[i-1, ema_long_header]:
                self.data.loc[i, 'EMA_Bullish'] = 1
            elif self.data.loc[i, ema_short_header] < self.data.loc[i, ema_long_header] and self.data.loc[i - 1, ema_short_header] > self.data.loc[i - 1, ema_long_header]:
                self.data.loc[i, 'EMA_Bullish'] = -1

            if self.data.loc[i, 'RSI'] > buy_threshold:
                self.data.loc[i, 'RSI_Bullish'] = 1
            elif self.data.loc[i, 'RSI'] < sell_threshold:
                self.data.loc[i, 'RSI_Bullish'] = -1

        # with pd.option_context('display.max_rows', None, 'display.max_columns', None):
        #     print(self.data)

        # df = self.data
        # plt.figure(figsize=(10, 5))
        # plt.plot(df.index, df["RSI_Bullish"], label="RSI", marker='o')
        # plt.plot(df.index, df["EMA_Bullish"], label="EMA", marker='x')
        # plt.title("RSI_Bullish vs EMA_Bullish")
        # plt.xlabel("Index")
        # plt.ylabel("Values")
        # plt.legend()
        # plt.show()

    def execute_strategy(self):
        self.generating_rsi_ema()
        run = 0
        hours = 120
        self.buy(symbol='BTCUSDT', orderType="MARKET", qty=0.3)
        has_stock = True
        while run != hours:
            self.generating_rsi_ema()
            print(f"Iteration: {run}")
            if self.data.iloc[-1]['EMA_Bullish'] == 1 and self.data.iloc[-1]['RSI_Bullish'] == 1:
                print("Buy Order")
                has_stock = True
                self.buy(symbol='BTCUSDT', orderType="MARKET", qty=0.3)
            elif self.data.iloc[-1]['RSI_Bullish'] == -1 and self.data.iloc[-1]['RSI_Bullish'] == -1:
                if has_stock:
                    print("Close Position")
                    self.close_positions(symbol="BTCUSDT",category="linear", orderType="MARKET")
                    has_stock = False
                else:
                    print("Short Position")
                    self.sell(symbol='BTCUSDT', orderType="MARKET", qty=0.3)
                    has_stock = True
            else:
                pass

            time.sleep(60)
            run += 1

if __name__ == "__main__":
    wrap = Strategy()
    wrap.execute_strategy()


