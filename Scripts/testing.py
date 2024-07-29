import yfinance as yf
import datetime as d
import pandas as pd

stock = "AAPL"
date_start = d.date.today()-d.timedelta(days=300)
date_end = d.date.today()

data = yf.download(stock, start= str(date_start), end = str(date_end))
#print(dataa)

length = len(data)
values = []*length
data['ema30'] = [0]*length
for i in range(30, length):
    temp2 = data.iloc[range(i-30, i), ].mean()
    data.at['ema30'][i] = temp2

with pd.option_context('display.max_rows', None):
    print(data)
#Average = dataa.iloc[:,0:1].mean(axis=0)
#print(Average)

