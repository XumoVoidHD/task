import pandas as pd
import time
import matplotlib.pyplot as plt
import mplfinance as mpf


start_time = time.time()
df = pd.read_excel("C:/Users/vedan/PycharmProjects/task/Volume Profile Indicator/POC Binance (1h timeframe).xlsx")
df = df[:100]

df['DateTime'] = pd.to_datetime(df['DateTime'])
df.set_index('DateTime', inplace=True)
fig, ax = plt.subplots(figsize=(12, 6))
mpf.plot(df, type='ohlc', ax=ax, style='charles', show_nontrading=True)
ax.plot(df.index, df['VAH'], label='VAH', linestyle='--')
ax.plot(df.index, df['VAL'], label='VAL', linestyle='--')
ax.plot(df.index, df['POC_Price'], label='POC Price', linestyle='-.')
ax.fill_between(df.index, df['VAH'], df['VAL'], color='gray', alpha=0.3)
ax.set_xlabel('DateTime')
ax.set_ylabel('Price')
ax.set_title('Candlestick Chart with VAH, VAL, and POC Prices')
ax.legend()
ax.grid(True)

plt.show()