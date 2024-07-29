import datetime
import time
import numpy as np
import talib
import pandas as pd
from backtesting import Backtest, Strategy
from multiprocessing import Pool
import os

filename = "AAPL_XNAS_4hour.csv"
data = pd.read_csv(f"data_4h/{filename}")
data = data.rename(columns={'timestamp': 'OpenTime', 'open': 'Open', "high": "High", 'low': 'Low', 'close': 'Close',
                            'volume': 'Volume'})
data['OpenTime'] = pd.to_datetime(data['OpenTime'], unit='ms')
data.set_index("OpenTime", inplace=True)
print(data)
sym = filename.split("_")[0]

excel_path = "APPLE.xlsx"
data.to_excel(excel_path, index=True, sheet_name="Sheet1")


print(os.listdir("data_4h"))