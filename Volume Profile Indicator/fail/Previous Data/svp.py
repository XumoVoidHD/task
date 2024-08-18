import os
import sys
import pandas as pd
import time
import matplotlib.pyplot as plt


def get_data_stock(symbol="AAPL", timeframe="5minute", folder="data_5min"):
    script_path = os.path.abspath(sys.argv[0])
    script_directory = os.path.dirname(script_path)
    v = os.path.dirname(script_directory)

    data = pd.read_csv(f"{v}\\data\\{folder}\\{symbol}_XNAS_{timeframe}.csv")
    data = data.rename(columns={'timestamp': 'DateTime', 'open': 'Open', "high": "High", 'low': 'Low', 'close': 'Close',
                                'volume': 'Volume'})
    data['DateTime'] = pd.to_datetime(data['DateTime'], unit='ms')
    data.set_index("DateTime", inplace=True)
    # data.drop('Unnamed: 6', axis=1, inplace=True)
    # # data.reset_index(drop=False, inplace=True)
    # data.to_excel("test.xlsx")
    return data


def get_data_binance():
    data = pd.read_csv("/data/bitstampUSD_1-min_data_2012-01-01_to_2021-03-31.csv")
    data = data.rename(columns={'timestamp': 'DateTime', 'open': 'Open', "high": "High", 'low': 'Low', 'close': 'Close',
                                'volume': 'Volume'})
    data['DateTime'] = pd.to_datetime(data['DateTime'], unit='s')
    data.drop('Unnamed: 6',axis=1, inplace=True)
    data.dropna(inplace=True)
    data.set_index("DateTime", inplace=True)
    # data.reset_index(drop=False, inplace=True)
    # data.to_excel("test.xlsx")

    return data


def calculate_vah_val(df):
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


def timezone(df):

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

        df_one_hour['POC_Price'] = poc_price
        df_one_hour['POC_Volume'] = poc_volume
        x = calculate_vah_val(df_one_hour)
        df_one_hour['VAH'] = x[0]
        df_one_hour['VAL'] = x[1]
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

        df_one_hour['POC_Price'] = poc_price
        df_one_hour['POC_Volume'] = poc_volume
        x = calculate_vah_val(df_one_hour)
        df_one_hour['VAH'] = x[0]
        df_one_hour['VAL'] = x[1]
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

        df_one_hour['POC_Price'] = poc_price
        df_one_hour['POC_Volume'] = poc_volume
        x = calculate_vah_val(df_one_hour)
        df_one_hour['VAH'] = x[0]
        df_one_hour['VAL'] = x[1]
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

        df_one_hour['POC_Price'] = poc_price
        df_one_hour['POC_Volume'] = poc_volume
        x = calculate_vah_val(df_one_hour)
        df_one_hour['VAH'] = x[0]
        df_one_hour['VAL'] = x[1]
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

        df_one_hour['POC_Price'] = poc_price
        df_one_hour['POC_Volume'] = poc_volume
        x = calculate_vah_val(df_one_hour)
        df_one_hour['VAH'] = x[0]
        df_one_hour['VAL'] = x[1]
        slices.append(df_one_hour)
        combined_data = pd.concat([combined_data, df_one_hour])

    # excel_filename = 'sample_data 4.xlsx'
    # combined_data.to_excel(excel_filename)
    combined_data.sort_index(inplace=True)

    return combined_data


def hour_poc(df):
    starting = df.index[0]
    print(type(starting))
    ending = df.index[-120]
    combined_data = pd.DataFrame()

    while starting <= ending:
        end_date = starting + pd.Timedelta(hours=1)
        while end_date not in df.index:
            end_date += pd.Timedelta(minutes=5)

        df_one_hour = df.loc[starting:end_date]

        volume_profile = df_one_hour.groupby('Close')['Volume'].sum()
        poc_price = volume_profile.idxmax()
        poc_volume = volume_profile.max()

        df_one_hour['POC_Volume'] = poc_volume
        df_one_hour['POC_Price'] = poc_price
        x = calculate_vah_val(df_one_hour)
        df_one_hour['VAH'] = x[0]
        df_one_hour['VAL'] = x[1]

        combined_data = pd.concat([combined_data, df_one_hour])

        starting = end_date + pd.Timedelta(minutes=5)

    return combined_data


if __name__ == "__main__":

    data = get_data_stock("AAPL", "5minute", "data_5min")
    # data = get_data_binance()

    start_time = time.time()
    df = timezone(data)
    df.sort_index(inplace=True)
    data.drop('Unnamed: 6', axis=1, inplace=True)
    excel_path = "POC Stock (given timeframe).xlsx"
    df.to_excel(excel_path, index=True, sheet_name="Sheet1")
    # with pd.option_context('display.max_rows', None, 'display.max_columns', None):
    #     print(df)
    df = hour_poc(data)
    data.drop('Unnamed: 6', axis=1, inplace=True)
    excel_path = "POC Stock (1h timeframe).xlsx"
    df.to_excel(excel_path, index=True, sheet_name="Sheet1")
    # with pd.option_context('display.max_rows', None, 'display.max_columns', None):
    #     print(df)

    end_time = time.time()
    print(f"Time taken is {end_time-start_time} seconds")
