import datetime
import time
import numpy as np
import talib
import pandas as pd
from backtesting import Backtest, Strategy
from multiprocessing import Pool
import os
from backtesting.lib import crossover

class STOCH_SMA(Strategy):
    def __init__(self, broker, data, params):
        super().__init__(broker, data, params)
        self.slowk = None
        self.slowd = None
        self.sma = None

    def init(self):
        close = self.data.Close
        high = self.data.High
        low = self.data.Low

        stoch = talib.STOCH(high, low, close, fastk_period=10)
        self.slowk = stoch[0]
        print(self.slowk)
        self.sma = talib.SMA(close, timeperiod=200)


    def next(self):
        price = self.data.Close[-1]

        if crossover(self.data.Close, self.sma) and self.slowk[-1] < 20:
            self.buy()
        elif crossover(self.sma, self.data.Close) and self.slowk[-1] > 80:
            self.sell()



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

    backtest = Backtest(data, STOCH_SMA, commission=0.002, exclusive_orders=True, cash=1000000)
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




