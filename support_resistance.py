import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import mplfinance as mpf

df = yf.download('^GSPC', start= '2023-01-01')
#df = df.drop(columns=['Open', 'Volume'])
#df = df.reset_index()
length = len(df)


df['Lowest'] = df['Low'].rolling(5, center= True).min()
df['Highest'] = df['High'].rolling(5, center= True).max()
supports = df['Lowest']
resistance = df['Highest']
levels = pd.concat([supports, resistance])
with pd.option_context('display.max_rows', None):#, 'display.max_columns', None):
    print(df)
mpf.plot(df, type='candle', hlines=levels.to_list())


