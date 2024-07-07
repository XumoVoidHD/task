import datetime
import time
import talib
import pandas as pd
from backtesting import Backtest, Strategy
from backtesting.lib import resample_apply
from multiprocessing import Pool
import os
from backtesting.lib import crossover
import pickle

class MACD_Strategy(Strategy):

    EMA_timeperiod = 100
    fastperiod = 12
    slowperiod = 26
    signal_period = 9

    def __init__(self, broker, data, params):
        super().__init__(broker, data, params)
        self.macd_hist = None
        self.macd_signal = None
        self.macd = None
        self.ma = None
        self.atr = None
        self.length = None

    def init(self):
        prices = self.data['Close']
        self.length = len(prices)
        self.ma = talib.EMA(prices, timeperiod=self.EMA_timeperiod)
        self.macd = self.I(lambda x: talib.MACD(x, fastperiod=self.fastperiod, slowperiod=self.slowperiod, signalperiod=self.signal_period)[0], prices)
        self.macd_signal = self.I(lambda x: talib.MACD(x, fastperiod=self.fastperiod, slowperiod=self.slowperiod, signalperiod=self.signal_period)[1], prices)
        self.macd_hist = self.I(lambda x: talib.MACD(x, fastperiod=self.fastperiod, slowperiod=self.slowperiod, signalperiod=self.signal_period)[2], prices)
        self.atr = self.I(talib.ATR, self.data.High, self.data.Low, self.data.Close, timeperiod=14)

    def next(self):
        price = self.data['Close']
        atr_value = self.atr[-1]
        take_profit = price + 3 * atr_value
        stop_loss = price - 1.5 * atr_value

        if crossover(self.macd, self.macd_signal) and self.macd[-1] < 0 and self.macd_signal[-1] < 0 and self.ma[-1] > price:
            self.buy()

        if crossover(self.macd_signal, self.macd) and self.macd[-1] > 0 and self.macd_signal[-1] > 0 and self.ma[-1] < price:
            self.sell()


# def walk_forward(strategy, filename, warmup_bars, lookback_bars, validation_bars, cash=100000, commission=0.002):
def walk_forward(filename):

    stat_master = []

    data = pd.read_csv(f"data/{filename}")
    data = data.rename(columns={'timestamp': 'OpenTime','open': 'Open', "high": "High", 'low': 'Low', 'close': 'Close', 'volume': 'Volume'})
    data['OpenTime'] = pd.to_datetime(data['OpenTime'], unit='ms')
    data.set_index("OpenTime", inplace=True)

    start_date = data.index[0]
    end_date = start_date + pd.DateOffset(months=4) - pd.Timedelta(days=1)

    df_4_months = data.loc[start_date:end_date]
    stat_master.append(run_backtest(df_4_months, MACD_Strategy))


    while pd.Timestamp(end_date) <= datetime.datetime(2024,6,10, 0, 0,0):
        start_date = end_date
        end_date = start_date + pd.DateOffset(months=4) - pd.Timedelta(days=1)
        df_4_months = data.loc[start_date:end_date]
        stat_master.append(run_backtest(df_4_months, MACD_Strategy))

    print(stat_master)

def run_backtest(df, strategy, cash=10000, commission=0.002):
    stat_instance = {}

    start_date = df.index.min()
    end_date = df.index.max()

    end_3_month_date = start_date + pd.DateOffset(months=3) - pd.DateOffset(days=1)
    start_1_month_date = end_date - pd.DateOffset(months=1) + pd.DateOffset(days=1)

    training_data = df.loc[start_date:end_3_month_date]
    validation_data = df.loc[start_1_month_date:end_date]

    bt_training = Backtest(training_data, strategy, cash=cash, commission=commission)
    stats_training = bt_training.optimize(EMA_timeperiod=range(50,130, 10), fastperiod=range(4,20, 4), slowperiod=range(20,32, 4), signal_period = range(3,15,3), maximize="Return [%]")
    optimized_params = stats_training['_strategy']

    EMA_timeperiod = optimized_params.EMA_timeperiod
    fastperiod = optimized_params.fastperiod
    slowperiod = optimized_params.slowperiod
    signal_period = optimized_params.signal_period

    bt_validation = Backtest(validation_data, strategy, cash=cash, commission=commission)
    stats_validation = bt_validation.run(EMA_timeperiod=EMA_timeperiod, fastperiod=fastperiod, slowperiod=slowperiod, signal_period=signal_period)

    stat_instance[f"{start_date}"] = {
        "EMA_timeperiod": int(EMA_timeperiod),
        "fastperiod": int(optimized_params.fastperiod),
        "slowperiod": int(optimized_params.slowperiod),
        "signal_period": int(signal_period)
    }

    print(stats_training)
    print(stats_validation)

    return stat_instance



    # for i in range(lookback_bars + warmup_bars, len(data)- validation_bars, validation_bars):
    #     training_data = data.iloc[i-lookback_bars-warmup_bars:i]
    #     validation_data = data.iloc[i-warmup_bars:i+validation_bars]
    #
    #     bt_training = Backtest(training_data, strategy, cash=cash, commission=commission)
    #     stats_training = bt_training.optimize(EMA_timeperiod=range(50,130, 10), fastperiod=range(4,20, 4), slowperiod=range(20,32, 4), signal_period = range(3,15,3), maximize="Return [%]")
    #
    #     EMA_timeperiod = stats_training._EMA_timeperiod
    #     fastperiod = stats_training.fastperiod
    #     slowperiod = stats_master.slowperiod
    #     signal_period = stats_master.signal_period
    #
    #     bt_validation = Backtest(validation_data, strategy, cash=cash, commission=commission)
    #     stats_validation = bt_validation.run(EMA_timeperiod=EMA_timeperiod, fastperiod=fastperiod, slowperiod=slowperiod, signal_period=signal_period)
    #
    #     stats_master.append(stats_validation)
    #
    # print(stats_master)
    # return stats_master


if __name__ == "__main__":
    start_time = time.time()
    with Pool() as p:
        p.map(walk_forward,os.listdir("data"))
    end_time = time.time()


    print(f"Time taken is {end_time - start_time} seconds with multi-threading")

