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
    #data.set_index("Date", inplace=True)
    data.reset_index(drop=True, inplace=True)
    data = data[:100]
    data['Volume'] = data['Volume']
    print(data)

    # Create traces
    candlestick = go.Candlestick(
        x=data['Date'],
        open=data['Open'],
        high=data['High'],
        low=data['Low'],
        close=data['Close'],
        name='Candlestick'
    )

    # Create the volume bar trace
    volume = go.Bar(
        x=data['Date'],
        y=data['Volume'],
        name='Volume',
        yaxis='y2'
    )

    # Define layout
    # layout = go.Layout(
    #     title='Candlestick Chart with Volume',
    #     xaxis=dict(title='Date'),
    #     yaxis=dict(
    #         title='Close Price',
    #         range=[data['Close'].min() * 0.95, data['Close'].max() * 1.05]  # Adjust the range to fit the close prices
    #     ),
    #     yaxis2=dict(
    #         title='Volume',
    #         overlaying='y',
    #         side='right',
    #         showgrid=True,
    #     ),
    #     legend=dict(x=0, y=1.2, orientation='h')
    # )

    layout = go.Layout(
        title='Candlestick Chart with Volume',
        xaxis=dict(title='Date'),
        yaxis=dict(
            title='Close Price',
            range=[data['Close'].min() * 0.95, data['Close'].max() * 1.05]  # Adjust the range to fit the close prices
        ),
        yaxis2=dict(
            title='Volume (in billions)',
            overlaying='y',
            side='right',
            showgrid=False,
            range=[0, data['Volume'].max() * 4.0],  # Adjust the range for the volume axis
            type='linear',  # Change to 'log' if you want a logarithmic scale
            tickformat=',.0f'  # Format ticks to show as whole numbers
        ),
        legend=dict(x=0, y=1.2, orientation='h')
    )

    # Create figure
    fig = go.Figure(data=[candlestick, volume], layout=layout)

    # Plot the figure
    fig.show()
