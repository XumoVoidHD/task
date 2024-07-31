import pandas as pd
import numpy as np

# Sample market data (replace with your actual data source)
# Assuming DataFrame df with columns: DateTime, Price, Volume
# df = pd.read_csv('your_market_data.csv', parse_dates=['DateTime'])

# Sample data creation for illustration
date_rng = pd.date_range(start='2024-07-27', end='2024-07-30', freq='T')
df = pd.DataFrame(date_rng, columns=['DateTime'])
df['Price'] = np.random.randint(100, 200, size=(len(date_rng)))
df['Volume'] = np.random.randint(1, 100, size=(len(date_rng)))

# Resample data to hourly intervals
df.set_index('DateTime', inplace=True)
hourly_data = df.resample('H').agg({'Price': 'ohlc', 'Volume': 'sum'})
hourly_data.columns = ['Open', 'High', 'Low', 'Close', 'Volume']

# Initialize lists to store VAH, VAL, and POC
vah_list = []
val_list = []
poc_list = []

print(hourly_data)
# Calculate Market Profile for each hour
for index, row in hourly_data.iterrows():
    hourly_prices = df.loc[index:index + pd.Timedelta(hours=1)]

    # Create price histogram
    price_volume = hourly_prices.groupby('Price')['Volume'].sum()

    # Calculate POC
    poc = price_volume.idxmax()
    poc_list.append(poc)

    # Calculate VAH and VAL
    total_volume = price_volume.sum()
    sorted_prices = price_volume.sort_values(ascending=False)
    cumulative_volume = sorted_prices.cumsum()

    val = sorted_prices[cumulative_volume <= total_volume * 0.15].index.max()
    vah = sorted_prices[cumulative_volume >= total_volume * 0.85].index.min()

    val_list.append(val)
    vah_list.append(vah)

# Output the results
print("VAH List:", vah_list)
print("VAL List:", val_list)
print("POC List:", poc_list)
