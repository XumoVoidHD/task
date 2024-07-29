import datetime
import time
import numpy as np
import talib
import pandas as pd
from backtesting import Backtest, Strategy
from multiprocessing import Pool
import os
from backtesting.lib import crossover


class StochRSI_Strategy(Strategy):
    fastk_period = 3
    fastd_period = 3
    rsi_timeperiod = 14
    stochrsi_timeperiod = 14
    def init(self):
        close = self.data.Close
        self.rsi = self.I(talib.RSI, close, timeperiod=self.rsi_timeperiod)
        self.stochrsi = self.I(talib.STOCHRSI, self.rsi, timeperiod=self.stochrsi_timeperiod, fastk_period=self.fastk_period, fastd_period=self.fastd_period)

    def next(self):
        # Check if the Stochastic RSI crosses above 0.2 (buy signal) and crosses below 0.8 (sell signal)
        if crossover(self.stochrsi, 0.2):
            self.buy()
        elif crossover(0.8, self.stochrsi):
            self.sell()


def run_backtest(filename, data):

    data = pd.read_csv(f"{data}/{filename}")
    data = data.rename(columns={'timestamp': 'OpenTime', 'open': 'Open', "high": "High", 'low': 'Low', 'close': 'Close', 'volume': 'Volume'})
    data['OpenTime'] = pd.to_datetime(data['OpenTime'], unit='ms')
    data.set_index("OpenTime", inplace=True)
    sym = filename.split("_")[0]

    bt = Backtest(data, StochRSI_Strategy, commission=0.002, exclusive_orders=True, cash=1000000)
    stats = bt.optimize(
    fastk_period=range(3, 15, 1),
    fastd_period=range(3, 15, 1),
    rsi_timeperiod=range(10, 20, 1),
    stochrsi_timeperiod=range(10, 20, 1),
    maximize='Equity Final [$]'
)
    print(stats)
    bt.plot()


if __name__ == "__main__":
    start_time = time.time()
    data = "data_1day"

    # with Pool() as p:
    #     p.map(run_backtest, os.listdir("data_15min"))

    for i in os.listdir(data):
        run_backtest(i, data)

    end_time = time.time()
    print(f"Time taken is {end_time - start_time} seconds with multi-threading")