import pandas as pd
import mplfinance as mpf
import matplotlib.pyplot as plt
import os
import sys


asset = "AAPL"
timeframe = "1day"
folder = "data"

if __name__ == "__main__":
    script_path = os.path.abspath(sys.argv[0])
    script_directory = os.path.dirname(script_path)
    v = os.path.dirname(script_directory)

    data = pd.read_csv(f"{v}\\data\\{folder}\\{asset}_XNAS_{timeframe}.csv")
    data = data.rename(columns={'timestamp': 'Date','open': 'Open', "high": "High", 'low': 'Low', 'close': 'Close', 'volume': 'Volume'})
    data['Date'] = pd.to_datetime(data['Date'], unit='ms')
    data.set_index("Date", inplace=True)
    # data.reset_index(drop=True, inplace=True)
    data = data[-500:]
    print(data)
    df = data

    fig, ax = plt.subplots(2, 1, sharex=True, gridspec_kw={'height_ratios': [3, 1]}, figsize=(10, 8))

    mpf.plot(df, type='candle', ax=ax[0], volume=ax[1], style='yahoo')

    ax[0].set_title('Candlestick Chart with Volume')
    ax[0].set_ylabel('Price [$]')
    ax[1].set_ylabel('Volume (in millions)')

    plt.show()