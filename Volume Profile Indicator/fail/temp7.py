from collections import defaultdict
import dateutil.parser
import finplot as fplt
import pandas as pd
import pytz
import os

utc2timestamp = lambda s: int(dateutil.parser.parse(s).replace(tzinfo=pytz.utc).timestamp() * 1000)
asset = "AAPL"
timeframe = "4hour"
folder = "data_4h"

def calc_volume_profile(df, period, bins):
    data = []
    df['hlc3'] = (df['high'] + df['low'] + df['close']) / 3
    _, all_bins = pd.cut(df['hlc3'], bins, right=False, retbins=True)
    for _, g in df.groupby(pd.Grouper(key='time', freq=period)):
        t = g.time.iloc[0]
        volbins = pd.cut(g['hlc3'], all_bins, right=False)
        price2vol = defaultdict(float)
        for iv, vol in zip(volbins, g.volume):
            price2vol[iv.left] += vol
        data.append([t, sorted(price2vol.items())])
    return data

def calc_vwap(df, period):
    vwap = pd.Series([], dtype='float64')
    df['hlc3v'] = df['hlc3'] * df['volume']
    for _, g in df.groupby(pd.Grouper(key='time', freq=period)):
        g_cumsum = g.hlc3v.cumsum() / g.volume.cumsum()
        vwap = pd.concat([vwap, g_cumsum])
    return vwap

script_path = os.path.abspath(__file__)
script_directory = os.path.dirname(script_path)
v = os.path.dirname(script_directory)

data = pd.read_csv(f"{v}\\data\\{folder}\\{asset}_XNAS_{timeframe}.csv")
data = data.rename(columns={'timestamp': 'time', 'open': 'open', "high": "high", 'low': 'low', 'close': 'close', 'volume': 'volume'})
data['time'] = pd.to_datetime(data['time'], unit='ms')
data.reset_index(drop=True, inplace=True)
df = data.tail(1000)
df.reset_index(drop=True, inplace=True)
df['hlc3v'] = df['hlc3'] = (df['high'] + df['low'] + df['close']) / 3

time_volume_profile = calc_volume_profile(df, period='W', bins=len(df))
vwap = calc_vwap(df, period='W')

# Create plot
plot1 = fplt.create_plot('AAPL 4-hour candlestick chart with VWAP and Volume Profile', init_zoom_periods=1000)

# Plot candlestick pattern
candlestick_data = df[['open', 'close', 'high', 'low']]
fplt.candlestick_ochl(candlestick_data.values, ax=plot1)

# Plot VWAP
plot2 = fplt.create_plot('AAPL 4-hour candlestick chart with VWAP and Volume Profile', init_zoom_periods=100)
fplt.plot(df['time'], vwap, ax=plot2, style='--', legend='VWAP')

# Plot volume profile
#plot3 = fplt.create_plot('AAPL 4-hour candlestick chart with VWAP and Volume Profile', init_zoom_periods=100)
#fplt.horiz_time_volume(time_volume_profile, ax=plot3.overlay(), draw_va=0.7, draw_poc=1.0)

# Show plot
fplt.show()
