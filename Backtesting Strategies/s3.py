import pandas as pd
import numpy as np
import yfinance as yf
import talib
from backtesting import Backtest, Strategy
import datetime

startdate = datetime.datetime(2024, 5, 26)
enddate = datetime.datetime(2024, 7, 23)
stocks = ['tcs.ns']


def Fetchdata(stock):
    data = yf.download(stock)
    data.drop('Adj Close', axis=1, inplace=True)
    return data


class SIDEMOMENTUM(Strategy):
    atr_var = 15
    multiplier1 = 100
    multiplier2 = 200
    dema_var = 50

    def init(self):
        self.dema50 = self.I(talib.DEMA, self.data.Close, timeperiod=self.dema_var)
        self.prev_26close = self.data.Close[-26]
        self.ema12 = self.I(talib.EMA, self.data.Close, timeperiod=12)
        self.ema26 = self.I(talib.EMA, self.data.Close, timeperiod=26)

        # Ichimoku Cloud indicators
        self.tenkan_sen = self.I(talib.MIN, self.data.High, timeperiod=9) + self.I(talib.MAX, self.data.Low,
                                                                                   timeperiod=9) / 2
        self.kijun_sen = self.I(talib.MIN, self.data.High, timeperiod=26) + self.I(talib.MAX, self.data.Low,
                                                                                   timeperiod=26) / 2
        self.senkou_span_a = (self.tenkan_sen + self.kijun_sen) / 2
        self.senkou_span_b = self.I(talib.MIN, self.data.High, timeperiod=52) + self.I(talib.MAX, self.data.Low,
                                                                                       timeperiod=52) / 2
        self.chikou_span = self.data.Close[-26]

        # Average True Range (ATR)
        self.atr = self.I(talib.ATR, self.data.High, self.data.Low, self.data.Close, timeperiod=self.atr_var)

    def next(self):
        # Check if close price is above DEMA50 and Ichimoku cloud (Senkou Span A and B)
        if self.dema50[-1] < self.data.Close[-1] and self.data.Close[-1] > max(self.senkou_span_a[-1],
                                                                               self.senkou_span_b[-1]):
            self.position.close()
            self.buy(sl=self.data.Close[-1] - self.atr[-1] * (self.multiplier2 / 100),
                     tp=self.data.Close[-1] + self.atr[-1] * (self.multiplier1 / 100))

        # Check if close price is below DEMA50 and Ichimoku cloud (Senkou Span A and B)
        elif self.dema50[-1] > self.data.Close[-1] and self.data.Close[-1] < min(self.senkou_span_a[-1],
                                                                                 self.senkou_span_b[-1]):
            self.position.close()
            self.sell(tp=self.data.Close[-1] - self.atr[-1] * (self.multiplier2 / 100),
                      sl=self.data.Close[-1] + self.atr[-1] * (self.multiplier1 / 100))


def walk_forward(strategy, data_full, warmup_bars, lookback_bars, validation_bars, cash=10000, commission=0):
    stats_master = []
    for i in range(lookback_bars + warmup_bars, len(data_full) - validation_bars, validation_bars):
        training_data = data_full.iloc[i - lookback_bars:i]
        validation_data = data_full.iloc[i:i + validation_bars]
        bt_training = Backtest(training_data, strategy, cash=cash, commission=commission)
        stats_training = bt_training.optimize(
            multiplier1=range(100, 300, 100),
            multiplier2=range(100, 300, 100),
            atr_var=range(7, 21, 7),
            dema_var=range(40, 60, 10),
            maximize='Return [%]'
        )
        opt_mul1 = stats_training._strategy.multiplier1
        opt_mul2 = stats_training._strategy.multiplier2
        opt_atr = stats_training._strategy.atr_var
        opt_dema = stats_training._strategy.dema_var

        bt_validation = Backtest(validation_data, strategy, cash=cash, commission=commission)
        stats_validation = bt_validation.run(
            multiplier1=opt_mul1, multiplier2=opt_mul2, atr_var=opt_atr, dema_var=opt_dema
        )

        stats_master.append(stats_validation)
        var1 = pd.DataFrame(stats_master)
        var1.to_excel("japen.xlsx")
    return stats_master


# Adjust the lookback_bars, validation_bars, and warmup_bars as per your needs
lookback_bars = 300  # 300 bars for training (lookback)
validation_bars = 100  # 120 bars for validation
warmup_bars = 80  # 80 bars for warmup

# Fetch the dataa for each stock and perform walk-forward analysis
for stock in stocks:
    data = Fetchdata(stock)
    stats = walk_forward(SIDEMOMENTUM, data, warmup_bars, lookback_bars, validation_bars)
    # Optionally, you can print or analyze the stats further
    for stat in stats:
        print(stat)
