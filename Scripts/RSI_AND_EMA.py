import yfinance as yf
import pandas as pd
import datetime
from openpyxl.workbook import Workbook
import talib

company_list = [
    "AAPL", "MSFT", "AMZN", "GOOGL", "GOOG", "NVDA", "TSLA", "META", "UNH",
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

company_data = {}

# Time Interval
time = 3000
start_date = datetime.date.today()-datetime.timedelta(days=time)
end_date = datetime.date.today()

# Theresholds
rsi_buy_threshold = 30
rsi_sell_threshold = 70
ema_short = 20
ema_long = 50

#Downloading Data
for symbol in company_list.keys():
    data = yf.download(symbol, start=start_date, end=end_date)
    data = data.reset_index()
    company_data[symbol] = data

# Number of data points
length = len(company_data['AAPL'])

# Calculating EMA
for symbol in company_list.keys():
    company_data[symbol]['ema20'] = [0.0] * length
    company_data[symbol]['ema50'] = [0.0] * length
    company_data[symbol]['bullish'] = [0] * length

    for i in range(ema_short, length):
        values20 = company_data[symbol].loc[range(i-ema_short, i+1), 'Close'].mean()
        company_data[symbol].loc[i, 'ema20'] = float(values20)

    for i in range(ema_long, length):
        values50 = company_data[symbol].loc[range(i - ema_long, i), 'Close'].mean()
        company_data[symbol].loc[i, 'ema50'] = float(values50)
        if company_data[symbol].loc[i, 'ema20'] > company_data[symbol].loc[i, 'ema50']:
            company_data[symbol].loc[i, 'bullish'] = 1
        else:
            company_data[symbol].loc[i, 'bullish'] = -1

# Calculating RSI
for symbol in company_list.keys():
    company_data[symbol]['Upward Movement'] = [0.0] * length
    company_data[symbol]['Signal'] = [0] * length
    company_data[symbol]['Downward Movement'] = [0.0] * length
    company_data[symbol]['Average Upward Movement'] = [0.0] * length
    company_data[symbol]['Average Downward Movement'] = [0.0] * length
    company_data[symbol]['Relative Strength'] = [0.0] * length
    company_data[symbol]['RSI'] = [0.0] * length

    for i in range(1, length):
        pre = float(company_data[symbol].at[i-1, 'Close'])
        post = float(company_data[symbol].at[i, 'Close'])
        if post > pre:
            company_data[symbol].at[i, 'Upward Movement'] = post - pre
        elif pre >= post:
            company_data[symbol].at[i, 'Downward Movement'] = pre-post

    period = 14
    company_data[symbol].at[period, 'Average Upward Movement'] = company_data[symbol].loc[range(0, period+1), 'Upward Movement'].mean()
    company_data[symbol].at[period, 'Average Downward Movement'] = company_data[symbol].loc[range(0, period+1), 'Downward Movement'].mean()
    company_data[symbol].at[period, 'Relative Strength'] = company_data[symbol].at[period, 'Average Upward Movement']/company_data[symbol].at[period, 'Average Downward Movement']
    company_data[symbol].at[period, 'RSI'] = 100 - (100 / (company_data[symbol].at[period, 'Relative Strength'] + 1))

    for i in range(period+1, length):
        company_data[symbol].at[i, 'Average Upward Movement'] = (company_data[symbol].at[i-1, 'Average Upward Movement']*(period-1) + company_data[symbol].at[i, 'Upward Movement'])/period
        company_data[symbol].at[i, 'Average Downward Movement'] = (company_data[symbol].at[i-1, 'Average Downward Movement'] * (period - 1) + company_data[symbol].at[i, 'Downward Movement'])/period
        company_data[symbol].at[i, 'Relative Strength'] = company_data[symbol].at[i, 'Average Upward Movement']/company_data[symbol].at[i, 'Average Downward Movement']
        company_data[symbol].at[i, 'RSI'] = 100-(100/(company_data[symbol].at[i, 'Relative Strength']+1))

# with pd.option_context('display.max_rows', None, 'display.max_columns', None):
#     print(company_data['AAPL'])

both_total_capital = 0
rsi_total_capital = 0
ema_total_capital = 0
buy_weight = 10

for symbol in company_list.keys():

    # To find revenue if we used both RSI and EMA
    capital = 10000
    print(f"Stock: {symbol}")
    for i in range(0, length):
        if capital > 0:
            if company_data[symbol].at[i, 'RSI'] <= rsi_buy_threshold or company_data[symbol].at[i, 'bullish'] == 1:
                company_data[symbol].at[i, 'Signal'] = 1
                capital -= company_data[symbol].at[i, 'Close'] * buy_weight
                company_list[symbol] += buy_weight
            elif company_data[symbol].at[i, 'RSI'] >= rsi_sell_threshold or company_data[symbol].at[i, 'bullish'] == -1:
                company_data[symbol].at[i, 'Signal'] = -1
                capital += company_data[symbol].at[i, 'Close'] * company_list[symbol]
                company_list[symbol] = 0
    both_total_capital += capital + company_list[symbol]*company_data[symbol].at[206, 'Close']
    print(f"Both:  {capital + company_list[symbol]*company_data[symbol].at[206, 'Close']}")

    # To find revenue if we just used RSI
    capital = 10000
    company_list = {symbol: 0 for symbol in company_list}
    for i in range(0, length):
        if capital > 0:
            if company_data[symbol].at[i, 'RSI'] <= rsi_buy_threshold:

                capital -= company_data[symbol].at[i, 'Close'] * buy_weight
                company_list[symbol] += buy_weight
            elif company_data[symbol].at[i, 'RSI'] >= rsi_sell_threshold:
                capital += company_data[symbol].at[i, 'Close'] * company_list[symbol]
                company_list[symbol] = 0
    rsi_total_capital += capital + company_list[symbol] * company_data[symbol].at[206, 'Close']
    print(f"RSI:  {capital + company_list[symbol]*company_data[symbol].at[206, 'Close']}")


    # To find revenue if we just used EMA
    capital = 10000
    company_list = {symbol: 0 for symbol in company_list}
    for i in range(ema_long, length):
        if capital > 0:
            if company_data[symbol].at[i, 'bullish'] == 1:
                capital -= company_data[symbol].at[i, 'Close'] * buy_weight
                company_list[symbol] += buy_weight
            elif company_data[symbol].at[i, 'bullish'] == -1:
                capital += company_data[symbol].at[i, 'Close'] * company_list[symbol]
                company_list[symbol] = 0
    ema_total_capital += capital + company_list[symbol] * company_data[symbol].at[206, 'Close']
    print(f"EMA:  {capital + company_list[symbol]*company_data[symbol].at[206, 'Close']}\n")


print(f"Initial Capital: $1,000,000")
print(f"Both Indicators: ${both_total_capital}")
print(f"RSI Indicator: ${rsi_total_capital}")
print(f"EMA Indicator: ${ema_total_capital}")


# with pd.ExcelWriter('output.xlsx') as writer:
#     for symbol in company_list.keys():
#         company_data[symbol].to_excel(writer, sheet_name=symbol)
