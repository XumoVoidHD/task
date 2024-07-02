# api_key = "xiZSBcGvryaj3YGTys"
# api_secret = "1cUxn7g22obd3n8YidklY8jWVfKvKvibNj3b"
import requests
import hmac
import time
import hashlib
import pandas as pd
import talib
class broker_wrapper:

    def __init__(self, api_key, api_secret):
        self.base_url = "https://api-demo-testnet.bybit.com"
        self.api_key = api_key
        self.api_secret = api_secret

    def generate_signature(self, query_string):

        return hmac.new(self.api_secret.encode('utf-8'), query_string.encode('utf-8'), hashlib.sha256).hexdigest()

    def generate_request(self, api_call, method, params=None):

        if params is None:
            params = {'timestamp': self.get_time()}
        query_string = ''.join([f"{key}={params[key]}" for key in params])
        signature = self.generate_signature(query_string)

        headers = {
            'X-BAPI-API-KEY': api_key,
            'X-BAPI-SIGN': signature,
            'X-BAPI-SIGN-TYPE': '2',
            'X-BAPI-TIMESTAMP': self.get_time(),
            'X-BAPI-RECV-WINDOW': '10000',
            'Content-Type': 'application/json'
        }

        if method == "POST":
            response = requests.post(self.base_url + api_call, headers=headers, params=params)
            return response
        elif method == "GET":
            response = requests.get(self.base_url + api_call, headers=headers, params=params)
            return response

    # def get_response(self, api_call="/fapi/v2/balance", params=None):
    #
    #     self.api_call = api_call
    #     if params is None:
    #         params = {}
    #     headers = {'X-MBX-APIKEY': api_key}
    #     query_string = '&'.join([f"{key}={params[key]}" for key in params])
    #
    #     signature = self.generate_signature(query_string)
    #     params["signature"] = signature
    #
    #     response = requests.get(self.base_url + self.api_call, headers=headers, params=params)
    #     return response
    #
    # def post_response(self, api_call="/fapi/v2/balance", params=None):
    #
    #     self.api_call = api_call
    #     if params is None:
    #         params = {}
    #     headers = {'X-MBX-APIKEY': api_key}
    #     query_string = '&'.join([f"{key}={params[key]}" for key in params])
    #
    #     signature = self.generate_signature(query_string)
    #     params["signature"] = signature
    #
    #     response = requests.post(self.base_url + self.api_call, headers=headers, params=params)
    #     return response

    def get_time(self, human_readable=False):
        # api_call = "/v5/market/time"
        #
        # response = self.generate_request(api_call=api_call, method="GET")
        # res = response.json()
        #
        # if human_readable:
        #     time_tuple = time.gmtime(int(res['result']['timeSecond']))
        #     human_time = time.strftime("%I:%M:%S %p", time_tuple)
        #
        #     return human_time
        # else:
        #     return str(int(int(res['result']['timeNano'])/1000000))
        x = str(int(time.time() * 10 ** 3))

        return x

    def place_order(self):
        endpoint = "/v5/order/create"
        method = "POST"
        params = {
            "category": "spot",
            "symbol": "BTCUSDT",
            "side": "Buy",
            "orderType": "Limit",
            "qty": "0.1",
            "price": "15600",
            "timeInForce": "PostOnly",
            "orderLinkId": "spot-test-postonly",
            "isLeverage": 0,
            "orderFilter": "Order"
        }
        return self.generate_request(api_call=endpoint, method=method, params=params).json()



if __name__ == "__main__":
    api_key = "x0eVUdWKCAnCUdEYw9"
    api_secret = "6HbJhpTSN0uuynsKpTy2I9tdmokdZqSCxmlC"

    wrap = broker_wrapper(api_key, api_secret)
    print(wrap.get_time())
    print(wrap.place_order())

