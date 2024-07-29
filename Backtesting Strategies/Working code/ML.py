from sklearn.model_selection import train_test_split
import yfinance as yf
from datetime import datetime
import talib
import pandas as pd


start_date = "2019-03-24"
end_date = "2023-03-24"
symbol = "AAPL"

date1 = datetime.strptime(start_date, "%Y-%m-%d")
date2 = datetime.strptime(end_date, "%Y-%m-%d")
data = yf.download(symbol, start=start_date, end=end_date)

data['RSI'] = talib.RSI(data['Close'])
data['EMA'] = talib.RSI(data['Close'])
data['ADX'] = talib.ADX(data['High'], data['Low'], data['Close'])
data = data.dropna()
data = data.drop('Open', axis=1)
data = data.drop('Volume', axis=1)
data = data.drop('Close', axis=1)

with pd.option_context('display.max_rows', None, 'display.max_columns', None):
    print(data)

X = data[['RSI', 'EMA', "ADX"]]
y = data[['High', 'Low', 'Adj Close']]

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.8, random_state=42)


