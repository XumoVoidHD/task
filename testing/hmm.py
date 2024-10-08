import requests
import time
import hashlib
import hmac
import uuid

api_key = "x0eVUdWKCAnCUdEYw9"
secret_key = "6HbJhpTSN0uuynsKpTy2I9tdmokdZqSCxmlC"
# api_key='RcIA33IxT0xbHxsOjj'
# secret_key='yd631L9kb3h1YuchJcWS2MlVy0sl1A7UciL9'
httpClient=requests.Session()
recv_window=str(5000)
url="https://api-demo-testnet.bybit.com" # Testnet endpoint


def HTTP_Request(endPoint,method,payload,Info):
    global time_stamp
    time_stamp=str(int(time.time() * 10 ** 3))
    signature=genSignature(payload)
    headers = {
        'X-BAPI-API-KEY': api_key,
        'X-BAPI-SIGN': signature,
        'X-BAPI-SIGN-TYPE': '2',
        'X-BAPI-TIMESTAMP': time_stamp,
        'X-BAPI-RECV-WINDOW': recv_window,
        'Content-Type': 'application/json'
    }
    if(method=="POST"):
        response = httpClient.request(method, url+endPoint, headers=headers, data=payload)
    else:
        response = httpClient.request(method, url+endPoint+"?"+payload, headers=headers)
    print(response.text)
    print(response.headers)
    print(Info + " Elapsed Time : " + str(response.elapsed))


def genSignature(payload):

    param_str= str(time_stamp) + api_key + recv_window + payload
    hash = hmac.new(bytes(secret_key, "utf-8"), param_str.encode("utf-8"),hashlib.sha256)
    signature = hash.hexdigest()
    return signature


#Create Order
endpoint="/v5/order/create"
method="POST"
orderLinkId=uuid.uuid4().hex
params='{"category":"spot","symbol": "BTCUSDT","side": "Buy","positionIdx": 0,"orderType": "MARKET","qty": "100","price": "10000","timeInForce": "GTC"}'
HTTP_Request(endpoint,method,params,"Create")

# #Get unfilled Orders
# endpoint="/v5/order/realtime"
# method="GET"
# params='category=linear&settleCoin=USDT'
# HTTP_Request(endpoint,method,params,"UnFilled")

# #Cancel Order
# endpoint="/v5/order/cancel"
# method="POST"
# params='{"category":"linear","symbol": "BTCUSDT","orderLinkId": "'+orderLinkId+'"}'
# HTTP_Request(endpoint,method,params,"Cancel")