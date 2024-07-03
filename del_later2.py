import base64
import hmac
import hashlib
import json
import requests
import time
from math import trunc


class PhemexBroker:
    TEST_NET_API_URL = 'https://testnet-api.phemex.com'

    CURRENCY_BTC = "BTC"
    CURRENCY_USD = "USD"

    SYMBOL_BTCUSD = "BTCUSD"
    SYMBOL_ETHUSD = "ETHUSD"
    SYMBOL_XRPUSD = "XRPUSD"

    SIDE_BUY = "Buy"
    SIDE_SELL = "Sell"

    ORDER_TYPE_MARKET = "Market"
    ORDER_TYPE_LIMIT = "Limit"

    TIF_IMMEDIATE_OR_CANCEL = "ImmediateOrCancel"
    TIF_GOOD_TILL_CANCEL = "GoodTillCancel"
    TIF_FOK = "FillOrKill"

    ORDER_STATUS_NEW = "New"
    ORDER_STATUS_PFILL = "PartiallyFilled"
    ORDER_STATUS_FILL = "Filled"
    ORDER_STATUS_CANCELED = "Canceled"
    ORDER_STATUS_REJECTED = "Rejected"
    ORDER_STATUS_TRIGGERED = "Triggered"
    ORDER_STATUS_UNTRIGGERED = "Untriggered"

    def __init__(self, api_key, api_secret):
        self.api_key = api_key
        self.api_secret = api_secret
        self.api_URL = self.TEST_NET_API_URL
        self.session = requests.session()

    def _send_request(self, method, endpoint, params={}, body={}):
        expiry = str(trunc(time.time()) + 60)
        query_string = '&'.join(['{}={}'.format(k, v) for k, v in params.items()])
        message = endpoint + query_string + expiry
        if body:
            body_str = json.dumps(body, separators=(',', ':'))
            message += body_str
        else:
            body_str = ""

        signature = hmac.new(self.api_secret.encode('utf-8'), message.encode('utf-8'), hashlib.sha256).hexdigest()
        self.session.headers.update({
            'x-phemex-request-signature': signature,
            'x-phemex-request-expiry': expiry,
            'x-phemex-access-token': self.api_key,
            'Content-Type': 'application/json'
        })

        url = self.api_URL + endpoint
        if query_string:
            url += '?' + query_string

        response = self.session.request(method, url, data=body_str)
        return response

    def query_account_positions(self, currency: str):
        return self._send_request("GET", "/accounts/accountPositions", {'currency': currency})

    def place_order(self, symbol, side, quantity, price=None, order_type=ORDER_TYPE_LIMIT, time_in_force=TIF_GOOD_TILL_CANCEL):
        params = {
            "symbol": symbol,
            "side": side,
            "ordType": order_type,
            "priceEp": price,
            "baseQtyEv": quantity,
            "timeInForce": time_in_force,
        }
        if order_type == self.ORDER_TYPE_MARKET:
            params.pop("priceEp")

        return self._send_request("PUT", "/orders", body=params)

    def amend_order(self, symbol, order_id, params={}):
        params["symbol"] = symbol
        params["orderID"] = order_id
        return self._send_request("PUT", "/orders/replace", params=params)

    def cancel_order(self, symbol, order_id):
        return self._send_request("DELETE", "/orders/cancel", params={"symbol": symbol, "orderID": order_id})

    def cancel_all_orders(self, symbol):
        return self._send_request("DELETE", "/orders/all", params={"symbol": symbol})

    def change_leverage(self, symbol, leverage):
        return self._send_request("PUT", "/positions/leverage", params={"symbol": symbol, "leverage": leverage})

    def change_risk_limit(self, symbol, risk_limit):
        return self._send_request("PUT", "/positions/riskLimit", params={"symbol": symbol, "riskLimit": risk_limit})

    def query_open_orders(self, symbol):
        return self._send_request("GET", "/orders/activeList", params={"symbol": symbol})

    def query_24h_ticker(self, symbol):
        return self._send_request("GET", "/md/ticker/24hr", params={"symbol": symbol})

    def query_market_data(self, symbol):
        return self._send_request("GET", "/md/orderbook", params={"symbol": symbol})

    def query_balance(self):
        return self._send_request("GET", "/phemex-user/users/children")


# Example usage
api_key = "4280d308-636d-4e61-b0a2-aaa18f78daf3"
api_secret = "lWlPr6RDwroL66u-l9CfYEhp4J8HyBlOT7ldAGWquSEwY2RkMjU1Zi0wOTRlLTQ4OGMtODMxZS1iZGU1N2ZjM2YyZGY"

broker = PhemexBroker(api_key, api_secret)

# Place an order example
order_response = broker.place_order(
    symbol=PhemexBroker.SYMBOL_BTCUSD,
    side=PhemexBroker.SIDE_BUY,
    quantity=100000,  # in satoshis, so 0.001 BTC
    price=500,  # in satoshis, so $50,000
    order_type=PhemexBroker.ORDER_TYPE_LIMIT
)
print(order_response.json())

# Query open orders example
open_orders_response = broker.query_open_orders(PhemexBroker.SYMBOL_BTCUSD)
print(open_orders_response.json())

# Cancel order example
# Assuming you have an order ID from the response



