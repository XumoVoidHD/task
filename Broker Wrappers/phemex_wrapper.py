import time as t
import hmac
import hashlib
import requests
import json


class Broker:

    def __init__(self, api_key, api_secret, base_url):
        self.api_key = api_key
        self.api_secret = api_secret
        self.base_url = base_url

    def signature(self):
        pass

    def get_request(self,api_call, params):

        expire_time = str(int(t.time()) + 60)
        query_string = None
        if params is not None:
            query_string = '&'.join([f"{key}={params[key]}" for key in params])

        signature = hmac.new(self.api_secret.encode('utf-8'), (api_call+query_string+expire_time).encode('utf-8'), hashlib.sha256).hexdigest()

        header = {
            "x-phemex-request-signature": signature,
            "x-phemex-request-expiry": expire_time,
            "x-phemex-access-token": self.api_key,
        }

        response = requests.get(self.base_url+api_call+"?"+query_string, headers=header)

        return response

    def post_response(self, api_call, params):
        expire_time = str(int(t.time()) + 60)
        body = json.dumps(params, separators=(',', ':'))
        message = api_call + expire_time + body
        signature = hmac.new(self.api_secret.encode('utf-8'), message.encode('utf-8'), hashlib.sha256).hexdigest()
        header = {
            "x-phemex-request-signature": signature,
            "x-phemex-request-expiry": expire_time,
            "x-phemex-access-token": self.api_key,
        }

        response = requests.post(self.base_url + api_call, headers=header, params=params)

        return response

    def place_order(self, symbol, quantity, price, side, order_type):
        api_call = "/orders"
        params = {
            "symbol": symbol,
            "qty": quantity,
            "price": price,
            "side": side,
            "ordType": order_type,
            "timeInForce": "GTC"
        }
        response = self.post_response(api_call, params)
        return response


if __name__ == "__main__":
    api_key = "4280d308-636d-4e61-b0a2-aaa18f78daf3"
    api_secret = "lWlPr6RDwroL66u-l9CfYEhp4J8HyBlOT7ldAGWquSEwY2RkMjU1Zi0wOTRlLTQ4OGMtODMxZS1iZGU1N2ZjM2YyZGY"
    base_url = "https://testnet-api.phemex.com"

    wrap = Broker(api_key=api_key, api_secret=api_secret, base_url=base_url)
    params = {
        "actionBy": "FromOrderPlacement",
        "symbol": "BTCUSD",
        "clOrdID": "uuid-1573058952273",
        "side": "Sell",

    }
    print(wrap.post_response(api_call="/orders", params=params).json())
    #print(wrap.post_response(api_call="/spot/orders", params=params).json())
    #response = wrap.place_order(symbol='BTCUSD', quantity=1, price=50000, side='Buy', order_type='Limit')
    #print(response.json())

