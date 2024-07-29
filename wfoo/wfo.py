import datetime
import time
import numpy as np
import talib
import pandas as pd
from backtesting import Backtest, Strategy
from multiprocessing import Pool
import os
from backtesting.lib import crossover


class ADXMOMENTUM(Strategy):
    multiplier1=200
    multiplier2=100
    dema_var=60
    atr_var=5
    adx_var=15
    mom_var=15
    bb_var=14

    def init(self):
        self.dema50=self.I(talib.DEMA,self.data.Close,timeperiod=self.dema_var)
        self.atr=self.I(talib.ATR,self.data.High,self.data.Low,self.data.Close,timeperiod=self.atr_var)
        self.hl2=(self.data.High+self.data.Low)/2
        self.lowerband=(self.hl2-(3*self.atr))
        self.upperband=(self.hl2+(3*self.atr))
        self.adx=self.I(talib.ADX,self.data.High,self.data.Low,self.data.Close,timeperiod=self.adx_var)
        self.mom=self.I(talib.MOM,self.data.Close,timeperiod=self.mom_var)
        self.bblow,self.bbmid,self.bbhigh=self.I(talib.BBANDS,self.data.Close,timeperiod=self.bb_var)

    # def next(self):
    #     # try to further imporove the logic with -3,-2 with the close price increasing.
    #     # now the problem is fixed it is behaving slightly better.
    #     if ((self.lowerband[-4] > self.dataa.Close[-3] or self.bblow[-4] > self.dataa.Close[-3]) and
    #             (self.dataa.Close[-1] < self.dema50[-1]) and
    #             ((self.adx[-2] > self.adx[-3] and self.mom[-1] > 0) or
    #              (self.dataa.Close[-3] < self.dataa.Close[-2] < self.dataa.Close[-1]))):
    #         self.position.close()
    #         self.buy(sl=(self.dataa.Close-self.atr*(self.multiplier2/100)*0.5),
    #                  tp=(self.dataa.Close+self.atr*(self.multiplier1/100)*1.5))
    #
    #     elif ((self.upperband[-4] < self.dataa.Close[-3] or self.bbhigh[-4] < self.dataa.Close[-3]) and
    #           (self.dataa.Close[-1] > self.dema50[-1]) and
    #           ((self.adx[-2] < self.adx[-3] and self.mom[-1] < 0) or
    #            (self.dataa.Close[-3] > self.dataa.Close[-2] > self.dataa.Close[-1]))):
    #         self.position.close()
    #         self.sell(tp=(self.dataa.Close-self.atr*(self.multiplier2/100)*0.5),
    #                   sl=(self.dataa.Close+self.atr*(self.multiplier1/100)*1.5))

    def next(self):
        if ((self.lowerband[-4] > self.data.Close[-3] or self.bblow[-4] > self.data.Close[-3]) and
                (self.data.Close[-1] < self.dema50[-1]) and
                ((self.adx[-2] > self.adx[-3] and self.mom[-1] > 0) or
                 (self.data.Close[-3] < self.data.Close[-2] < self.data.Close[-1]))):
            self.position.close()
            self.buy()

        elif ((self.upperband[-4] < self.data.Close[-3] or self.bbhigh[-4] < self.data.Close[-3]) and
              (self.data.Close[-1] > self.dema50[-1]) and
              ((self.adx[-2] < self.adx[-3] and self.mom[-1] < 0) or
               (self.data.Close[-3] > self.data.Close[-2] > self.data.Close[-1]))):
            self.position.close()
            self.sell()


class Walk_forward:
    def walk_forward(self, filename, minutes, dir):

        stat_master = []

        data = pd.read_csv(f"{dir}/{filename}")
        data = data.rename(columns={'timestamp': 'OpenTime', 'open': 'Open', "high": "High", 'low': 'Low',
                                    'close': 'Close', 'volume': 'Volume'})
        data['OpenTime'] = pd.to_datetime(data['OpenTime'], unit='ms')
        data.set_index("OpenTime", inplace=True)
        sym = filename.split("_")[0]
        print("Start: " + sym)
        start_date = data.index[0]
        end_date = start_date + pd.DateOffset(months=4)

        while end_date not in data.index:
            end_date -= pd.Timedelta(minutes=minutes)

        while start_date not in data.index:
            start_date += pd.Timedelta(minutes=minutes)

        df_4_months = data.loc[start_date:end_date]
        stat_master.append(self.run_backtest(df_4_months, ADXMOMENTUM, minutes))


        while pd.Timestamp(end_date) <= datetime.datetime(2024,6,10, 0, 0,0):
            start_date = start_date + pd.DateOffset(months=1)
            end_date = start_date + pd.DateOffset(months=4)

            while (end_date not in data.index and pd.Timestamp(end_date) <=
                   datetime.datetime(2024,6,10, 0, 0,0)):
                end_date -= pd.Timedelta(minutes=minutes)

            if pd.Timestamp(end_date) > datetime.datetime(2024,6,10, 0, 0,0):
                end_date = data.index[-1]

            while (start_date not in data.index and pd.Timestamp(end_date) <=
                   datetime.datetime(2024,6,10, 0, 0,0)):
                start_date += pd.Timedelta(minutes=minutes)

            df_4_months = data.loc[start_date:end_date]
            stat_master.append(self.run_backtest(df_4_months, ADXMOMENTUM, minutes))


        print("End: " + sym)
        return {sym: stat_master}

    def custom_constraint_function(self, params, training_data):
        bt = Backtest(training_data, ADXMOMENTUM, cash=10_000, commission=.002)
        stats = bt.run(**params)
        num_trades = stats['# Trades']
        min_trades = 2
        return num_trades >= min_trades

    def run_backtest(self,df, strategy, minutes, cash=10000, commission=0.002):

        print(df)

        stat_instance = {}

        start_date = df.index[0]
        end_date = df.index[-1]
        end_3_month_date = start_date + pd.DateOffset(months=3)
        start_1_month_date = end_date - pd.DateOffset(months=1)

        while (end_3_month_date not in df.index and pd.Timestamp(end_3_month_date) <=
               datetime.datetime(2024, 6, 10, 0, 0, 0)):
            end_3_month_date -= pd.Timedelta(minutes=minutes)

        while (start_1_month_date not in df.index and pd.Timestamp(start_1_month_date) <=
               datetime.datetime(2024, 6, 10, 0, 0, 0)):
            start_1_month_date += pd.Timedelta(minutes=minutes)

        training_data = df.loc[start_date:end_3_month_date]
        validation_data = df.loc[start_1_month_date:end_date]

        bt_training = Backtest(training_data, strategy, cash=cash, commission=commission)
        stats_validation = bt_training.optimize(
            multiplier1=range(199,201,1),
            multiplier2=range(99,101,1),
            mom_var=range(14,16,1),
            adx_var=range(14,16,1),
            dema_var=range(59,61,1),
            atr_var=range(4,6,1),
            bb_var=range(13,15,1),
            maximize='Sharpe Ratio'
        )
        #self.constraint=lambda params: custom_constraint_function(params, training_data))
        optimized_params = stats_validation['_strategy']

        multiplier1 = int(optimized_params.multiplier1)
        multiplier2 = int(optimized_params.multiplier2)
        mom_var = int(optimized_params.mom_var)
        adx_var = int(optimized_params.adx_var)
        dema_var = int(optimized_params.dema_var)
        atr_var = int(optimized_params.atr_var)
        bb_var = int(optimized_params.bb_var)

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
            "multiplier1": multiplier1,
            "multiplier2": multiplier2,
            "mom_var": mom_var,
            "adx_var": adx_var,
            "dema_var": dema_var,
            "atr_var": atr_var,
            "bb_var": bb_var
        }

        bt_validation = Backtest(validation_data, strategy, cash=cash, commission=commission)
        stats_validation = bt_validation.run(multiplier1=multiplier1, multiplier2=multiplier2, mom_var=mom_var,
                                             adx_var=adx_var, dema_var=dema_var, atr_var=atr_var, bb_var=bb_var)

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
            "multiplier1": multiplier1,
            "multiplier2": multiplier2,
            "mom_var": mom_var,
            "adx_var": adx_var,
            "dema_var": dema_var,
            "atr_var": atr_var,
            "bb_var": bb_var
        }
        return stat_instance

    def initiater(self, args):
        return self.walk_forward(*args)


if __name__ == "__main__":

    minutes = 5
    data = 'data_5min'
    conver_to_excel = True


    master = []
    main = Walk_forward()
    start_time = time.time()
    with Pool() as p:
        master.append(p.map(main.initiater, [(filename, minutes, data) for filename in os.listdir(data)]))

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
                            "multiplier1": values["multiplier1"],
                            "multiplier2": values["multiplier2"],
                            "mom_var": values["mom_var"],
                            "adx_var": values["adx_var"],
                            "dema_var": values["dema_var"],
                            "atr_var": values["atr_var"],
                            "bb_var": values["bb_var"]

                        }
                        flattened_data.append(record_dict)

    df = pd.DataFrame(flattened_data)
    with pd.option_context('display.max_rows', None, 'display.max_columns', None):
        print(df)

    if conver_to_excel:
        excel_path = "5555 Timeframe EMA.xlsx"
        df.to_excel(excel_path, index=False, sheet_name="Sheet1")

        print(f"DataFrame successfully saved to {excel_path}")

    end_time = time.time()
    print(f"Time taken is {end_time - start_time} seconds with multi-threading")


