import pandas as pd
import plotly.graph_objs as go
import plotly.express as px
import time

# Load data
start_time = time.time()
df = pd.read_excel("C:/Users/vedan/PycharmProjects/task/Volume Profile Indicator/Test12 POC.xlsx")
df = df[-500:]
# Create traces
trace_close = go.Scatter(x=df['DateTime'], y=df['Close'], mode='lines+markers', name='Close')
trace_vah_hourly = go.Scatter(x=df['DateTime'], y=df['VAH (Hourly)'], mode='lines', name='VAH Hourly', line=dict(dash='dash'))
trace_val_hourly = go.Scatter(x=df['DateTime'], y=df['VAL (Hourly)'], mode='lines', name='VAL Hourly', line=dict(dash='dash'))
trace_poc_hourly = go.Scatter(x=df['DateTime'], y=df['POC_Price (Hourly)'], mode='lines', name='POC Price Hourly', line=dict(dash='dot'))
trace_vah_timezone = go.Scatter(x=df['DateTime'], y=df['VAH (Timezone)'], mode='lines', name='VAH Timezone', line=dict(dash='dash'))
trace_val_timezone = go.Scatter(x=df['DateTime'], y=df['VAL (Timezone)'], mode='lines', name='VAL Timezone', line=dict(dash='dash'))
trace_poc_timezone = go.Scatter(x=df['DateTime'], y=df['POC_Price (Timezone)'], mode='lines', name='POC Price Timezone', line=dict(dash='dot'))

# Create filled areas
trace_fill_hourly = go.Scatter(
    x=df['DateTime'].tolist() + df['DateTime'][::-1].tolist(),
    y=df['VAH (Hourly)'].tolist() + df['VAL (Hourly)'][::-1].tolist(),
    fill='toself',
    fillcolor='rgba(128, 128, 128, 0.3)',
    line=dict(color='rgba(255,255,255,0)'),
    showlegend=False
)

trace_fill_timezone = go.Scatter(
    x=df['DateTime'].tolist() + df['DateTime'][::-1].tolist(),
    y=df['VAH (Timezone)'].tolist() + df['VAL (Timezone)'][::-1].tolist(),
    fill='toself',
    fillcolor='rgba(255, 0, 0, 0.3)',
    line=dict(color='rgba(255,255,255,0)'),
    showlegend=False
)

# Create figure
fig = go.Figure(data=[trace_close, trace_vah_hourly, trace_val_hourly, trace_poc_hourly, trace_vah_timezone, trace_val_timezone, trace_poc_timezone, trace_fill_hourly, trace_fill_timezone])

# Update layout
fig.update_layout(
    title='Close, VAH, VAL, and POC Prices',
    xaxis_title='DateTime',
    yaxis_title='Price',
    legend_title='Legend',
    xaxis=dict(showgrid=True),
    yaxis=dict(showgrid=True),
    template='plotly_white'
)

# Show plot
fig.show()

end_time = time.time()
print(f"Time taken is {end_time - start_time} seconds")