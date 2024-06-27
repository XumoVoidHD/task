import requests as req
import time
import hashlib
import hmac
import uuid
import json
import uuid


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
            response = req.post(self.url + endPoint, headers=headers, data=payload)
            #response = req.request(method, self.url + endPoint, headers=headers, data=payload)
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
        res = self.generate_response(endPoint=endpoint, method=method, payload=params)

        return res

    def sell(self, symbol, orderType, qty, price= 0, category= "spot", timeInForce= "GTC", orderLinkId=False):
        endpoint="/v5/order/create"
        method = "POST"
        params = {
            "category": category,
            "symbol": symbol,
            "side": "Sell",
            "orderType": orderType,
            "qty": "50",
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

        return res

    def intstrument_info(self, category="spot"):
        endpoint = "/v5/account/wallet-balance"
        method = "GET"
        # params = {
        #     "category": "spot",
        #     'symbol': "BTCUSDT"
        # }
        params='category=spot&symbol=BTCUSDT'

        res = self.generate_response(endPoint=endpoint, method=method, payload=params)

        return res


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

    print(wrap.buy(symbol="BTCUSDT", orderType="MARKET", qty=100, category="spot", timeInForce="GTG").json())
    print(wrap.intstrument_info().json())
    # session = HTTPS("https://api.bybit.com", api_key=api_key, api_secret=secret_key)
    # session.get_wallet_balance()

