import os
import sys
import pandas as pd
import time
import matplotlib.pyplot as plt
import numpy as np
from backtesting import Backtest, Strategy
from multiprocessing import Pool
from backtesting.lib import crossover


class svp:
    def __init__(self):
        self.svp_data = pd.DataFrame
        self.svp_hour_data = pd.DataFrame
        self.svp_timezone_data = pd.DataFrame
        self.timezone_poc_dict = {}
        self.timezone_vah_dict = {}
        self.timezone_val_dict = {}
        self.hour_poc_dict = {}
        self.hour_vah_dict = {}
        self.hour_val_dict = {}

    def get_data_stock(self, symbol="AAPL", timeframe="5minute", folder="data_5min"):
        script_path = os.path.abspath(sys.argv[0])
        script_directory = os.path.dirname(script_path)
        v = os.path.dirname(script_directory)

        data = pd.read_csv(f"{v}\\data\\{folder}\\{symbol}_XNAS_{timeframe}.csv")
        data = data.rename(
            columns={'timestamp': 'DateTime', 'open': 'Open', "high": "High", 'low': 'Low', 'close': 'Close',
                     'volume': 'Volume'})
        data['DateTime'] = pd.to_datetime(data['DateTime'], unit='ms')
        data.set_index("DateTime", inplace=True)
        self.svp_data = data

        data.to_excel("wow.xlsx", index=True, sheet_name="Sheet1")
        return data

    def get_data_binance(self):
        data = pd.read_csv(
            "C:/Users/vedan/PycharmProjects/task/data/binance_data.csv")
        data = data.rename(
            columns={'timestamp': 'DateTime', 'open': 'Open', "high": "High", 'low': 'Low', 'close': 'Close',
                     'volume': 'Volume'})
        data['DateTime'] = pd.to_datetime(data['DateTime'], unit='s')
        # data.drop('Unnamed: 6', axis=1, inplace=True)
        data.dropna(inplace=True)
        data.set_index("DateTime", inplace=True)
        self.svp_data = data

        return data

    def get_mt5_data(self, name):
        # file_path = name
        # df = pd.read_excel(file_path)
        df = pd.read_csv("USDJPY_owo.csv")
        df['DateTime'] = pd.to_datetime(df['DateTime'])
        df.set_index('DateTime', inplace=True)
        df = df.drop(columns=['Vol', 'Spread'])

        return df

    def calculate_vah_val(self, df):
        volume_profile = df.groupby('Close')['Volume'].sum()

        volume_profile = volume_profile.sort_values(ascending=False)

        total_volume = volume_profile.sum()

        value_area_volume = total_volume * 0.70

        accumulated_volume = 0
        value_area_prices = []

        for price, volume in volume_profile.items():
            accumulated_volume += volume
            value_area_prices.append(price)
            if accumulated_volume >= value_area_volume:
                break

        vah = max(value_area_prices)
        val = min(value_area_prices)

        return vah, val

    def timezone(self, df):

        combined_data = pd.DataFrame()
        slices = []

        start_time = "7:00:00"
        start_time = pd.Timestamp(start_time).time()
        mask = (df.index.time == start_time)
        start_indices = df[mask].index

        for start_index in start_indices:
            end = start_index + pd.Timedelta(hours=3)
            end_end = end + pd.Timedelta(hours=2)
            df_one_hour = df.loc[start_index:end]
            volume_profile = df_one_hour.groupby('Close')['Volume'].sum()
            poc_price = volume_profile.idxmax()
            poc_volume = volume_profile.max()

            df_one_hour['POC_Price (Timezone)'] = poc_price
            df_one_hour['POC_Volume (Timezone)'] = poc_volume
            x = self.calculate_vah_val(df_one_hour)
            df_one_hour['VAH (Timezone)'] = x[0]
            df_one_hour['VAL (Timezone)'] = x[1]
            df_one_hour['Resistance'] = x[0] + 6 * 0.0001
            df_one_hour['Support'] = x[1] - 6 * 0.0001
            self.timezone_poc_dict[str(start_index)] = float(df_one_hour['POC_Price (Timezone)'].iloc[0])
            self.timezone_vah_dict[str(start_index)] = float(df_one_hour['VAH (Timezone)'].iloc[0])
            self.timezone_val_dict[str(start_index)] = float(df_one_hour['VAL (Timezone)'].iloc[0])
            slices.append(df_one_hour)
            combined_data = pd.concat([combined_data, df_one_hour])
            while(end < (end_end-pd.Timedelta(minutes=1))):
                try:
                    combined_data.loc[end, 'Resistance'] = combined_data.loc[end-pd.Timedelta(minutes=1), 'Resistance']
                    combined_data.loc[end, 'Support'] = combined_data.loc[end-pd.Timedelta(minutes=1), 'Support']
                except Exception as e:
                    pass
                end += pd.Timedelta(minutes=1)


        start_time = "12:00:00"
        start_time = pd.Timestamp(start_time).time()
        mask = (df.index.time == start_time)
        start_indices = df[mask].index

        for start_index in start_indices:
            end = start_index + pd.Timedelta(hours=2)
            df_one_hour = df.loc[start_index:end]
            volume_profile = df_one_hour.groupby('Close')['Volume'].sum()
            poc_price = volume_profile.idxmax()
            poc_volume = volume_profile.max()

            df_one_hour['POC_Price (Timezone)'] = poc_price
            df_one_hour['POC_Volume (Timezone)'] = poc_volume
            x = self.calculate_vah_val(df_one_hour)
            df_one_hour['VAH (Timezone)'] = x[0]
            df_one_hour['VAL (Timezone)'] = x[1]
            df_one_hour['Resistance'] = x[0] + 6 * 0.0001
            df_one_hour['Support'] = x[1] - 6 * 0.0001
            self.timezone_poc_dict[str(start_index)] = float(df_one_hour['POC_Price (Timezone)'].iloc[0])
            self.timezone_vah_dict[str(start_index)] = float(df_one_hour['VAH (Timezone)'].iloc[0])
            self.timezone_val_dict[str(start_index)] = float(df_one_hour['VAL (Timezone)'].iloc[0])
            slices.append(df_one_hour)
            combined_data = pd.concat([combined_data, df_one_hour])


        start_time = "14:00:00"
        start_time = pd.Timestamp(start_time).time()
        mask = (df.index.time == start_time)
        start_indices = df[mask].index

        for start_index in start_indices:
            end = start_index + pd.Timedelta(hours=1)
            df_one_hour = df.loc[start_index:end]
            volume_profile = df_one_hour.groupby('Close')['Volume'].sum()
            poc_price = volume_profile.idxmax()
            poc_volume = volume_profile.max()

            df_one_hour['POC_Price (Timezone)'] = poc_price
            df_one_hour['POC_Volume (Timezone)'] = poc_volume

            x = self.calculate_vah_val(df_one_hour)
            df_one_hour['VAH (Timezone)'] = x[0]
            df_one_hour['VAL (Timezone)'] = x[1]
            df_one_hour['Resistance'] = x[0] + 6 * 0.0001
            df_one_hour['Support'] = x[1] - 6 * 0.0001
            self.timezone_poc_dict[str(start_index)] = float(df_one_hour['POC_Price (Timezone)'].iloc[0])
            self.timezone_vah_dict[str(start_index)] = float(df_one_hour['VAH (Timezone)'].iloc[0])
            self.timezone_val_dict[str(start_index)] = float(df_one_hour['VAL (Timezone)'].iloc[0])
            slices.append(df_one_hour)
            combined_data = pd.concat([combined_data, df_one_hour])


        start_time = "15:00:00"
        start_time = pd.Timestamp(start_time).time()
        mask = (df.index.time == start_time)
        start_indices = df[mask].index

        for start_index in start_indices:
            end = start_index + pd.Timedelta(hours=2)
            end_end = end + pd.Timedelta(minutes=330)
            df_one_hour = df.loc[start_index:end]
            volume_profile = df_one_hour.groupby('Close')['Volume'].sum()
            poc_price = volume_profile.idxmax()
            poc_volume = volume_profile.max()

            df_one_hour['POC_Price (Timezone)'] = poc_price
            df_one_hour['POC_Volume (Timezone)'] = poc_volume
            x = self.calculate_vah_val(df_one_hour)
            df_one_hour['VAH (Timezone)'] = x[0]
            df_one_hour['VAL (Timezone)'] = x[1]
            df_one_hour['Resistance'] = x[0] + 6 * 0.0001
            df_one_hour['Support'] = x[1] - 6 * 0.0001
            self.timezone_poc_dict[str(start_index)] = float(df_one_hour['POC_Price (Timezone)'].iloc[0])
            self.timezone_vah_dict[str(start_index)] = float(df_one_hour['VAH (Timezone)'].iloc[0])
            self.timezone_val_dict[str(start_index)] = float(df_one_hour['VAL (Timezone)'].iloc[0])
            slices.append(df_one_hour)
            combined_data = pd.concat([combined_data, df_one_hour])
            while(end < end_end):
                try:
                    combined_data.loc[end, 'Resistance'] = combined_data.loc[end-pd.Timedelta(minutes=1), 'Resistance']
                    combined_data.loc[end, 'Support'] = combined_data.loc[end-pd.Timedelta(minutes=1), 'Support']
                except Exception as e:
                    pass
                end += pd.Timedelta(minutes=1)


        start_time = "22:30:00"
        start_time = pd.Timestamp(start_time).time()
        mask = (df.index.time == start_time)
        start_indices = df[mask].index

        for start_index in start_indices:
            end = start_index + pd.Timedelta(hours=7)
            end_end = end + pd.Timedelta(minutes=90)
            df_one_hour = df.loc[start_index:end]
            volume_profile = df_one_hour.groupby('Close')['Volume'].sum()
            poc_price = volume_profile.idxmax()
            poc_volume = volume_profile.max()

            df_one_hour['POC_Price (Timezone)'] = poc_price
            df_one_hour['POC_Volume (Timezone)'] = poc_volume
            x = self.calculate_vah_val(df_one_hour)
            df_one_hour['VAH (Timezone)'] = x[0]
            df_one_hour['VAL (Timezone)'] = x[1]
            df_one_hour['Resistance'] = x[0] + 6 * 0.0001
            df_one_hour['Support'] = x[1] - 6 * 0.0001
            self.timezone_poc_dict[str(start_index)] = float(df_one_hour['POC_Price (Timezone)'].iloc[0])
            self.timezone_vah_dict[str(start_index)] = float(df_one_hour['VAH (Timezone)'].iloc[0])
            self.timezone_val_dict[str(start_index)] = float(df_one_hour['VAL (Timezone)'].iloc[0])
            slices.append(df_one_hour)
            combined_data = pd.concat([combined_data, df_one_hour])
            while(end < end_end):
                try:
                    combined_data.loc[end, 'Resistance'] = combined_data.loc[end-pd.Timedelta(minutes=1), 'Resistance']
                    combined_data.loc[end, 'Support'] = combined_data.loc[end-pd.Timedelta(minutes=1), 'Support']
                except Exception as e:
                    pass
                end += pd.Timedelta(minutes=1)

        combined_data.sort_index(inplace=True)
        self.svp_timezone_data = combined_data

        return combined_data

    def hour_poc(self, df):
        starting = df.index[0]
        ending = df.index[-10]
        combined_data = pd.DataFrame()

        while starting <= ending:
            end_date = starting + pd.Timedelta(hours=1)
            while end_date not in df.index:
                end_date += pd.Timedelta(minutes=1)

            df_one_hour = df.loc[starting:end_date]

            volume_profile = df_one_hour.groupby('Close')['Volume'].sum()
            poc_price = volume_profile.idxmax()
            poc_volume = volume_profile.max()

            df_one_hour['POC_Volume'] = poc_volume
            df_one_hour['POC_Price'] = poc_price
            x = self.calculate_vah_val(df_one_hour)
            df_one_hour['VAH'] = x[0]
            df_one_hour['VAL'] = x[1]

            self.hour_poc_dict[str(starting)] = float(df_one_hour['POC_Price'].iloc[0])
            self.hour_vah_dict[str(starting)] = float(df_one_hour['VAH'].iloc[0])
            self.hour_val_dict[str(starting)] = float(df_one_hour['VAL'].iloc[0])

            combined_data = pd.concat([combined_data, df_one_hour])

            starting = end_date + pd.Timedelta(minutes=1)

        self.svp_hour_data = combined_data
        return combined_data

    def generate_buy_and_sell(self):
        self.svp_data['Buy'] = np.where(self.svp_data['Close'] - self.svp_data['Resistance'] > 0, 1, 0)
        self.svp_data['Sell'] = np.where(self.svp_data['Close'] - self.svp_data['Support'] < 0, 1, 0)

    def combined(self, data):
        self.hour_poc(data)
        self.timezone(data)
        self.svp_timezone_data.drop(columns=['Open', 'High', 'Low', 'Close', 'Volume'], inplace=True)
        self.svp_data = self.svp_hour_data.join(self.svp_timezone_data, sort=True)
        self.svp_data.rename(columns={'POC_Price': 'POC_Price (Hourly)'}, inplace=True)
        self.svp_data.rename(columns={'POC_Volume': 'POC_Volume (Hourly)'}, inplace=True)
        self.svp_data.rename(columns={'VAH': 'VAH (Hourly)'}, inplace=True)
        self.svp_data.rename(columns={'VAL': 'VAL (Hourly)'}, inplace=True)
        self.generate_buy_and_sell()

        return self.svp_data

    def print_dict(self):
        print("Timezone_POC")
        print(self.timezone_poc_dict)
        print("Timezone VAH")
        print(self.timezone_vah_dict)
        print("Timezone VAL")
        print(self.timezone_val_dict)
        print("Hour POC")
        print(self.hour_poc_dict)
        print("Hour VAH")
        print(self.hour_vah_dict)
        print("Hour VAL")
        print(self.hour_val_dict)

    def plot(self, data=None, read=False):
        if read:
            df = pd.read_excel("C:/Users/vedan/PycharmProjects/task/Volume Profile Indicator/Test17.xlsx")
        else:
            df = data
        plt.figure(figsize=(12, 6))
        plt.plot(df.index, df['Close'], label='Close', marker='o')
        plt.plot(df.index, df['VAH (Hourly)'], label='VAH Hourly', linestyle='--')
        plt.plot(df.index, df['VAL (Hourly)'], label='VAL Hourly', linestyle='--')
        plt.plot(df.index, df['POC_Price (Hourly)'], label='POC Price Hourly', linestyle='-.')
        plt.plot(df.index, df['VAH (Timezone)'], label='VAH Timezone', linestyle='--')
        plt.plot(df.index, df['VAL (Timezone)'], label='VAL Timezone', linestyle='--')
        plt.plot(df.index, df['Resistance'], label='VAH Timezone', linestyle='--')
        plt.plot(df.index, df['Support'], label='VAL Timezone', linestyle='--')
        plt.plot(df.index, df['POC_Price (Timezone)'], label='POC Price Timezone', linestyle='-.')
        buy_signal = data[data['Buy'] == 1]
        sell_signal = data[data['Sell'] == 1]
        plt.scatter(buy_signal.index, buy_signal['Close']+0.5, label='Buy Signal', marker="^", color='green', alpha=1, s=200)
        plt.scatter(sell_signal.index, sell_signal['Close']+0.5, label='Sell Signal', marker="v", color='red', alpha=1, s=200)
        plt.fill_between(df.index, df['VAH (Hourly)'], df['VAL (Hourly)'], color='gray', alpha=0.3)
        plt.fill_between(df.index, df['VAH (Timezone)'], df['VAL (Timezone)'], color='blue', alpha=0.3)
        plt.fill_between(df.index, df['Resistance'], df['Support'], color='red', alpha=0.3)
        plt.xlabel('DateTime')
        plt.ylabel('Price')
        plt.title('Close, VAH, VAL, and POC Prices')
        plt.legend()
        plt.grid(True)
        plt.show()


class TUPOC(Strategy):


    def __init__(self, broker, data, params):
        super().__init__(broker, data, params)


    def init(self):
        pass

    def next(self):
        buy_signal = self.data["Buy"][-1]
        sell_signal = self.data['Sell'][-1]

        if buy_signal == 1:
            self.buy()
        elif sell_signal == 1:
            self.sell()



if __name__ == "__main__":
    file_path = "C:/Users/vedan/PycharmProjects/task/Volume Profile Indicator/Test29.xlsx"
    data = pd.read_excel(file_path, sheet_name='Sheet1')
    data.set_index('DateTime', inplace=True)
    print(data)
    # data.index = data.index.strftime('%Y-%m-%d %H:%M:%S')
    print(data)
    backtest = Backtest(data, TUPOC, exclusive_orders=True)
    stats = backtest.run()
    print(stats["_trades"])
    print(stats)