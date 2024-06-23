import talib
import pandas as pd
import yfinance as yf
from backtesting import Backtest, Strategy
from backtesting.lib import crossover
from backtesting.test import SMA, GOOG

rsi_sell_threshold = 70
rsi_buy_threshold = 30


class BB_Strategy(Strategy):

    def __init__(self, broker, data, params):
        super().__init__(broker, data, params)
        self.upper_band = None
        self.middle_band = None
        self.lower_band = None
        self.RSI = None
        self.atr = None

    def init(self):
        price = self.data.Close
        self.upper_band = self.I(lambda x: talib.BBANDS(x)[0], price)
        self.middle_band = self.I(lambda x: talib.BBANDS(x)[1], price)
        self.lower_band = self.I(lambda x: talib.BBANDS(x)[2], price)
        self.RSI = self.I(talib.RSI, price, 13)
        self.atr = self.I(talib.ATR, self.data.High, self.data.Low, self.data.Close, timeperiod=14)

    def next(self):
        price = self.data.Close
        atr_value = self.atr[-1]
        take_profit = price + 3 * atr_value
        stop_loss = price - 1.5 * atr_value

        if self.position:
            if self.data.High[-1] > self.upper_band[-1] and self.RSI[-1] >= rsi_sell_threshold:
                self.position.close()
                # self.sell()
        else:
            if self.data.Low[-1] < self.lower_band[-1] and self.RSI[-1] <= rsi_buy_threshold:
                self.buy(tp= take_profit, sl= stop_loss)


results = {}

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

for symbol in company_list:

    data = yf.download(tickers= symbol, start="2020-01-01",end="2024-04-04" )
    backtest = Backtest(data, BB_Strategy, commission=0.002, exclusive_orders=True)
    stats = backtest.run()
    results[symbol] = stats
    print(stats)
    #backtest.plot()


class rsi_ema_strategy(Strategy):

    def init(self):
        price = self.data.Close
        self.rsi = self.I(talib.RSI, price)
        self.ma1 = self.I(SMA, price, 20)
        self.ma2 = self.I(SMA, price, 50)
        self.atr = self.I(talib.ATR, data.High, data.Low, data.Close, timeperiod=14)

    def next(self):
        price = self.data.Close[-1]
        atr_value = self.atr[-1]

        take_profit = price + 3 * atr_value
        stop_loss = price - 1.5 * atr_value
        if crossover(30, self.rsi) or crossover(self.ma1, self.ma2):
            self.buy(tp=take_profit, sl=stop_loss)
        elif crossover(self.rsi, 70) or crossover(self.ma2, self.ma1):
            self.position.close()


# data = yf.download("AAPL", "2022-01-01","2024-04-04" )
# backtest = Backtest(data, rsi_ema_strategy, commission=0.002, exclusive_orders=True)
# stats = backtest.run()
# print(stats)
# backtest.plot()

class MyMACDStrategy(Strategy):

    def init(self):
        price = self.data.Close
        self.macd = self.I(lambda x: talib.MACD(x)[0], price)
        self.macd_signal = self.I(lambda x: talib.MACD(x)[1], price)
        print(self.macd_signal)

    def next(self):
        if crossover(self.macd, self.macd_signal):
            self.buy()
        elif crossover(self.macd_signal, self.macd):
            self.sell()


# data = yf.download("AAPL", "2020-04-04","2024-04-04" )
# backtest = Backtest(data, MyMACDStrategy, commission=0.002, exclusive_orders=True)
# stats = backtest.run()
# print(stats)


class MySMAStrategy(Strategy):

    def init(self):
        price = self.data.Close
        self.ma1 = self.I(SMA, price, 10)
        self.ma2 = self.I(SMA, price, 20)

    def next(self):
        if crossover(self.ma1, self.ma2):
            self.buy()
        elif crossover(self.ma2, self.ma1):
            self.sell()

#
# backtest = Backtest(GOOG, MySMAStrategy, commission=0.002, exclusive_orders=True)
# stats = backtest.run()
# print(stats)
