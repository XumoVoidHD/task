import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime


capital = 10000

# company_list = [
#     "AAPL", "MSFT", "AMZN", "GOOGL", "GOOG", "NVDA", "TSLA", "META", "UNH",
#     "JNJ", "V", "XOM", "WMT", "JPM", "PG", "MA", "HD", "CVX", "MRK", "ABBV", "PEP",
#     "KO", "LLY", "BAC", "AVGO", "TMO", "COST", "DIS", "PFE", "CSCO", "ACN", "ABT",
#     "DHR", "NFLX", "LIN", "NKE", "MCD", "NEE", "ADBE", "TXN", "PM", "ORCL", "AMD",
#     "HON", "AMGN", "UNP", "MDT", "IBM", "SBUX", "QCOM", "GS", "LOW", "MS", "BLK",
#     "BMY", "CAT", "GE", "RTX", "INTC", "ISRG", "CHTR", "AMT", "GILD", "NOW", "BKNG",
#     "PLD", "PYPL", "SYK", "EL", "ZTS", "SPGI", "TMUS", "ADI", "LRCX", "SCHW", "CB",
#     "REGN", "EQIX", "MU", "MMC", "APD", "FDX", "CL", "MDLZ", "TGT", "CI", "DUK",
#     "ECL", "EW", "FIS", "MAR", "GM", "NSC", "SO", "PNC", "SHW", "TFC", "USB", "ITW",
#     "HUM"
# ]
# company_list = {symbol: 0 for symbol in company_list}

company_list = {
     "AAPL": 0, "MSFT": 0
}
company_data = {}
start_date = "2019-03-24"
end_date = "2023-03-24"

date1 = datetime.strptime(start_date, "%Y-%m-%d")
date2 = datetime.strptime(end_date, "%Y-%m-%d")
# difference = date2 - date1
# difference = difference.days
bull_values = []
data = pd.DataFrame()

for symbol in company_list.keys():
    #print(f"Downloading data for {symbol}...")
    # Download data for the company
    data = yf.download(symbol, start=start_date, end=end_date)
    # Calculate EMA20 and EMA50
    data['ema_short'] = data['Close'].ewm(span=20, adjust=False).mean()
    data['ema_long'] = data['Close'].ewm(span=50, adjust=False).mean()
    data = data.drop(columns=['Volume', 'Open', 'Close', 'High', 'Low'])
    # Calculate the bullish signal
    condition1 = data['ema_short'] > data['ema_long']
    condition2 = data['ema_long'] > data['ema_short']
    data['bullish'] = np.where(condition1, 1.0, 0.0)
    # Store the data in the dictionary
    company_data[symbol] = data

dates_market_open = company_data['AAPL'].index.tolist()

# for symbol in company_list.keys():
#     with pd.option_context('display.max_rows', None):
#         print(symbol)
#         print(company_data[symbol])

for i in dates_market_open:
    for symbol in company_list.keys():
        #print(i)
        bullish = company_data[symbol].loc[i, ['bullish']]
        print(type(bullish))
        bullish = int(bullish.iloc[0])
        current_price = company_data[symbol].loc[i, ['Adj Close']]
        current_price = float(current_price.iloc[0])
        #print(f"For Stock {symbol}: {bullish} and it closed at {current_price}")
        if capital > current_price:
            if bullish == 0 and company_list[symbol] == 0:
                # print(f"Instruction: Sell \nHolding: False")
                # print(f"Capital: {capital}")
                continue
            elif bullish == 1 and company_list[symbol] == 0:
                # print("Instruction: Buy \nHolding: False")
                capital -= current_price
                company_list[symbol] += 1
                # print(f"Capital: {capital}")
            elif bullish == 0 and company_list[symbol] > 0:
                # print("Instruction: Sell \nHolding: True")
                capital += current_price*company_list[symbol]
                company_list[symbol] = 0
                # print(f"Capital: {capital}")
            elif bullish == 1 and company_list[symbol] > 0:
                # print("Instruction: Buy \nHolding: True")
                capital -= current_price
                company_list[symbol] += 1
                # print(f"Capital: {capital}")
                continue
            else:
                # print(f"Capital: {capital}")
                continue
        else:
            continue

total = capital
for symbol in company_list.keys():
    print(f"You own {company_list[symbol]} stock of {symbol}")
    total += company_list[symbol] * float(company_data[symbol].loc[dates_market_open[-1], ['Adj Close']].iloc[0])

print(f"\nRemaining Capital ${capital}")
print(f"Total Portfolio Value: ${total}")
print(f"Profit: ${total-10000}")
print(f"Gain of {int(((total-10000)*100)/10000)}%")
