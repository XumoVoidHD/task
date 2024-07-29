import json
import hashlib
import hmac
import requests
import time


class PhemexBroker:
    def __init__(self, api_key, secret_key):
        self.api_key = api_key
        self.secret_key = secret_key
        self.base_url = 'https://testnet-api.phemex.com'

    def _generate_signature(self, timestamp, method, endpoint, body=''):
        message = f'{endpoint}{timestamp}{body}'
        signature = hmac.new(self.secret_key.encode('utf-8'), message.encode('utf-8'), hashlib.sha256).hexdigest()
        return signature

    def _headers(self, method, endpoint, body=''):
        timestamp = int(time.time() * 1000)
        signature = self._generate_signature(timestamp, method, endpoint, body)
        return {
            'x-phemex-access-token': self.api_key,
            'x-phemex-request-signature': signature,
            'x-phemex-request-expiry': str(timestamp + 60000),
            'Content-Type': 'application/json'
        }

    def get_account_info(self):
        method = 'GET'
        endpoint = '/accounts/accountPositions'
        url = self.base_url + endpoint
        headers = self._headers(method, endpoint)
        response = requests.get(url, headers=headers)
        return response.json()

    def place_order(self, symbol, side, quantity, price, order_type='Limit'):
        method = 'POST'
        endpoint = '/orders'
        url = self.base_url + endpoint
        body = {
            'symbol': symbol,
            'side': side,
            'priceEp': int(price * 10000),  # Convert price to integer format expected by Phemex
            'orderQty': quantity,
            'ordType': order_type
        }
        body_str = json.dumps(body)  # Convert the body to JSON string
        headers = self._headers(method, endpoint, body_str)
        response = requests.post(url, headers=headers, data=body_str)
        return response.json()


# Usage
api_key = '4280d308-636d-4e61-b0a2-aaa18f78daf3'
secret_key = 'lWlPr6RDwroL66u-l9CfYEhp4J8HyBlOT7ldAGWquSEwY2RkMjU1Zi0wOTRlLTQ4OGMtODMxZS1iZGU1N2ZjM2YyZGY'
broker = PhemexBroker(api_key, secret_key)

# Get account info
account_info = broker.get_account_info()
print(account_info)
params = {
    "order_type":'LIMIT',
    'side': "Buy",
    "size": "yo"

}
# Place an order
order_response = broker.place_order(symbol='BTCUSD', side='Buy', quantity=1, price=40000)
print(order_response)
