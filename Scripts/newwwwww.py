import pandas as pd
import numpy as np
import talib as tb
import matplotlib.pyplot as plt
import yfinance as yf
import datetime

symbol = "V"
time = 60
start_date = datetime.date.today()-datetime.timedelta(days=time)
end_date = datetime.date.today()

data = yf.download(symbol, start=start_date, end= end_date, interval='1h')
data = data.drop(columns=['Volume', 'Open', 'High', 'Low', 'Adj Close'])
data = data.reset_index()
length = len(data)
data['signal'] = [0.0] * length
data['MACD'] = [0.0] * length
data['ema12'] = [0.0] * length
data['ema26'] = [0.0] * length
data['bullish'] = [0] * length
data['crossover'] = [0.0] * length

for i in range(12, length):
    data.loc[i, 'ema12'] = data.loc[range(i-12, i+1), 'Close'].mean()

for i in range(26, length):
    data.loc[i, 'ema26'] = data.loc[range(i - 26, i + 1), 'Close'].mean()

    data.loc[i,'MACD'] = (data.loc[i,'ema12'] - data.loc[i, 'ema26'])
    data.loc[i, 'signal'] = data.loc[range(i - 9, i + 1), 'MACD'].mean()

    if data.loc[i, 'ema12'] > data.loc[i, 'ema26']:
        data.loc[i, 'bullish'] = 1
    else:
        data.loc[i, 'bullish'] = -1

for i in range(27, length):
    if data.loc[i-1, 'MACD'] > data.loc[i-1, 'signal'] and data.loc[i, 'MACD'] < data.loc[i, 'signal']:
        data.loc[i, 'crossover'] = -1
    elif data.loc[i-1, 'MACD'] < data.loc[i-1, 'signal'] and data.loc[i, 'MACD'] > data.loc[i, 'signal']:
        data.loc[i, 'crossover'] = 1
    else:
        data.loc[i, 'crossover'] = 0



with pd.option_context('display.max_rows', None, 'display.max_columns', None):
    print(data)



# fig = plt.figure(figsize=(12,8))
# ax1 = fig.add_subplot(111, ylabel='Signal Range')
#
# data['ema12'].plot(ax=ax1, color='b', lw=2.)
# data['ema26'].plot(ax=ax1, color='#F39C12', lw=2.)
# data['MACD'].plot(ax=ax1, color='r', lw=2.)
# data['signal'].plot(ax=ax1, color='g', lw=2.)
#
# plt.legend(['ema12', 'ema26', 'MACD', 'signal'])
# plt.title('Crossover')
# plt.show()