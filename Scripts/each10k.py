import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime


total = 0
capital_left = 0

company_list = [
     "AAPL"#, "MSFT", "AMZN", "GOOGL", "GOOG", "NVDA", "TSLA", "META", "UNH",
    # "JNJ", "V", "XOM", "WMT", "JPM", "PG", "MA", "HD", "CVX", "MRK", "ABBV", "PEP",
    # "KO", "LLY", "BAC", "AVGO", "TMO", "COST", "DIS", "PFE", "CSCO", "ACN", "ABT",
    # "DHR", "NFLX", "LIN", "NKE", "MCD", "NEE", "ADBE", "TXN", "PM", "ORCL", "AMD",
    # "HON", "AMGN", "UNP", "MDT", "IBM", "SBUX", "QCOM", "GS", "LOW", "MS", "BLK",
    # "BMY", "CAT", "GE", "RTX", "INTC", "ISRG", "CHTR", "AMT", "GILD", "NOW", "BKNG",
    # "PLD", "PYPL", "SYK", "EL", "ZTS", "SPGI", "TMUS", "ADI", "LRCX", "SCHW", "CB",
    # "REGN", "EQIX", "MU", "MMC", "APD", "FDX", "CL", "MDLZ", "TGT", "CI", "DUK",
    # "ECL", "EW", "FIS", "MAR", "GM", "NSC", "SO", "PNC", "SHW", "TFC", "USB", "ITW",
    # "HUM"
]
company_list = {symbol: 0 for symbol in company_list}

# company_list = {
#      "AAPL": 0, "MSFT": 0
# }
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
    #print(f"Downloading dataa for {symbol}...")
    # Download dataa for the company
    data = yf.download(symbol, start=start_date, end=end_date)
    # Calculate EMA20 and EMA50
    data['ema_short'] = data['Close'].ewm(span=20, adjust=False).mean()
    data['ema_long'] = data['Close'].ewm(span=50, adjust=False).mean()
    data = data.drop(columns=['Volume', 'Open', 'Close', 'High', 'Low'])
    # Calculate the bullish signal
    condition1 = data['ema_short'] > data['ema_long']
    condition2 = data['ema_long'] > data['ema_short']
    data['bullish'] = np.where(condition1, 1.0, 0.0)
    # Store the dataa in the dictionary
    company_data[symbol] = data

dates_market_open = company_data['AAPL'].index.tolist()

# for symbol in company_list.keys():
#     with pd.option_context('display.max_rows', None):
#         print(symbol)
#         print(company_data[symbol])

for symbol in company_list.keys():
    capital = 10000
    print(f"Current for {symbol}")
    for i in dates_market_open:
        #print(i)
        bullish = company_data[symbol].loc[i, ['bullish']]
        bullish = int(bullish.iloc[0])
        current_price = company_data[symbol].loc[i, ['Adj Close']]
        current_price = float(current_price.iloc[0])
        #print(f"You have {company_list[symbol]} stocks of {symbol} on {i}")
        if capital > current_price:
            if bullish == 0 and company_list[symbol] == 0:
                # print("hit1")
                # print(f"Instruction: Sell \nHolding: False")
                # print(f"Capital: {capital}\n")
                continue
            elif bullish == 1 and company_list[symbol] == 0:
                # print("hit2")
                # print("Instruction: Buy \nHolding: False")
                capital -= current_price
                # print(f"Price {current_price}")
                company_list[symbol] += 1
                # print(f"Capital: {capital}\n")
            elif bullish == 0 and company_list[symbol] > 0:
                # print("hit3")
                # print("Instruction: Sell \nHolding: True")
                capital += current_price*company_list[symbol]
                # print(f"Price {current_price*company_list[symbol]}")
                company_list[symbol] = 0
                # print(f"Capital: {capital}\n")
            elif bullish == 1 and company_list[symbol] > 0:
                # print("hit4")
                # print("Instruction: Buy \nHolding: True")
                capital -= current_price
                company_list[symbol] += 1
                # print(f"Capital: {capital}\n")
                continue
            else:
                # print(f"Capital: {capital}\n")
                continue
        else:
            continue

    capital_left += capital
    total += capital + company_list[symbol] * current_price

for symbol in company_list.keys():
    print(f"You own {company_list[symbol]} stock of {symbol}")
    total += company_list[symbol] * float(company_data[symbol].loc[dates_market_open[-1], ['Adj Close']].iloc[0])
print(f"\nRemaining Capital ${capital_left}")
print(f"Total Portfolio Value: ${total}")
print("Initial capital $1000000")
print(f"Profit ${total-1000000}")
print(f"Gain of {int(((total-1000000)*100)/1000000)}%")

company_list['AAPL'].to_excel('new5.xlsx')