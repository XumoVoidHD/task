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
    ema_long = 50
    ema_short = 20

    def init(self):
        price = self.data.Close
        self.ma1 = self.I(talib.EMA, price, timeperiod=self.ema_short)
        self.ma2 = self.I(talib.EMA, price, timeperiod=self.ema_long)
        self.atr = self.I(talib.ATR, self.data.High, self.data.Low, self.data.Close, timeperiod=14)

    def next(self):
        price = self.data.Close[-1]
        atr_value = self.atr[-1]

        take_profit = price + 3 * atr_value
        stop_loss = price - 1.5 * atr_value
        if crossover(self.ma1, self.ma2):
            self.buy(tp=take_profit, sl=stop_loss)
        elif crossover(self.ma2, self.ma1):
            self.position.close()

def walk_forward(filename):
    stat_master = []

    data = pd.read_csv(f"data/{filename}")
    data = data.rename(columns={'timestamp': 'OpenTime','open': 'Open', "high": "High", 'low': 'Low', 'close': 'Close', 'volume': 'Volume'})
    data['OpenTime'] = pd.to_datetime(data['OpenTime'], unit='ms')
    data.set_index("OpenTime", inplace=True)
    sym = filename.split("_")[0]
    print(sym)
    start_date = data.index[0]
    end_date = start_date + pd.DateOffset(months=8)

    df_4_months = data.loc[start_date:end_date]
    stat_master.append(run_backtest(df_4_months, MACD_Strategy))

    while pd.Timestamp(end_date) <= datetime.datetime(2024, 6, 10, 0, 0, 0):
        start_date = end_date
        end_date = start_date + pd.DateOffset(months=8)
        df_4_months = data.loc[start_date:end_date]
        stat_master.append(run_backtest(df_4_months, MACD_Strategy))

    return {sym: stat_master}

def run_backtest(df, strategy, cash=10000, commission=0.002):
    stat_instance = {}

    start_date = df.index.min()
    end_date = df.index.max()

    end_3_month_date = start_date + pd.DateOffset(months=6)
    start_1_month_date = end_date - pd.DateOffset(months=2)

    training_data = df.loc[start_date:end_3_month_date]
    validation_data = df.loc[start_1_month_date:end_date]

    def custom_objective_function(stats):
        final_equity = stats['Equity Final [$]']
        sharpe_ratio = stats['Sharpe Ratio']
        return final_equity * 0.5 + sharpe_ratio * 0.5

    def custom_constraint_function(params):
        bt = Backtest(training_data, MACD_Strategy, cash=10_000, commission=.002)
        stats = bt.run(**params)
        num_trades = stats['# Trades']
        min_trades = 5
        return num_trades >= min_trades

    bt_training = Backtest(training_data, strategy, cash=cash, commission=commission)
    stats_validation = bt_training.optimize(
        ema_short=range(4, 60, 2),
        ema_long=range(10, 90, 2),
        maximize=lambda params: params['Return [%]'],
        constraint=lambda params: params.ema_short < params.ema_long and custom_constraint_function(params)
    )

    optimized_params = stats_validation['_strategy']
    ema_short = optimized_params.ema_short
    ema_long = optimized_params.ema_long

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
        "ema_long": int(optimized_params.ema_long),
        "ema_short": int(optimized_params.ema_short),
    }

    bt_validation = Backtest(validation_data, strategy, cash=cash, commission=commission)
    stats_validation = bt_validation.run(ema_long=ema_long, ema_short=ema_short)

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
        "ema_long": int(optimized_params.ema_long),
        "ema_short": int(optimized_params.ema_short),
    }

    return stat_instance

if __name__ == "__main__":
    master = []

    start_time = time.time()
    with Pool() as p:
        master.append(p.map(walk_forward, os.listdir("data")))

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
                            "ema_long": values['ema_long'],
                            "ema_short": values['ema_short'],
                        }
                        flattened_data.append(record_dict)

    df_stats = pd.DataFrame(flattened_data)
    df_stats.to_csv("walk_forward_optimized_params.csv", index=False)
    print("--- %s seconds ---" % (time.time() - start_time))
