from collections import defaultdict
import dateutil.parser
import finplot as fplt
import pandas as pd
import pytz
import requests
import sys
import os


utc2timestamp = lambda s: int(dateutil.parser.parse(s).replace(tzinfo=pytz.utc).timestamp() * 1000)
print(utc2timestamp)
asset = "AAPL"
timeframe = "1day"
folder = "data_1d"

# def download_price_history(symbol='BTCUSDT', start_time='2020-06-22', end_time='2020-08-19', interval_mins=1):
#     interval_ms = 1000*60*interval_mins
#     interval_str = '%sm'%interval_mins if interval_mins<60 else '%sh'%(interval_mins//60)
#     start_time = utc2timestamp(start_time)
#     end_time = utc2timestamp(end_time)
#     data = []
#     for start_t in range(start_time, end_time, 1000*interval_ms):
#         end_t = start_t + 1000*interval_ms
#         if end_t >= end_time:
#             end_t = end_time - interval_ms
#         url = 'https://www.binance.com/fapi/v1/klines?interval=%s&limit=%s&symbol=%s&startTime=%s&endTime=%s' % (interval_str, 1000, symbol, start_t, end_t)
#         print(url)
#         d = requests.get(url).json()
#         assert type(d)==list, d
#         data += d
#     df = pd.DataFrame(data, columns='time open high low close volume a b c d e f'.split())
#     return df.astype({'time':'datetime64[ms]', 'open':float, 'high':float, 'low':float, 'close':float, 'volume':float})


def calc_volume_profile(df, period, bins):
    data = []
    df['hlc3'] = (df['high'] + df['low'] + df['close']) / 3
    _,all_bins = pd.cut(df['hlc3'], bins, right=False, retbins=True)
    for _,g in df.groupby(pd.Grouper(key='time', freq=period)):
        t = g.time.iloc[0]
        volbins = pd.cut(g['hlc3'], all_bins, right=False)
        price2vol = defaultdict(float)
        for iv,vol in zip(volbins, g.volume):
            price2vol[iv.left] += vol
        data.append([t, sorted(price2vol.items())])

    return data


def calc_vwap(period):
    vwap = pd.Series([], dtype='float64')
    df['hlc3v'] = df['hlc3'] * df['volume']
    for _,g in df.groupby(pd.Grouper(key='time', freq=period)):
        i0,i1 = g.index[0],g.index[-1]
        vwap = pd.concat([vwap, g.hlc3v.loc[i0:i1].cumsum() / df.volume.loc[i0:i1].cumsum()])
    return vwap


script_path = os.path.abspath(sys.argv[0])
script_directory = os.path.dirname(script_path)
v = os.path.dirname(script_directory)

data = pd.read_csv(f"{v}\\data\\{folder}\\{asset}_XNAS_{timeframe}.csv")
data = data.rename(columns={'timestamp': 'time','open': 'open', "high": "high", 'low': 'low', 'close': 'close', 'volume': 'volume'})
data['time'] = pd.to_datetime(data['time'], unit='ms')
# data.set_index("time", inplace=True)
data.reset_index(drop=True, inplace=True)
df = data.tail(1000)
df.reset_index(drop=True, inplace=True)
df['hlc3v'] = [0.0] * len(df)
df['hlc3'] = [0.0] * len(df)
df['vah'] = [0.0] * len(df)
df['val'] = [0.0] * len(df)
df['poc'] = [0.0] * len(df)
print(df)
time_volume_profile = calc_volume_profile(df, period='W', bins=len(df))
vwap = calc_vwap(period='W')

plot = fplt.create_plot('AAPL 4h Data')
fplt.plot(df.time, df.open, legend='Open')
fplt.plot(df.time, df.high, legend='High')
fplt.plot(df.time, df.low, legend='Low')
fplt.plot(df.time, df.close, legend='Close')
fplt.plot(df.time, vwap, style='--', legend='VWAP', ax=plot)
fplt.horiz_time_volume(time_volume_profile, draw_va=0.7, draw_poc=0.5, ax=plot)
# fplt.candlestick_ochl(df[['open', 'high', 'low', 'close']], ax=plot.overlay())

fplt.show()