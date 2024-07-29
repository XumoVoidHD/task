import datetime
import time
import numpy as np
import talib
import pandas as pd
from backtesting import Backtest, Strategy
from multiprocessing import Pool
import os
from backtesting.lib import crossover

class BB_RSI(Strategy):
    rsi_timeperiod = 13
    rsi_over_bought = 70
    rsi_over_sold = 30
    bb_timeperiod = 30

    def __init__(self, broker, data, params):
        super().__init__(broker, data, params)
        self.resistance = None
        self.support = None
        self.rsi_value = None

    def init(self):
        price = self.data.Close
        bb_bands = talib.BBANDS(price, timeperiod=self.bb_timeperiod)
        self.resistance = bb_bands[0]
        self.support = bb_bands[2]
        self.rsi_value = talib.RSI(price, timeperiod=self.rsi_timeperiod)

    def next(self):
        price = self.data.Close[-1]

        if self.rsi_value[-1] < self.rsi_over_bought:
            self.sell()
        elif self.rsi_value[-1] > self.rsi_over_sold:
            self.buy()


        # if self.resistance[-1] < price <= self.resistance[-2] and self.rsi_value[-1] < self.rsi_over_bought < self.rsi_value[-2]:
        #     self.sell()
        # elif self.support[-1] > price >= self.support[-2] and self.rsi_value[-1] > self.rsi_over_sold >= self.rsi_value[-2]:
        #     self.buy()


def run_backtest(filename, data):

    data = pd.read_csv(f"{data}/{filename}")
    data = data.rename(columns={'timestamp': 'OpenTime', 'open': 'Open', "high": "High", 'low': 'Low', 'close': 'Close', 'volume': 'Volume'})
    data['OpenTime'] = pd.to_timedelta(data['OpenTime'], unit='ms')
    data.set_index("OpenTime", inplace=True)
    sym = filename.split("_")[0]

    backtest = Backtest(data, BB_RSI, commission=0.002, exclusive_orders=True, cash=1000000)
    stats = backtest.run()
    print(stats)
    backtest.plot()



if __name__ == "__main__":
    start_time = time.time()
    data = "data_1day"

    # with Pool() as p:
    #     p.map(run_backtest, os.listdir("data_15min"))

    for i in os.listdir(data):
        run_backtest(i, data)

    end_time = time.time()
    print(f"Time taken is {end_time - start_time} seconds with multi-threading")

