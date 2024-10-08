import datetime
import time
import numpy as np
import talib
import pandas as pd
from backtesting import Backtest, Strategy
from multiprocessing import Pool
import os
from backtesting.lib import crossover

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
            self.buy(tp=take_profit)

        if crossover(self.macd_signal, self.macd) and self.macd[-1] > 0 and self.macd_signal[-1] > 0 and self.ma[-1] < price:
            self.sell()


# def walk_forward(strategy, filename, warmup_bars, lookback_bars, validation_bars, cash=100000, commission=0.002):
def walk_forward(filename):

    stat_master = []

    data = pd.read_csv(f"data/{filename}")
    data = data.rename(columns={'timestamp': 'OpenTime','open': 'Open', "high": "High", 'low': 'Low', 'close': 'Close', 'volume': 'Volume'})
    data['OpenTime'] = pd.to_datetime(data['OpenTime'], unit='ms')
    data.set_index("OpenTime", inplace=True)
    sym = filename.split("_")[0]
    print(sym)
    start_date = data.index[0]
    end_date = start_date + pd.DateOffset(months=8) - pd.Timedelta(days=1)

    df_4_months = data.loc[start_date:end_date]
    stat_master.append(run_backtest(df_4_months, MACD_Strategy))


    while pd.Timestamp(end_date) <= datetime.datetime(2024,6,10, 0, 0,0):
        start_date = start_date + pd.DateOffset(months=1)
        end_date = start_date + pd.DateOffset(months=8) - pd.Timedelta(days=1)
        df_4_months = data.loc[start_date:end_date]
        stat_master.append(run_backtest(df_4_months, MACD_Strategy))


    return {sym: stat_master}


def run_backtest(df, strategy, cash=10000, commission=0.002):

    def custom_constraint_function(params):
        bt = Backtest(training_data, MACD_Strategy, cash=10_000, commission=.002)
        stats = bt.run(**params)
        num_trades = stats['# Trades']
        min_trades = 2
        return num_trades >= min_trades

    stat_instance = {}

    start_date = df.index.min()
    end_date = df.index[-1]
    end_3_month_date = start_date + pd.DateOffset(months=3)
    start_1_month_date = end_date - pd.DateOffset(months=1)

    print(f"Pre: {end_3_month_date}")
    while end_3_month_date not in df.index and pd.Timestamp(end_3_month_date) <= datetime.datetime(2024, 6, 10, 0, 0, 0):
        print("hit3")
        end_3_month_date -= pd.Timedelta(hours=1)
    print(f"Post: {end_3_month_date}")

    print(f"Pre: {start_1_month_date}")
    while start_1_month_date not in df.index and pd.Timestamp(start_1_month_date) <= datetime.datetime(2024, 6, 10, 0, 0, 0):
        print("hit4")
        start_1_month_date += pd.Timedelta(hours=1)
    print(f"Post: {start_1_month_date}")

    training_data = df.loc[start_date:end_3_month_date]
    validation_data = df.loc[start_1_month_date:end_date]

    bt_training = Backtest(training_data, strategy, cash=cash, commission=commission)
    stats_validation = bt_training.optimize(EMA_timeperiod=range(5,30, 10), fastperiod=range(2,22, 8),
                                            slowperiod=range(10,32, 8), signal_period=range(1,16,6),
                                            maximize=lambda stats: stats['Return [%]'],)
                                            #constraint=lambda params: custom_constraint_function(params))
    optimized_params = stats_validation['_strategy']

    EMA_timeperiod = optimized_params.EMA_timeperiod
    fastperiod = optimized_params.fastperiod
    slowperiod = optimized_params.slowperiod
    signal_period = optimized_params.signal_period

    stat_instance[f"{start_date}"] = {
        "Start (Training)": str(stats_validation['Start']),
        "End (Training)": str(stats_validation['End']),
        "Start (Testing)": np.nan,
        "End (Testing)": np.nan,
        "Duration": str(stats_validation['Duration']),
        "Exposure Time [%]": stats_validation['Exposure Time [%]'],
        'Equity Final [$]': stats_validation['Equity Final [$]'],
        'Equity Peak [$]': stats_validation['Equity Peak [$]'],
        'Return [%]': stats_validation['Return [%]'],
        'Buy & Hold Return [%]': stats_validation['Buy & Hold Return [%]'],
        'Return (Ann.) [%]': stats_validation['Return (Ann.) [%]'],
        'Return (Ann.) [%]': stats_validation['Return (Ann.) [%]'],
        'Sharpe Ratio': stats_validation['Sharpe Ratio'],
        'Sortino Ratio': stats_validation['Sortino Ratio'],
        'Calmar Ratio': stats_validation['Calmar Ratio'],
        'Max. Drawdown [%]': stats_validation['Max. Drawdown [%]'],
        'Avg. Drawdown [%]': stats_validation['Avg. Drawdown [%]'],
        'Max. Drawdown Duration': stats_validation['Max. Drawdown Duration'],
        'Max. Drawdown Duration': str(stats_validation['Max. Drawdown Duration']),
        '# Trades': stats_validation['# Trades'],
        'Win Rate [%]': stats_validation['Win Rate [%]'],
        'Best Trade [%]': stats_validation['Best Trade [%]'],
        'Worst Trade [%]': stats_validation['Worst Trade [%]'],
        'Avg. Trade [%]': stats_validation['Avg. Trade [%]'],
        'Max. Trade Duration': str(stats_validation['Max. Trade Duration']),
        'Avg. Trade Duration': str(stats_validation['Avg. Trade Duration']),
        'Profit Factor': str(stats_validation['Profit Factor']),
        'Expectancy [%]': str(stats_validation['Expectancy [%]']),
        'SQN': str(stats_validation['SQN']),
        "EMA_timeperiod": int(EMA_timeperiod),
        "fastperiod": int(optimized_params.fastperiod),
        "slowperiod": int(optimized_params.slowperiod),
        "signal_period": int(signal_period)
    }

    bt_validation = Backtest(validation_data, strategy, cash=cash, commission=commission)
    stats_validation = bt_validation.run(EMA_timeperiod=EMA_timeperiod, fastperiod=fastperiod, slowperiod=slowperiod, signal_period=signal_period)

    stat_instance[f"{start_1_month_date}"] = {
        "Start (Training)": np.nan,
        "End (Training)": np.nan,
        "Start (Testing)": str(stats_validation['Start']),
        "End (Testing)": str(stats_validation['End']),
        "Duration": str(stats_validation['Duration']),
        "Exposure Time [%]": stats_validation['Exposure Time [%]'],
        'Equity Final [$]': stats_validation['Equity Final [$]'],
        'Equity Peak [$]': stats_validation['Equity Peak [$]'],
        'Return [%]': stats_validation['Return [%]'],
        'Buy & Hold Return [%]': stats_validation['Buy & Hold Return [%]'],
        'Return (Ann.) [%]': stats_validation['Return (Ann.) [%]'],
        'Return (Ann.) [%]': stats_validation['Return (Ann.) [%]'],
        'Sharpe Ratio': stats_validation['Sharpe Ratio'],
        'Sortino Ratio': stats_validation['Sortino Ratio'],
        'Calmar Ratio': stats_validation['Calmar Ratio'],
        'Max. Drawdown [%]': stats_validation['Max. Drawdown [%]'],
        'Avg. Drawdown [%]': stats_validation['Avg. Drawdown [%]'],
        'Max. Drawdown Duration': stats_validation['Max. Drawdown Duration'],
        'Max. Drawdown Duration': str(stats_validation['Max. Drawdown Duration']),
        '# Trades': stats_validation['# Trades'],
        'Win Rate [%]': stats_validation['Win Rate [%]'],
        'Best Trade [%]': stats_validation['Best Trade [%]'],
        'Worst Trade [%]': stats_validation['Worst Trade [%]'],
        'Avg. Trade [%]': stats_validation['Avg. Trade [%]'],
        'Max. Trade Duration': str(stats_validation['Max. Trade Duration']),
        'Avg. Trade Duration': str(stats_validation['Avg. Trade Duration']),
        'Profit Factor': str(stats_validation['Profit Factor']),
        'Expectancy [%]': str(stats_validation['Expectancy [%]']),
        'SQN': str(stats_validation['SQN']),
        "EMA_timeperiod": int(EMA_timeperiod),
        "fastperiod": int(optimized_params.fastperiod),
        "slowperiod": int(optimized_params.slowperiod),
        "signal_period": int(signal_period)
    }

    return stat_instance



    # for i in range(lookback_bars + warmup_bars, len(dataa)- validation_bars, validation_bars):
    #     training_data = dataa.iloc[i-lookback_bars-warmup_bars:i]
    #     validation_data = dataa.iloc[i-warmup_bars:i+validation_bars]
    #
    #     bt_training = Backtest(training_data, strategy, cash=cash, commission=commission)
    #     stats_validation = bt_training.optimize(EMA_timeperiod=range(50,130, 10), fastperiod=range(4,20, 4), slowperiod=range(20,32, 4), signal_period = range(3,15,3), maximize="Return [%]")
    #
    #     EMA_timeperiod = stats_validation._EMA_timeperiod
    #     fastperiod = stats_validation.fastperiod
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

    master = []

    start_time = time.time()
    with Pool() as p:
        master.append(p.map(walk_forward,os.listdir("data")))

    flattened_data = []
    for sublist in master:
        for item in sublist:
            for stock, records in item.items():
                for record in records:
                    for date, values in record.items():
                        record_dict = {
                            'name': stock,
                            'Start (Training)': values['Start (Training)'],
                            'End (Training)': values['End (Training)'],
                            'Start (Testing)': values['Start (Testing)'],
                            'End (Testing)': values['End (Testing)'],
                            'Duration': values['Duration'],
                            'Exposure Time [%]': values['Exposure Time [%]'],
                            'Equity Final [$]': values['Equity Final [$]'],
                            'Equity Peak [$]': values['Equity Peak [$]'],
                            'Return [%]': values['Return [%]'],
                            'Buy & Hold Return [%]': values['Buy & Hold Return [%]'],
                            'Return (Ann.) [%]': values['Return (Ann.) [%]'],
                            'Sharpe Ratio': values['Sharpe Ratio'],
                            'Sortino Ratio': values['Sortino Ratio'],
                            'Calmar Ratio': values['Calmar Ratio'],
                            'Max. Drawdown [%]': values['Max. Drawdown [%]'],
                            'Avg. Drawdown [%]': values['Avg. Drawdown [%]'],
                            'Max. Drawdown Duration': values['Max. Drawdown Duration'],
                            'Max. Drawdown Duration': values['Max. Drawdown Duration'],
                            '# Trades': values['# Trades'],
                            'Win Rate [%]': values['Win Rate [%]'],
                            'Best Trade [%]': values['Best Trade [%]'],
                            'Worst Trade [%]': values['Worst Trade [%]'],
                            'Avg. Trade [%]': values['Avg. Trade [%]'],
                            'Max. Trade Duration': values['Max. Trade Duration'],
                            'Avg. Trade Duration': values['Avg. Trade Duration'],
                            'Profit Factor': values['Profit Factor'],
                            'Expectancy [%]': values['Expectancy [%]'],
                            'SQN': values['SQN'],
                            'EMA_timeperiod': values['EMA_timeperiod'],
                            'fastperiod': values['fastperiod'],
                            'slowperiod': values['slowperiod'],
                            'signal_period': values['signal_period']
                        }
                        flattened_data.append(record_dict)

    df = pd.DataFrame(flattened_data)
    with pd.option_context('display.max_rows', None, 'display.max_columns', None):
        print(df)

    excel_path = "Test1.xlsx"
    df.to_excel(excel_path, index=False, sheet_name="Sheet1")

    print(f"DataFrame successfully saved to {excel_path}")

    end_time = time.time()
    print(f"Time taken is {end_time - start_time} seconds with multi-threading")

