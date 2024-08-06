import os
import sys
import pandas as pd
import time
import matplotlib.pyplot as plt

start_time = time.time()
df = pd.read_excel("C:/Users/vedan/PycharmProjects/task/Volume Profile Indicator/Test15.xlsx")
# df = df[-2000:]

plt.figure(figsize=(12, 6))
plt.plot(df['DateTime'], df['Close'], label='Close', marker='o')
plt.plot(df['DateTime'], df['VAH (Hourly)'], label='VAH Hourly', linestyle='--')
plt.plot(df['DateTime'], df['VAL (Hourly)'], label='VAL Hourly', linestyle='--')
plt.plot(df['DateTime'], df['POC_Price (Hourly)'], label='POC Price Hourly', linestyle='-.')
plt.plot(df['DateTime'], df['VAH (Timezone)'], label='VAH Timezone', linestyle='--')
plt.plot(df['DateTime'], df['VAL (Timezone)'], label='VAL Timezone', linestyle='--')
plt.plot(df['DateTime'], df['POC_Price (Timezone)'], label='POC Price Timezone', linestyle='-.')
plt.fill_between(df['DateTime'], df['VAH (Hourly)'], df['VAL (Hourly)'], color='gray', alpha=0.3)
plt.fill_between(df['DateTime'], df['VAH (Timezone)'], df['VAL (Timezone)'], color='red', alpha=0.3)
plt.xlabel('DateTime')
plt.ylabel('Price')
plt.title('Close, VAH, VAL, and POC Prices')
plt.legend()
plt.grid(True)
plt.show()
end_time = time.time()
print(f"Time taken is {end_time - start_time} seconds")