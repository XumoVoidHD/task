from collections import defaultdict
import dateutil.parser
import finplot as fplt
import pandas as pd
import pytz
import requests
import sys
import os

utc2timestamp = lambda s: int(dateutil.parser.parse(s).replace(tzinfo=pytz.utc).timestamp() * 1000)
asset = "AAPL"
timeframe = "4hour"
folder = "data_4h"


def calc_volume_profile(df, period, bins):
    df['hlc3'] = (df['high'] + df['low'] + df['close']) / 3
    _, all_bins = pd.cut(df['hlc3'], bins, right=False, retbins=True)
    volume_profiles = []

    for _, g in df.groupby(pd.Grouper(key='time', freq=period)):
        volbins = pd.cut(g['hlc3'], all_bins, right=False)
        price2vol = defaultdict(float)

        for iv, vol in zip(volbins, g['volume']):
            price2vol[iv.left] += vol

        sorted_price2vol = sorted(price2vol.items())
        total_volume = sum(price2vol.values())
        cum_volume = 0.0
        vah = val = poc = None

        for price, vol in sorted_price2vol:
            cum_volume += vol
            if poc is None or vol > price2vol[poc]:
                poc = price
            if vah is None and cum_volume >= 0.7 * total_volume:
                vah = price
            if val is None and cum_volume >= 0.3 * total_volume:
                val = price

        volume_profiles.append((g['time'].iloc[0], vah, val, poc))

    return volume_profiles


def calc_vwap(period):
    vwap = pd.Series([], dtype='float64')
    df['hlc3v'] = df['hlc3'] * df['volume']
    for _, g in df.groupby(pd.Grouper(key='time', freq=period)):
        i0, i1 = g.index[0], g.index[-1]
        vwap = pd.concat([vwap, g.hlc3v.loc[i0:i1].cumsum() / df.volume.loc[i0:i1].cumsum()])
    return vwap


# download and calculate indicators
# df = download_price_history(interval_mins=30) # reduce to [15, 5, 1] minutes to increase accuracy
script_path = os.path.abspath(sys.argv[0])
script_directory = os.path.dirname(script_path)
v = os.path.dirname(script_directory)

data = pd.read_csv(f"{v}\\data\\{folder}\\{asset}_XNAS_{timeframe}.csv")
data = data.rename(
    columns={'timestamp': 'time', 'open': 'open', "high": "high", 'low': 'low', 'close': 'close', 'volume': 'volume'})
data['time'] = pd.to_datetime(data['time'], unit='ms')
data.reset_index(drop=True, inplace=True)
df = data.tail(1000)
df.reset_index(drop=True, inplace=True)
df['hlc3v'] = [0.0] * len(df)
df['hlc3'] = [0.0] * len(df)
df['vah'] = [0.0] * len(df)
df['val'] = [0.0] * len(df)
df['poc'] = [0.0] * len(df)

# Calculate volume profile and vwap
volume_profile = calc_volume_profile(df, period='W', bins=len(df))
vwap = calc_vwap(period='W')

# Extract VAH, VAL, POC from the volume profile
for time, vah, val, poc in volume_profile:
    df.loc[df['time'] == time, 'vah'] = vah
    df.loc[df['time'] == time, 'val'] = val
    df.loc[df['time'] == time, 'poc'] = poc

plot = fplt.create_plot('AAPL 4-hour Volume Profile')
fplt.plot(df.time, df.open, legend='Open')
fplt.plot(df.time, df.high, legend='High')
fplt.plot(df.time, df.low, legend='Low')
fplt.plot(df.time, df.close, legend='Close')
fplt.plot(df.time, vwap, style='--', legend='VWAP', ax=plot)

fplt.plot(df.time, df.vah, style='-.', color='#FF0000', legend='VAH', ax=plot)  # Red dashed line
fplt.plot(df.time, df.val, style='v', color='#0000FF', legend='VAL', ax=plot)   # Blue dotted line
fplt.plot(df.time, df.poc, style='^', color='#00FF00', width=2, legend='POC', ax=plot) # Green solid line, thicker

fplt.show()