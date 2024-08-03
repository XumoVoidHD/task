import os
import sys
import pandas as pd
import time
import matplotlib.pyplot as plt


class svp:

    def __init__(self):
        # self.start_datetime = '2010-01-04  09:15:00'
        # self.end_datetime = '2024-06-10 11:55:00'
        # datetime_range = pd.date_range(start=self.start_datetime, end=self.end_datetime, freq='h')
        # self.svp_data = pd.DataFrame(datetime_range, columns=['Datetime'])
        self.svp_data = pd.DataFrame
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
        # data.drop('Unnamed: 6', axis=1, inplace=True)
        # # data.reset_index(drop=False, inplace=True)
        # data.to_excel("test.xlsx")
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
        # data.reset_index(drop=False, inplace=True)
        # data.to_excel("test.xlsx")
        self.svp_data = data

        return data

    def get_mt5_data(self, name):
        file_path = name
        df = pd.read_excel(file_path)
        df.set_index('DateTime', inplace=True)
        #df.index = pd.to_datetime(df.index)
        with pd.option_context('display.max_rows', None, 'display.max_columns', None):
            print(df)
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

        start_time = "14:00:00"
        start_time = pd.Timestamp(start_time).time()
        mask = (df.index.time == start_time)
        start_indices = df[mask].index

        combined_data = pd.DataFrame()
        slices = []
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
            self.timezone_poc_dict[str(start_index)] = float(df_one_hour['POC_Price (Timezone)'].iloc[0])
            self.timezone_vah_dict[str(start_index)] = float(df_one_hour['VAH (Timezone)'].iloc[0])
            self.timezone_val_dict[str(start_index)] = float(df_one_hour['VAL (Timezone)'].iloc[0])
            slices.append(df_one_hour)
            combined_data = pd.concat([combined_data, df_one_hour])

        start_time = "22:30:00"
        start_time = pd.Timestamp(start_time).time()
        mask = (df.index.time == start_time)
        start_indices = df[mask].index

        for start_index in start_indices:
            end = start_index + pd.Timedelta(hours=7)
            df_one_hour = df.loc[start_index:end]
            volume_profile = df_one_hour.groupby('Close')['Volume'].sum()
            poc_price = volume_profile.idxmax()
            poc_volume = volume_profile.max()

            df_one_hour['POC_Price (Timezone)'] = poc_price
            df_one_hour['POC_Volume (Timezone)'] = poc_volume
            x = self.calculate_vah_val(df_one_hour)
            df_one_hour['VAH (Timezone)'] = x[0]
            df_one_hour['VAL (Timezone)'] = x[1]
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
            df_one_hour = df.loc[start_index:end]
            volume_profile = df_one_hour.groupby('Close')['Volume'].sum()
            poc_price = volume_profile.idxmax()
            poc_volume = volume_profile.max()

            df_one_hour['POC_Price (Timezone)'] = poc_price
            df_one_hour['POC_Volume (Timezone)'] = poc_volume
            x = self.calculate_vah_val(df_one_hour)
            df_one_hour['VAH (Timezone)'] = x[0]
            df_one_hour['VAL (Timezone)'] = x[1]
            self.timezone_poc_dict[str(start_index)] = float(df_one_hour['POC_Price (Timezone)'].iloc[0])
            self.timezone_vah_dict[str(start_index)] = float(df_one_hour['VAH (Timezone)'].iloc[0])
            self.timezone_val_dict[str(start_index)] = float(df_one_hour['VAL (Timezone)'].iloc[0])
            slices.append(df_one_hour)
            combined_data = pd.concat([combined_data, df_one_hour])

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
            self.timezone_poc_dict[str(start_index)] = float(df_one_hour['POC_Price (Timezone)'].iloc[0])
            self.timezone_vah_dict[str(start_index)] = float(df_one_hour['VAH (Timezone)'].iloc[0])
            self.timezone_val_dict[str(start_index)] = float(df_one_hour['VAL (Timezone)'].iloc[0])
            slices.append(df_one_hour)
            combined_data = pd.concat([combined_data, df_one_hour])

        start_time = "7:00:00"
        start_time = pd.Timestamp(start_time).time()
        mask = (df.index.time == start_time)
        start_indices = df[mask].index

        for start_index in start_indices:
            end = start_index + pd.Timedelta(hours=3)
            df_one_hour = df.loc[start_index:end]
            volume_profile = df_one_hour.groupby('Close')['Volume'].sum()
            poc_price = volume_profile.idxmax()
            poc_volume = volume_profile.max()

            df_one_hour['POC_Price (Timezone)'] = poc_price
            df_one_hour['POC_Volume (Timezone)'] = poc_volume
            x = self.calculate_vah_val(df_one_hour)
            df_one_hour['VAH (Timezone)'] = x[0]
            df_one_hour['VAL (Timezone)'] = x[1]
            self.timezone_poc_dict[str(start_index)] = float(df_one_hour['POC_Price (Timezone)'].iloc[0])
            self.timezone_vah_dict[str(start_index)] = float(df_one_hour['VAH (Timezone)'].iloc[0])
            self.timezone_val_dict[str(start_index)] = float(df_one_hour['VAL (Timezone)'].iloc[0])
            slices.append(df_one_hour)
            combined_data = pd.concat([combined_data, df_one_hour])

        # excel_filename = 'sample_data 4.xlsx'
        # combined_data.to_excel(excel_filename)
        combined_data.sort_index(inplace=True)
        # self.svp_data = self.svp_data.join(combined_data)

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

        self.svp_data['POC_Price (Hourly)'] = combined_data['POC_Price']
        self.svp_data['POC_Volume (Hourly)'] = combined_data['POC_Volume']
        self.svp_data['VAH (Hourly)'] = combined_data['VAH']
        self.svp_data['VAL (Hourly)'] = combined_data['VAL']

        # self.svp_data = self.svp_data.join(combined_data)
        return combined_data

    def combined(self, data):
        self.hour_poc(data)
        self.timezone(data)
        self.svp_data.rename(columns={'POC_Price': 'POC_Price (Timezone)'}, inplace=True)
        self.svp_data.rename(columns={'POC_Volume': 'POC_Volume (Timezone)'}, inplace=True)
        self.svp_data.rename(columns={'VAH': 'VAH (Timezone'}, inplace=True)
        self.svp_data.rename(columns={'VAL': 'VAL (Timezone'}, inplace=True)

        return self.svp_data


if __name__ == "__main__":
    start_time = time.time()
    obj = svp()
    data = obj.get_data_stock()
    df = obj.combined(data)
    # print("Timezone_POC")
    # print(obj.timezone_poc_dict)
    # print("Timezone VAH")
    # print(obj.timezone_vah_dict)
    # print("Timezone VAL")
    # print(obj.timezone_val_dict)
    # print("Hour POC")
    # print(obj.hour_poc_dict)
    # print("Hour VAH")
    # print(obj.hour_vah_dict)
    # print("Hour VAL")
    # print(obj.hour_val_dict)
    # df.drop('Unnamed: 6', axis=1, inplace=True)

    excel_path = "Test6 POC.xlsx"
    df.to_excel(excel_path, index=True, sheet_name="Sheet1")
    with pd.option_context('display.max_rows', None, 'display.max_columns', None):
        print(df)

    end_time = time.time()

    print(f"Time taken to execute this program is {end_time-start_time} seconds")


