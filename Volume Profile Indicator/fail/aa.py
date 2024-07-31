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
from plotly.subplots import make_subplots


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
    #data.set_index("Date", inplace=True)
    data.reset_index(drop=True, inplace=True)
    # data = data[:100]
    print(data)
    df = data


# Create the candlestick trace
    candlestick = go.Candlestick(
        x=df['Date'],
        open=df['Open'],
        high=df['High'],
        low=df['Low'],
        close=df['Close'],
        name='Candlestick'
    )

    # Create the volume bar trace
    volume = go.Bar(
        x=df['Date'],
        y=df['Volume'],
        name='Volume'
    )

    # Create subplots: 2 rows, 1 column
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True,
                        vertical_spacing=0.02, row_heights=[0.9, 0.3])

    # Add candlestick trace to the first row
    fig.add_trace(candlestick, row=1, col=1)

    # Add volume trace to the second row
    fig.add_trace(volume, row=2, col=1)

    # Update layout
    fig.update_layout(
        title='Candlestick Chart with Volume',
        xaxis=dict(title='Date'),
        yaxis=dict(title='Price'),
        yaxis2=dict(title='Volume (in thousands)'),
        showlegend=False
    )

    # Plot the figure
    fig.show()