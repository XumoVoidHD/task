from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime


start_date = "2019-03-24"
end_date = "2023-03-24"
symbol = "AAPL"

print("Download start")
date1 = datetime.strptime(start_date, "%Y-%m-%d")
date2 = datetime.strptime(end_date, "%Y-%m-%d")
df = yf.download(symbol, start=start_date, end=end_date)
print("Download done")
df['returns'] = np.log(df.Close.pct_change()+1)
df['direction'] = [1 if i>0 else -1 for i in df['returns']]

def lagit(df, lags):
    names = []

    for i in range(1, lags+1):
        df['Lag_'+str(i)] = df['returns'].shift(i)
        df['Lag_'+str(i)+'_dir'] = [1 if j > 0 else -1 for j in df['Lag_'+str(i)]]
        names.append('Lag_'+str(i)+'_dir')

    return names


dirnames = lagit(df, 2)
df.dropna(inplace=True)

# model = LogisticRegression()
# model.fit(df[dirnames], df['direction'])
# df['prediction_Logit'] = model.predict(df[dirnames])


train, test = train_test_split(df, shuffle=False, test_size=0.8, random_state=42)
model = LogisticRegression()
model.fit(train[dirnames], train['direction'])
test['prediction_Logit'] = model.predict(test[dirnames])
test['strat_Logit'] = test['prediction_Logit'] * test['returns']
print(np.exp(test[['returns', 'strat_Logit']].sum()))
print(np.exp(test[['returns', 'strat_Logit']].cumsum()).plot())