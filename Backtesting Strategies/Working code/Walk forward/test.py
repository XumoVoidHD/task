import datetime
import time
import numpy as np
import talib
import pandas as pd
from backtesting import Backtest, Strategy
from multiprocessing import Pool
import os
from backtesting.lib import crossover


class ADX_Strategy(Strategy):
    rsi_timeperiod = 14
    adx_timeperiod = 14
    dema_timeperiod = 14

    def __init__(self, broker, data, params):
        super().__init__(broker, data, params)
        self.adx = None
        self.rsi = None
        self.dema200 = None

    def init(self):
        self.dema200 = self.I(talib.DEMA, self.data.Close, timeperiod=self.dema_timeperiod)
        self.adx = self.I(talib.ADX, self.data.High, self.data.Low, self.data.Close, timeperiod=self.adx_timeperiod)
        self.rsi = self.I(talib.RSI, self.data.Close, timeperiod=self.rsi_timeperiod)

    def next(self):
        if (self.adx[-1] > self.adx[-2] and self.data.Close > self.dema200 and self.rsi < 70 and self.data.Volume[-1] >
                self.data.Volume[-2]):
            self.buy()

        elif (self.adx[-1] < self.adx[-2] and self.data.Close < self.dema200 and self.rsi > 70 and self.data.Volume[
            -1] < self.data.Volume[-2]):
            self.sell()


def walk_forward(filename):

    stat_master = []

    data = pd.read_csv(f"C:/Users/vedan/PycharmProjects/task/Backtesting Strategies/dataa/{filename}")
    data = data.rename(columns={'timestamp': 'OpenTime','open': 'Open', "high": "High", 'low': 'Low', 'close': 'Close', 'volume': 'Volume'})
    data['OpenTime'] = pd.to_datetime(data['OpenTime'], unit='ms')
    data.set_index("OpenTime", inplace=True)
    sym = filename.split("_")[0]
    print("Start: " + sym)
    start_date = data.index[0]
    end_date = start_date + pd.DateOffset(months=4)

    # print(f"Pre1: {end_date}")
    while end_date not in data.index:
        # print("hit1")
        end_date -= pd.Timedelta(hours=1)
    # print(f"Post1: {end_date}")

    # print(f"Pre2: {start_date}")
    while start_date not in data.index:
        # print("hit2")
        start_date += pd.Timedelta(hours=1)
    # print(f"Post2: {start_date}")

    df_4_months = data.loc[start_date:end_date]
    stat_master.append(run_backtest(df_4_months, ADX_Strategy))


    while pd.Timestamp(end_date) <= datetime.datetime(2024,6,10, 0, 0,0):
        start_date = start_date + pd.DateOffset(months=1)
        end_date = start_date + pd.DateOffset(months=4)
        # print(f"Pre3: {end_date}")
        while end_date not in data.index and pd.Timestamp(end_date) <= datetime.datetime(2024,6,10, 0, 0,0):
            # print("hit3")
            end_date -= pd.Timedelta(hours=1)
        # print(f"Post3: {end_date}")

        if pd.Timestamp(end_date) > datetime.datetime(2024,6,10, 0, 0,0):
            end_date = data.index[-1]

        # print(f"Post4: {start_date}")
        while start_date not in data.index and pd.Timestamp(end_date) <= datetime.datetime(2024,6,10, 0, 0,0):
            # print("hit4")
            start_date += pd.Timedelta(hours=1)
        # print(f"Post4: {start_date}")

        df_4_months = data.loc[start_date:end_date]
        stat_master.append(run_backtest(df_4_months, ADX_Strategy))


    print("End: " + sym)
    return {sym: stat_master}


def run_backtest(df, strategy, cash=10000, commission=0.002):

    def custom_constraint_function(params):
        bt = Backtest(training_data, ADX_Strategy, cash=10_000, commission=.002)
        stats = bt.run(**params)
        num_trades = stats['# Trades']
        min_trades = 2
        return num_trades >= min_trades

    stat_instance = {}

    start_date = df.index[0]
    end_date = df.index[-1]
    # print("Start: " + str(start_date))
    # print("End: " + str(end_date))
    end_3_month_date = start_date + pd.DateOffset(months=3)
    start_1_month_date = end_date - pd.DateOffset(months=1)
    # print(df)

    # print(f"Pre5: {end_3_month_date}")
    while end_3_month_date not in df.index and pd.Timestamp(end_3_month_date) <= datetime.datetime(2024, 6, 10, 0, 0, 0):
        # print("hit5: " + str(end_3_month_date))
        end_3_month_date -= pd.Timedelta(hours=1)
    # print(f"Post5: {end_3_month_date}")

    # print(f"Pre6: {start_1_month_date}")
    while start_1_month_date not in df.index and pd.Timestamp(start_1_month_date) <= datetime.datetime(2024, 6, 10, 0, 0, 0):
        # print("hit6: " + str(start_1_month_date))
        start_1_month_date += pd.Timedelta(hours=1)

    # print(f"Post6: {start_1_month_date}")

    training_data = df.loc[start_date:end_3_month_date]
    validation_data = df.loc[start_1_month_date:end_date]

    bt_training = Backtest(training_data, strategy, cash=cash, commission=commission)
    stats_validation = bt_training.optimize(rsi_timeperiod=range(4, 24, 4),adx_timeperiod=range(4, 24, 4), dema_timeperiod=range(10, 250, 20),
                                            maximize='Equity Final [$]')
                                            #constraint=lambda params: custom_constraint_function(params))
    optimized_params = stats_validation['_strategy']

    rsi_timeperiod = optimized_params.rsi_timeperiod
    adx_timeperiod = optimized_params.adx_timeperiod
    dema_timeperiod = optimized_params.dema_timeperiod

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
        'SQN': str(stats_validation['SQN'])
    }

    bt_validation = Backtest(validation_data, strategy, cash=cash, commission=commission)
    stats_validation = bt_validation.run(rsi_timeperiod=rsi_timeperiod, adx_timeperiod=adx_timeperiod, dema_timeperiod= dema_timeperiod)

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
    }

    return stat_instance


if __name__ == "__main__":

    master = []

    start_time = time.time()
    with Pool() as p:
        master.append(p.map(walk_forward,os.listdir("C:/Users/vedan/PycharmProjects/task/Backtesting Strategies/dataa")))

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
                        }
                        flattened_data.append(record_dict)

    df = pd.DataFrame(flattened_data)
    with pd.option_context('display.max_rows', None, 'display.max_columns', None):
        print(df)

    excel_path = "wfo.xlsx"
    df.to_excel(excel_path, index=False, sheet_name="Sheet1")

    print(f"DataFrame successfully saved to {excel_path}")

    end_time = time.time()
    print(f"Time taken is {end_time - start_time} seconds with multi-threading")


