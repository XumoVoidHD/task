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


def do_backtest(filename):
    result_data = []

    data = pd.read_csv(f"C:/Users/vedan/PycharmProjects/task/Backtesting Strategies/data/{filename}")
    # os.remove(f"dataa/{filename}")
    data = data.rename(columns={'timestamp': 'OpenTime','open': 'Open', "high": "High", 'low': 'Low', 'close': 'Close', 'volume': 'Volume'})
    data['OpenTime'] = pd.to_datetime(data['OpenTime'], unit='ms')
    data.set_index("OpenTime", inplace=True)
    backtest = Backtest(data, StochRSI_Strategy, commission=0.002, exclusive_orders=True)
    stats = backtest.optimize(rsi_timeperiod=range(10,20,2), stochrsi_timeperiod=range(10,20,2), maximize="Return [%]")
    sym = filename.split("_")[0]
   #  backtest.plot(filename=sym, open_browser=False)
    optimized_params = stats['_strategy']
    return (sym, stats['Start'], stats['End'], stats['Duration'], stats['Exposure Time [%]'], stats['Equity Final [$]'], stats['Equity Peak [$]'], stats['Return [%]'], stats['Buy & Hold Return [%]'], stats['Return (Ann.) [%]'], stats['Return (Ann.) [%]'], stats['Sharpe Ratio'], stats['Sortino Ratio'], stats['Calmar Ratio'], stats['Max. Drawdown [%]'], stats['Avg. Drawdown [%]'], stats['Max. Drawdown Duration'], stats['Max. Drawdown Duration'], stats['# Trades'], stats['Win Rate [%]'], stats['Best Trade [%]'], stats['Worst Trade [%]'], stats['Avg. Trade [%]'], stats['Max. Trade Duration'], stats['Avg. Trade Duration'], stats['Profit Factor'], stats['Expectancy [%]'], stats['SQN'])




if __name__ == "__main__":

    convert_to_excel = True

    multi_threading = True
    results = None
    if multi_threading:
        start_time = time.time()
        with Pool() as p:
            results = p.map(do_backtest, os.listdir("C:/Users/vedan/PycharmProjects/task/Backtesting Strategies/data"))
        end_time = time.time()

        # it = 1
        # for i in results:
        #     print("\n" + str(i[7]) + "'s Performance "+ str(it) + "\n")
        #     print(i[1])
        #     it += 1

        print(f"Time taken is {end_time-start_time} seconds with multi-threading")
    else:
        it = 0
        start_time = time.time()
        files = os.listdir("C:/Users/vedan/PycharmProjects/task/Multi-Threaded Backtesting/data")
        for file in files:
            result = StochRSI_Strategy(file)
            # print("\n" +result[0] + "'s Performance "+ str(it) + "\n")
            # print(result[1])
            # it += 1
        # print(it)
        end_time = time.time()
        print(f"Time taken is {end_time-start_time} seconds without multi_threading")

    if convert_to_excel:
        names = []
        start = []
        end = []
        duration = []
        exposure_time = []
        equity_final = []
        equity_peak = []
        returns = []
        buy_and_hold = []
        returns_annum = []
        volatility = []
        sharpe_ratio = []
        sortino_ratio = []
        calmar_ratio = []
        max_drawdown = []
        avg_drawdown = []
        max_drawdown_duration = []
        avg_drawdown_duration = []
        trades = []
        win_rate = []
        best_trades = []
        worst_trades = []
        avg_trades = []
        max_trade_druation = []
        avg_trade_duration = []
        profit_factor = []
        expectancy = []
        SQN = []


        for i in range(0, len(results)):
            names.append(results[i][0])
            start.append(str(results[i][1]))
            end.append(str(results[i][2]))
            duration.append(results[i][3])
            exposure_time.append(results[i][4])
            equity_final.append(results[i][5])
            equity_peak.append(results[i][6])
            returns.append(results[i][7])
            buy_and_hold.append(results[i][8])
            returns_annum.append(results[i][9])
            volatility.append(results[i][10])
            sharpe_ratio.append(results[i][11])
            sortino_ratio.append(results[i][12])
            calmar_ratio.append(results[i][13])
            max_drawdown.append(results[i][14])
            avg_drawdown.append(results[i][15])
            max_drawdown_duration.append(results[i][16])
            avg_drawdown_duration.append(results[i][17])
            trades.append(results[i][18])
            win_rate.append(results[i][19])
            best_trades.append(results[i][20])
            worst_trades.append(results[i][21])
            avg_trades.append(results[i][22])
            max_trade_druation.append(results[i][23])
            avg_trade_duration.append(results[i][24])
            profit_factor.append(results[i][25])
            expectancy.append(results[i][26])
            SQN.append(results[i][27])


        existing_data = {
            "Index": range(1, len(names) + 1)
        }

        df = pd.DataFrame(existing_data)
        df['Names'] = names
        df['Start'] = start
        df['End'] = end
        df['Duration'] = duration
        df['Exposure Time [%]'] = exposure_time
        df['Equity Final [$]'] = equity_final
        df['Equity Final [$]'] = equity_peak
        df['Return [%]'] = returns
        df['Buy & Hold Return [%]'] = buy_and_hold
        df['Return (Ann.) [%]'] = returns_annum
        df['Volatility (Ann.) [%]'] = volatility
        df['Sharpe Ratio'] = sharpe_ratio
        df['Sortino Ratio'] = sortino_ratio
        df['Calmar Ratio'] = calmar_ratio
        df['Max. Drawdown [%]'] = max_drawdown
        df['Avg. Drawdown [%] '] = avg_drawdown
        df['Max. Drawdown Duration'] = max_drawdown_duration
        df['Avg. Drawdown Duration'] = avg_drawdown_duration
        df['# Trades'] = trades
        df['Win Rate [%]'] = win_rate
        df['Best Trade [%]'] = best_trades
        df['Worst Trade [%]'] = worst_trades
        df['Avg. Trade [%]'] = avg_trades
        df['Max. Trade Duration'] = max_trade_druation
        df['Avg. Trade Duration'] = avg_trade_duration
        df['Profit Factor'] = profit_factor
        df['Expectancy [%]'] = expectancy
        df['SQN'] = SQN


        excel_path = "stochastic_rsi 2.xlsx"

        # Convert the DataFrame to an Excel file
        df.to_excel(excel_path, index=False, sheet_name="Sheet1")

        print(f"DataFrame successfully saved to {excel_path}")