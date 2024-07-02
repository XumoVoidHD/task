import time
import hashlib
import hmac
import requests

# Replace these with your actual API key and secret
# API_KEY = 'xiZSBcGvryaj3YGTys'
# API_SECRET = '1cUxn7g22obd3n8YidklY8jWVfKvKvibNj3b'
API_KEY = "x0eVUdWKCAnCUdEYw9"
API_SECRET = "6HbJhpTSN0uuynsKpTy2I9tdmokdZqSCxmlC"


def generate_signature(params, api_secret):
    """
    Generate the HMAC SHA256 signature.
    """
    query_string = '&'.join([f"{k}={params[k]}" for k in sorted(params)])
    return hmac.new(api_secret.encode('utf-8'), query_string.encode('utf-8'), hashlib.sha256).hexdigest()


def get_server_time():
    """
    Get the server time from Bybit.
    """
    url = 'https://api.bybit.com/v2/public/time'
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()['time_now']
    else:
        raise Exception('Failed to get server time')


def place_order(symbol, side, order_type, qty, price, api_key, api_secret):
    # """
    # Place an order on Bybit.
    #
    # :param symbol: Trading pair symbol, e.g., 'BTCUSD'
    # :param side: Order side, 'Buy' or 'Sell'
    # :param order_type: Order type, e.g., 'Limit'
    # :param qty: Quantity to order
    # :param price: Price for limit orders
    # :param api_key: Your Bybit API key
    # :param api_secret: Your Bybit API secret
    # :return: Response from Bybit API
    # """
    url = 'https://api-demo-testnet.bybit.com/v5/order/create'
    server_time = get_server_time()

    params = '{"category":"spot","symbol": "BTCUSDT","side": "Buy","positionIdx": 0,"orderType": "MARKET","qty": "100","price": "10000","timeInForce": "GTC"}'

    params['sign'] = generate_signature(params, api_secret)

    response = requests.post(url, data=params)

    if response.status_code == 200:
        return response.json()
    else:
        return response.json()


# Example usage
response = place_order(
    symbol='BTCUSD',
    side='Buy',
    order_type='Limit',
    qty=1,
    price=30000,
    api_key=API_KEY,
    api_secret=API_SECRET
)
print(response)
