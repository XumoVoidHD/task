import os
from multiprocessing import Pool
import time
import pandas as pd
import sys
import matplotlib.pyplot as plt
import datetime
import mplfinance as mpf
from scipy import stats, signal
import plotly.express as px
import plotly.graph_objects as go
asset = "AAPL"
timeframe = "1day"
folder = "data"

if __name__ == "__main__":
    script_path = os.path.abspath(sys.argv[0])
    script_directory = os.path.dirname(script_path)
    v = os.path.dirname(script_directory)

    data = pd.read_csv(f"{v}\\data\\{folder}\\{asset}_XNAS_{timeframe}.csv")
    data = data.rename(columns={'timestamp': 'Date','open': 'Open', "high": "High", 'low': 'Low', 'close': 'Close', 'volume': 'Volume'})
    data['Date'] = pd.to_datetime(data['Date'], unit='ms').dt.date
    # data.set_index("Date", inplace=True)
    data.reset_index(drop=True, inplace=True)
    print(data)
    data = data[:100]
    # px.histogram(data, x='Volume', y='Close', nbins=150, orientation='h').show()
    fig = go.Figure(data=go.Candlestick(x=data['Date'],
                                 open=data['Open'],
                                 high=data['High'],
                                 low=data['Low'],
                                 close=data['Close']))
    fig.show()




