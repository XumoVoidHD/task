import os
import sys
import pandas as pd
import time
import matplotlib.pyplot as plt

start_time = time.time()
df = pd.read_excel("C:/Users/vedan/PycharmProjects/task/Volume Profile Indicator/POC Binance (1h timeframe).xlsx")
df = df[:100]

plt.figure(figsize=(12, 6))
plt.plot(df['DateTime'], df['Close'], label='Close', marker='o')
plt.plot(df['DateTime'], df['VAH'], label='VAH', linestyle='--')
plt.plot(df['DateTime'], df['VAL'], label='VAL', linestyle='--')
plt.plot(df['DateTime'], df['POC_Price'], label='POC Price', linestyle='-.')
plt.fill_between(df['DateTime'], df['VAH'], df['VAL'], color='gray', alpha=0.3)
plt.xlabel('DateTime')
plt.ylabel('Price')
plt.title('Close, VAH, VAL, and POC Prices')
plt.legend()
plt.grid(True)
plt.show()
end_time = time.time()
print(f"Time taken is {end_time - start_time} seconds")