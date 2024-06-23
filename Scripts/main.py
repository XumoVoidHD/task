import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import sys

company_list = [
    "AAPL",  # Apple Inc.
    "MSFT",  # Microsoft Corporation
    "AMZN",  # Amazon.com Inc.
    "GOOGL",  # Alphabet Inc. (Class A)
    "GOOG",  # Alphabet Inc. (Class C)
    "BRK.B",  # Berkshire Hathaway Inc. (Class B)
    "NVDA",  # NVIDIA Corporation
    "TSLA",  # Tesla Inc.
    "META",  # Meta Platforms Inc.
    "UNH",  # UnitedHealth Group Incorporated
    "JNJ",  # Johnson & Johnson
    "V",  # Visa Inc.
    "XOM",  # Exxon Mobil Corporation
    "WMT",  # Walmart Inc.
    "JPM",  # JPMorgan Chase & Co.
    "PG",  # Procter & Gamble Company
    "MA",  # Mastercard Incorporated
    "HD",  # The Home Depot Inc.
    "CVX",  # Chevron Corporation
    "MRK",  # Merck & Co., Inc.
    "ABBV",  # AbbVie Inc.
    "PEP",  # PepsiCo, Inc.
    "KO",  # The Coca-Cola Company
    "LLY",  # Eli Lilly and Company
    "BAC",  # Bank of America Corporation
    "AVGO",  # Broadcom Inc.
    "TMO",  # Thermo Fisher Scientific Inc.
    "COST",  # Costco Wholesale Corporation
    "DIS",  # The Walt Disney Company
    "PFE",  # Pfizer Inc.
    "CSCO",  # Cisco Systems, Inc.
    "ACN",  # Accenture plc
    "ABT",  # Abbott Laboratories
    "DHR",  # Danaher Corporation
    "NFLX",  # Netflix, Inc.
    "LIN",  # Linde plc
    "NKE",  # NIKE, Inc.
    "MCD",  # McDonald's Corporation
    "NEE",  # NextEra Energy, Inc.
    "ADBE",  # Adobe Inc.
    "TXN",  # Texas Instruments Incorporated
    "PM",  # Philip Morris International Inc.
    "ORCL",  # Oracle Corporation
    "AMD",  # Advanced Micro Devices, Inc.
    "HON",  # Honeywell International Inc.
    "AMGN",  # Amgen Inc.
    "UNP",  # Union Pacific Corporation
    "MDT",  # Medtronic plc
    "IBM",  # International Business Machines Corporation
    "SBUX",  # Starbucks Corporation
    "QCOM",  # QUALCOMM Incorporated
    "GS",  # The Goldman Sachs Group, Inc.
    "LOW",  # Lowe's Companies, Inc.
    "MS",  # Morgan Stanley
    "BLK",  # BlackRock, Inc.
    "BMY",  # Bristol-Myers Squibb Company
    "CAT",  # Caterpillar Inc.
    "GE",  # General Electric Company
    "RTX",  # Raytheon Technologies Corporation
    "INTC",  # Intel Corporation
    "ISRG",  # Intuitive Surgical, Inc.
    "CHTR",  # Charter Communications, Inc.
    "AMT",  # American Tower Corporation
    "GILD",  # Gilead Sciences, Inc.
    "NOW",  # ServiceNow, Inc.
    "BKNG",  # Booking Holdings Inc.
    "PLD",  # Prologis, Inc.
    "PYPL",  # PayPal Holdings, Inc.
    "SYK",  # Stryker Corporation
    "EL",  # The Estée Lauder Companies Inc.
    "ZTS",  # Zoetis Inc.
    "SPGI",  # S&P Global Inc.
    "TMUS",  # T-Mobile US, Inc.
    "ADI",  # Analog Devices, Inc.
    "LRCX",  # Lam Research Corporation
    "SCHW",  # The Charles Schwab Corporation
    "CB",  # Chubb Limited
    "REGN",  # Regeneron Pharmaceuticals, Inc.
    "EQIX",  # Equinix, Inc.
    "MU",  # Micron Technology, Inc.
    "MMC",  # Marsh & McLennan Companies, Inc.
    "APD",  # Air Products and Chemicals, Inc.
    "ADI",  # Analog Devices, Inc.
    "FDX",  # FedEx Corporation
    "CL",  # Colgate-Palmolive Company
    "MDLZ",  # Mondelez International, Inc.
    "TGT",  # Target Corporation
    "CI",  # Cigna Corporation
    "DUK",  # Duke Energy Corporation
    "ECL",  # Ecolab Inc.
    "EW",  # Edwards Lifesciences Corporation
    "FIS",  # Fidelity National Information Services, Inc.
    "MAR",  # Marriott International, Inc.
    "GM",  # General Motors Company
    "NSC",  # Norfolk Southern Corporation
    "SO",  # The Southern Company
    "PNC",  # The PNC Financial Services Group, Inc.
    "SHW",  # The Sherwin-Williams Company
    "TFC",  # Truist Financial Corporation
    "USB",  # U.S. Bancorp
    "ITW",  # Illinois Tool Works Inc.
    "HUM",  # Humana Inc.
]



x = str(input("Stock: "))
x_data = yf.download(x, start="2018-03-24", end="2023-03-24")
x_data['ema_short'] = x_data['Close'].ewm(span=20, adjust=False).mean()
x_data['ema_long'] = x_data['Close'].ewm(span=50, adjust=False).mean()
x_data['bullish'] = 0.0
x_data['bullish'] = np.where(x_data['ema_short'] > x_data['ema_long'], 1.0, 0.0)
with pd.option_context('display.max_rows', None, 'display.max_columns', None):
    print(x_data)

