# Public Key: 72230b0e2a222e592bf49815d1ccd1ef06469a6bcbc83a6081118cc6ec771270
# Secret Key: 96eb5cda871fb203cd9b082830b2c264acdbd5822c1873d86db5d7149009666d
import datetime
import pandas as pd
from dotenv import load_dotenv
import requests
import os
from binance.client import Client
import json
#
api_key = "72230b0e2a222e592bf49815d1ccd1ef06469a6bcbc83a6081118cc6ec771270"
api_secret = "96eb5cda871fb203cd9b082830b2c264acdbd5822c1873d86db5d7149009666d"
# headers = {'content-type': 'application/json', 'X-MBX-APIKEY': api_key}
# print(type(headers))
# url = 'https://testnet.binancefuture.com'
# api_call = '/fapi/v2/ticker/price'
# headers = {'X-MBX-APIKEY': api_key}
#
# response = requests.get(url + api_call, headers=headers)
# print(response.json())


client = Client(api_key, api_secret, testnet=True)
tickers = client.get_asset_balance(asset="ETH")
#tickers = pd.DataFrame(tickers)
print(tickers)
