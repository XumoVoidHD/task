import time
import talib
import pandas as pd
from backtesting import Backtest, Strategy
from multiprocessing import Pool
import os
from backtesting.lib import crossover


class MACD_Strategy(Strategy):

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
        self.ma = talib.EMA(prices, timeperiod=100)
        self.macd = self.I(lambda x: talib.MACD(x)[0], prices)
        self.macd_signal = self.I(lambda x: talib.MACD(x)[1], prices)
        self.macd_hist = self.I(lambda x: talib.MACD(x)[2], prices)
        self.atr = self.I(talib.ATR, self.data.High, self.data.Low, self.data.Close, timeperiod=14)

    def next(self):
        price = self.data['Close']
        atr_value = self.atr[-1]
        take_profit = price + 3 * atr_value
        stop_loss = price - 1.5 * atr_value

        if crossover(self.macd, self.macd_signal) and self.macd < 0 and self.macd_signal < 0:
            self.buy()

        if crossover(self.macd_signal, self.macd) and self.macd > 0 and self.macd_signal > 0:
            self.sell()

        # if self.data.iloc[-2]["macd_line"] < 0 and self.data.iloc[-2]["signal_line"] < 0 and self.data.iloc[-2][
        #     'Moving Average'] < self.data.iloc[-2]["Close"]:
        #     if self.data.iloc[-3]["macd_line"] < self.data.iloc[-3]["signal_line"] and self.data.iloc[-2]["macd_line"] > \
        #             self.data.iloc[-2]["signal_line"]:
        #         print("Buy")
        #         self.buy(tp= take_profit, sl= stop_loss)
        #
        # if self.data.iloc[-2]["macd_line"] > 0 and self.data.iloc[-2]["signal_line"] > 0 and self.data.iloc[-2][
        #     'Moving Average'] > self.data.iloc[-2]["Close"]:
        #     if self.data.iloc[-3]["macd_line"] > self.data.iloc[-3]["signal_line"] and self.data.iloc[-2]["macd_line"] < \
        #             self.data.iloc[-2]["signal_line"]:
        #         print("Sell")
        #         self.position.close()


def do_backtest(filename):
    data = pd.read_csv(f"data/{filename}")
    # os.remove(f"data/{filename}")
    data = data.rename(columns={'timestamp': 'OpenTime','open': 'Open', "high": "High", 'low': 'Low', 'close': 'Close', 'volume': 'Volume'})
    data['OpenTime'] = pd.to_datetime(data['OpenTime'], unit='ms')
    data.set_index("OpenTime", inplace=True)
    backtest = Backtest(data, MACD_Strategy, commission=0.002, exclusive_orders=True)
    stats = backtest.run()
    sym = filename.split("_")[0]
    # backtest.plot(filename=sym, open_browser=False)

    return (sym, stats)


if __name__ == "__main__":

    multi_threading = True

    if multi_threading:
        start_time = time.time()
        with Pool()  as p:
            result = p.map(do_backtest, os.listdir("data"))
        end_time = time.time()

        it = 1
        # for i in result:
        #     print("\n" +i[0] + "'s Performance "+ str(it) + "\n")
        #     print(i[1])
        #     it += 1

        print(f"Time taken is {end_time-start_time} seconds with multi-threading")
    else:
        it = 0
        start_time = time.time()
        files = os.listdir("C:/Users/vedan/PycharmProjects/task/Multi-Threaded Backtesting/data")
        for file in files:
            result = do_backtest(file)
            # print("\n" +result[0] + "'s Performance "+ str(it) + "\n")
            # print(result[1])
            # it += 1
        # print(it)
        end_time = time.time()
        print(f"Time taken is {end_time-start_time} seconds without multi_threading")