import requests as req
import time
from datetime import datetime
import hashlib
import hmac
import uuid
import json
import uuid
import urllib.parse
import pandas as pd


class Broker:

    def __init__(self, api_key, secret_key, url, recv_window):
        self.api_key = api_key
        self.secret_key = secret_key
        self.url = url
        self.recv_window = recv_window

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
            #response = req.post(self.url + endPoint, headers=headers, dataa=payload)
            response = req.request(method, self.url + endPoint, headers=headers, data=payload)
        else:
            response = req.request(method, self.url + endPoint + "?" + str(payload), headers=headers)

        return response
        # print(response.text)
        # print(response.headers)
        # print(Info + " Elapsed Time : " + str(response.elapsed))

    def genSignature(self, payload):
        param_str = self.get_time() + api_key + str(recv_window) + str(payload)
        hash = hmac.new(bytes(secret_key, "utf-8"), param_str.encode("utf-8"), hashlib.sha256)
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

    def get_klines(self, category, symbol, interval=120, limit=100):
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
        print(res)
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



if __name__ == "__main__":
    api_key = "x0eVUdWKCAnCUdEYw9"
    secret_key = "6HbJhpTSN0uuynsKpTy2I9tdmokdZqSCxmlC"
    recv_window = str(5000)
    url = "https://api-demo-testnet.bybit.com"

    wrap = Broker(api_key, secret_key, url, recv_window)
    # endpoint="/v5/order/create"
    # method="POST"
    # orderLinkId=uuid.uuid4().hex
    # params='{"category":"spot","symbol": "BTCUSDT","side": "Buy","orderType": "MARKET","qty": "100","price": "10000","timeInForce": "GTC"}'
    # print(type(params))
    # wrap.generate_response(endpoint, method, params, "Create")

    print(wrap.buy(symbol="BTCUSDT", orderType="MARKET", qty=1, category="linear", timeInForce="GTG"))
    # print(wrap.sell(symbol="BTCUSDT", orderType="MARKET", qty=1, category="linear", timeInForce="GTG"))
    # print(wrap.positions(category="linear"))
    # print(wrap.close_positions(symbol="BTCUSDT", category="linear", orderType="MARKET"))
    # print(wrap.get_balance())
    # print(wrap.get_server_time())
    # print(wrap.get_klines(category="linear", symbol="BTCUSDT"))
    # session = HTTPS("https://api.bybit.com", api_key=api_key, api_secret=secret_key)
    # session.get_wallet_balance()

