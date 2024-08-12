import os
import sys
import matplotlib.pyplot as plt
import MetaTrader5 as mt5
import pandas as pd
from datetime import datetime, timedelta
import time
import pytz


pips = 6
pips_weightage = 0.0001


class svp:
    def __init__(self):
        self.svp_data = pd.DataFrame
        self.svp_hour_data = pd.DataFrame
        self.svp_timezone_data = pd.DataFrame
        self.timezone_poc_dict = {}
        self.timezone_vah_dict = {}
        self.timezone_val_dict = {}
        self.hour_poc_dict = []
        self.hour_vah_dict = []
        self.hour_val_dict = []
        self.support = []
        self.resistance = []

    def get_data_stock(self, symbol="AAPL", timeframe="5minute", folder="data_5min"):
        script_path = os.path.abspath(sys.argv[0])
        script_directory = os.path.dirname(script_path)
        v = os.path.dirname(script_directory)

        data = pd.read_csv(f"{v}\\data\\{folder}\\{symbol}_XNAS_{timeframe}.csv")
        data = data.rename(
            columns={'timestamp': 'DateTime', 'open': 'Open', "high": "High", 'low': 'Low', 'close': 'Close',
                     'volume': 'Volume'})
        data['DateTime'] = pd.to_datetime(data['DateTime'], unit='ms')
        data.set_index("DateTime", inplace=True)
        self.svp_data = data

        data.to_excel("wow.xlsx", index=True, sheet_name="Sheet1")
        return data

    def get_data_binance(self):
        data = pd.read_csv(
            "/data/binance_data.csv")
        data = data.rename(
            columns={'timestamp': 'DateTime', 'open': 'Open', "high": "High", 'low': 'Low', 'close': 'Close',
                     'volume': 'Volume'})
        data['DateTime'] = pd.to_datetime(data['DateTime'], unit='s')
        # data.drop('Unnamed: 6', axis=1, inplace=True)
        data.dropna(inplace=True)
        data.set_index("DateTime", inplace=True)
        self.svp_data = data

        return data

    def get_mt5_data(self, name):
        # file_path = name
        # df = pd.read_excel(file_path)
        df = pd.read_csv(name)
        df['DateTime'] = pd.to_datetime(df['DateTime'])
        df.set_index('DateTime', inplace=True)
        df = df.drop(columns=['Vol', 'Spread'])

        return df

    def calculate_vah_val(self, df):
        volume_profile = df.groupby('Close')['Volume'].sum()

        volume_profile = volume_profile.sort_values(ascending=False)

        total_volume = volume_profile.sum()

        value_area_volume = total_volume * 0.70

        accumulated_volume = 0
        value_area_prices = []

        for price, volume in volume_profile.items():
            accumulated_volume += volume
            value_area_prices.append(price)
            if accumulated_volume >= value_area_volume:
                break

        vah = max(value_area_prices)
        val = min(value_area_prices)

        return vah, val

    def timezone(self, df):

        combined_data = pd.DataFrame()
        slices = []

        start_time = "7:00:00"
        start_time = pd.Timestamp(start_time).time()
        mask = (df.index.time == start_time)
        start_indices = df[mask].index

        for start_index in start_indices:
            end = start_index + pd.Timedelta(hours=3)
            end_end = end + pd.Timedelta(hours=2)
            df_one_hour = df.loc[start_index:end]
            volume_profile = df_one_hour.groupby('Close')['Volume'].sum()
            poc_price = volume_profile.idxmax()
            poc_volume = volume_profile.max()

            df_one_hour['POC_Price (Timezone)'] = poc_price
            df_one_hour['POC_Volume (Timezone)'] = poc_volume
            x = self.calculate_vah_val(df_one_hour)
            df_one_hour['VAH (Timezone)'] = x[0]
            df_one_hour['VAL (Timezone)'] = x[1]
            df_one_hour['Resistance'] = x[0] + pips * pips_weightage
            df_one_hour['Support'] = x[1] - pips * pips_weightage
            # self.timezone_poc_dict = [float(df_one_hour['POC_Price (Timezone)'].iloc[0]), 2, str(start_index)]
            self.resistance.append([float(df_one_hour['VAH (Timezone)'].iloc[0]), 2, str(start_index)])
            self.support.append([float(df_one_hour['VAL (Timezone)'].iloc[0]), 2, str(start_index)])
            slices.append(df_one_hour)
            combined_data = pd.concat([combined_data, df_one_hour])
            while(end < (end_end-pd.Timedelta(minutes=1))):
                try:
                    combined_data.loc[end, 'Resistance'] = combined_data.loc[end-pd.Timedelta(minutes=1), 'Resistance']
                    combined_data.loc[end, 'Support'] = combined_data.loc[end-pd.Timedelta(minutes=1), 'Support']
                except Exception as e:
                    pass
                end += pd.Timedelta(minutes=1)


        start_time = "12:00:00"
        start_time = pd.Timestamp(start_time).time()
        mask = (df.index.time == start_time)
        start_indices = df[mask].index

        for start_index in start_indices:
            end = start_index + pd.Timedelta(hours=2)
            df_one_hour = df.loc[start_index:end]
            volume_profile = df_one_hour.groupby('Close')['Volume'].sum()
            poc_price = volume_profile.idxmax()
            poc_volume = volume_profile.max()

            df_one_hour['POC_Price (Timezone)'] = poc_price
            df_one_hour['POC_Volume (Timezone)'] = poc_volume
            x = self.calculate_vah_val(df_one_hour)
            df_one_hour['VAH (Timezone)'] = x[0]
            df_one_hour['VAL (Timezone)'] = x[1]
            df_one_hour['Resistance'] = x[0] + pips * pips_weightage
            df_one_hour['Support'] = x[1] - pips * pips_weightage
            # self.timezone_poc_dict = [float(df_one_hour['POC_Price (Timezone)'].iloc[0]), 2, str(start_index)]
            self.resistance.append([float(df_one_hour['VAH (Timezone)'].iloc[0]), 2, str(start_index)])
            self.support.append([float(df_one_hour['VAL (Timezone)'].iloc[0]), 2, str(start_index)])
            slices.append(df_one_hour)
            combined_data = pd.concat([combined_data, df_one_hour])


        start_time = "14:00:00"
        start_time = pd.Timestamp(start_time).time()
        mask = (df.index.time == start_time)
        start_indices = df[mask].index

        for start_index in start_indices:
            end = start_index + pd.Timedelta(hours=1)
            df_one_hour = df.loc[start_index:end]
            volume_profile = df_one_hour.groupby('Close')['Volume'].sum()
            poc_price = volume_profile.idxmax()
            poc_volume = volume_profile.max()

            df_one_hour['POC_Price (Timezone)'] = poc_price
            df_one_hour['POC_Volume (Timezone)'] = poc_volume

            x = self.calculate_vah_val(df_one_hour)
            df_one_hour['VAH (Timezone)'] = x[0]
            df_one_hour['VAL (Timezone)'] = x[1]
            df_one_hour['Resistance'] = x[0] + pips * pips_weightage
            df_one_hour['Support'] = x[1] - pips * pips_weightage
            # self.timezone_poc_dict = [float(df_one_hour['POC_Price (Timezone)'].iloc[0]), 2, str(start_index)]
            self.resistance.append([float(df_one_hour['VAH (Timezone)'].iloc[0]), 2, str(start_index)])
            self.support.append([float(df_one_hour['VAL (Timezone)'].iloc[0]), 2, str(start_index)])
            slices.append(df_one_hour)
            combined_data = pd.concat([combined_data, df_one_hour])


        start_time = "15:00:00"
        start_time = pd.Timestamp(start_time).time()
        mask = (df.index.time == start_time)
        start_indices = df[mask].index

        for start_index in start_indices:
            end = start_index + pd.Timedelta(hours=2)
            end_end = end + pd.Timedelta(minutes=330)
            df_one_hour = df.loc[start_index:end]
            volume_profile = df_one_hour.groupby('Close')['Volume'].sum()
            poc_price = volume_profile.idxmax()
            poc_volume = volume_profile.max()

            df_one_hour['POC_Price (Timezone)'] = poc_price
            df_one_hour['POC_Volume (Timezone)'] = poc_volume
            x = self.calculate_vah_val(df_one_hour)
            df_one_hour['VAH (Timezone)'] = x[0]
            df_one_hour['VAL (Timezone)'] = x[1]
            df_one_hour['Resistance'] = x[0] + pips * pips_weightage
            df_one_hour['Support'] = x[1] - pips * pips_weightage
            #self.timezone_poc_dict = [float(df_one_hour['POC_Price (Timezone)'].iloc[0]), 1, str(start_index)]
            self.resistance.append([float(df_one_hour['VAH (Timezone)'].iloc[0]), 2, str(start_index)])
            self.support.append([float(df_one_hour['VAL (Timezone)'].iloc[0]), 2, str(start_index)])
            slices.append(df_one_hour)
            combined_data = pd.concat([combined_data, df_one_hour])
            while(end < end_end):
                try:
                    combined_data.loc[end, 'Resistance'] = combined_data.loc[end-pd.Timedelta(minutes=1), 'Resistance']
                    combined_data.loc[end, 'Support'] = combined_data.loc[end-pd.Timedelta(minutes=1), 'Support']
                except Exception as e:
                    pass
                end += pd.Timedelta(minutes=1)


        start_time = "22:30:00"
        start_time = pd.Timestamp(start_time).time()
        mask = (df.index.time == start_time)
        start_indices = df[mask].index

        for start_index in start_indices:
            end = start_index + pd.Timedelta(hours=7)
            end_end = end + pd.Timedelta(minutes=90)
            df_one_hour = df.loc[start_index:end]
            volume_profile = df_one_hour.groupby('Close')['Volume'].sum()
            poc_price = volume_profile.idxmax()
            poc_volume = volume_profile.max()

            df_one_hour['POC_Price (Timezone)'] = poc_price
            df_one_hour['POC_Volume (Timezone)'] = poc_volume
            x = self.calculate_vah_val(df_one_hour)
            df_one_hour['VAH (Timezone)'] = x[0]
            df_one_hour['VAL (Timezone)'] = x[1]
            df_one_hour['Resistance'] = x[0] + pips * pips_weightage
            df_one_hour['Support'] = x[1] - pips * pips_weightage
            # self.timezone_poc_dict = [float(df_one_hour['POC_Price (Timezone)'].iloc[0]), 1, str(start_index)]
            self.resistance.append([float(df_one_hour['VAH (Timezone)'].iloc[0]), 2, str(start_index)])
            self.support.append([float(df_one_hour['VAL (Timezone)'].iloc[0]), 2, str(start_index)])
            slices.append(df_one_hour)
            combined_data = pd.concat([combined_data, df_one_hour])
            while(end < end_end):
                try:
                    combined_data.loc[end, 'Resistance'] = combined_data.loc[end-pd.Timedelta(minutes=1), 'Resistance']
                    combined_data.loc[end, 'Support'] = combined_data.loc[end-pd.Timedelta(minutes=1), 'Support']
                except Exception as e:
                    pass
                end += pd.Timedelta(minutes=1)

        combined_data.sort_index(inplace=True)
        self.svp_timezone_data = combined_data

        return combined_data

    def hour_poc(self, df):
        starting = df.index[0]
        ending = df.index[-5]
        combined_data = pd.DataFrame()

        while starting <= ending:
            end_date = starting + pd.Timedelta(hours=1)
            while end_date not in df.index and end_date <= ending:
                end_date += pd.Timedelta(minutes=1)

            df_one_hour = df.loc[starting:end_date]

            volume_profile = df_one_hour.groupby('Close')['Volume'].sum()
            poc_price = volume_profile.idxmax()
            poc_volume = volume_profile.max()

            df_one_hour['POC_Volume'] = poc_volume
            df_one_hour['POC_Price'] = poc_price
            x = self.calculate_vah_val(df_one_hour)
            df_one_hour['VAH'] = x[0]
            df_one_hour['VAL'] = x[1]
            # self.timezone_poc_dict[float(df_one_hour['POC_Price'].iloc[0]), 1, str(starting)]
            self.resistance.append([float(df_one_hour['VAH'].iloc[0]), 1, str(starting)])
            self.support.append([float(df_one_hour['VAL'].iloc[0]), 1, str(starting)])

            combined_data = pd.concat([combined_data, df_one_hour])

            starting = end_date + pd.Timedelta(minutes=1)

        self.svp_hour_data = combined_data
        return combined_data

    def generate_buy_and_sell(self):
        for index, row in self.svp_data.iterrows():
            if pd.isna(row['VAH (Timezone)']):
                self.svp_data.at[index, 'Buy'] = 1 if row['Close'] - row['Resistance'] > 0 else 0
                self.svp_data.at[index, 'Sell'] = 1 if row['Close'] - row['Support'] < 0 else 0

    def combined(self, data):
        self.hour_poc(data)
        self.timezone(data)
        self.svp_timezone_data.drop(columns=['Open', 'High', 'Low', 'Close', 'Volume'], inplace=True)
        self.svp_data = self.svp_hour_data.join(self.svp_timezone_data, sort=True)
        self.svp_data.rename(columns={'POC_Price': 'POC_Price (Hourly)'}, inplace=True)
        self.svp_data.rename(columns={'POC_Volume': 'POC_Volume (Hourly)'}, inplace=True)
        self.svp_data.rename(columns={'VAH': 'VAH (Hourly)'}, inplace=True)
        self.svp_data.rename(columns={'VAL': 'VAL (Hourly)'}, inplace=True)
        self.generate_buy_and_sell()

        return self.svp_data

    def print_dict(self):
        print("Timezone_POC")
        print(self.timezone_poc_dict)
        print("Timezone VAH")
        print(self.timezone_vah_dict)
        print("Timezone VAL")
        print(self.timezone_val_dict)
        print("Hour POC")
        print(self.hour_poc_dict)
        print("Hour VAH")
        print(self.hour_vah_dict)
        print("Hour VAL")
        print(self.hour_val_dict)

    def plot(self, data=None, read=False):
        if read:
            df = pd.read_excel("C:/Users/vedan/PycharmProjects/task/Volume Profile Indicator/Test17.xlsx")
        else:
            df = data
        plt.figure(figsize=(12, 6))
        plt.plot(df.index, df['Close'], label='Close', marker='o')
        plt.plot(df.index, df['VAH (Hourly)'], label='VAH Hourly', linestyle='--')
        plt.plot(df.index, df['VAL (Hourly)'], label='VAL Hourly', linestyle='--')
        plt.plot(df.index, df['POC_Price (Hourly)'], label='POC Price Hourly', linestyle='-.')
        plt.plot(df.index, df['VAH (Timezone)'], label='VAH Timezone', linestyle='--')
        plt.plot(df.index, df['VAL (Timezone)'], label='VAL Timezone', linestyle='--')
        plt.plot(df.index, df['Resistance'], label='VAH Timezone', linestyle='--')
        plt.plot(df.index, df['Support'], label='VAL Timezone', linestyle='--')
        plt.plot(df.index, df['POC_Price (Timezone)'], label='POC Price Timezone', linestyle='-.')
        buy_signal = data[data['Buy'] == 1]
        sell_signal = data[data['Sell'] == 1]
        plt.scatter(buy_signal.index, buy_signal['Close']+0.2, label='Buy Signal', marker="^", color='green', alpha=1, s=50)
        plt.scatter(sell_signal.index, sell_signal['Close']-0.2, label='Sell Signal', marker="v", color='red', alpha=1, s=50)
        plt.fill_between(df.index, df['VAH (Hourly)'], df['VAL (Hourly)'], color='gray', alpha=0.3)
        plt.fill_between(df.index, df['VAH (Timezone)'], df['VAL (Timezone)'], color='blue', alpha=0.3)
        plt.fill_between(df.index, df['Resistance'], df['Support'], color='red', alpha=0.3)
        plt.xlabel('DateTime')
        plt.ylabel('Price')
        plt.title('Close, VAH, VAL, and POC Prices')
        plt.legend()
        plt.grid(True)
        plt.show()

    def backtest(self):
        capital = 10000
        holding = 0
        df = pd.read_excel("Test24.xlsx", sheet_name='Sheet1')
        df.set_index('DateTime', inplace=True)
        for index in df.index:
            if df.loc[index, "Buy"].any() == 1:
                temp = capital * 0.2
                holding += int(temp/df.loc[index, "Close"])
                capital -= df.loc[index, "Close"] * int(temp/df.loc[index, "Close"])
            if df.loc[index, "Sell"].any() == 1:
                if holding > 0:
                    temp = holding * df.loc[index, "Close"]
                    capital += temp
                    holding = 0

        print(f"Capital: {capital}")

    def make_box(self, data):
        self.combined(data)

        support = self.support
        resistance = self.resistance
        support_box = []
        resistance_box = []
        filtered_support_box = []
        filtered_resistance_box = []

        for i in range(0, len(support)):
            temp = 0
            for j in range(i, len(support)):
                if support[i][0] - pips * pips_weightage < support[j][0] < support[i][0] + pips * pips_weightage:
                    temp += support[j][1]
            support[i].append(temp)
            support_box.append(support[i])

        for i in range(0, len(resistance)):
            temp = 0
            for j in range(i, len(resistance)):
                if resistance[i][0] - pips * pips_weightage < resistance[j][0] < resistance[i][0] + pips * pips_weightage:
                    temp += resistance[j][1]
            resistance[i].append(temp)
            resistance_box.append(resistance[i])

        for i in support_box:
            if i[3] >= 5:
                filtered_support_box.append(i)

        for i in resistance_box:
            if i[3] >= 5:
                filtered_resistance_box.append(i)

        return filtered_resistance_box, filtered_support_box


class MT5Wrapper:
    def __init__(self, path=None):
        if path is not None:
            if not mt5.initialize(path):
                print("Initialize() failed, error code =", mt5.last_error())
        else:
            if not mt5.initialize():
                print("Initialize() failed, error code =", mt5.last_error())

    def login(self, account_id, password, server):
        """Login to MT5 account"""
        session = mt5.login(account_id, password=password, server=server)
        if not session:
            print("Login failed, error code =", mt5.last_error())
        else:
            print("Logged in", session)

    def get_latest_close_price(self, symbol, timeframe=mt5.TIMEFRAME_M1):
        """Get the latest close price for a symbol."""
        # Ensure the symbol is available and subscribed
        if not mt5.symbol_select(symbol, True):
            print(f"Failed to select symbol {symbol}")
            return None

        # Get the current date and time
        current_time = datetime.now()

        # Fetch the latest candle
        rates = mt5.copy_rates_from_pos(symbol, timeframe, 0, 1)

        if rates is None or len(rates) == 0:
            print("Error getting historical data, error code =", mt5.last_error())
            return None
        else:
            # Return the close price of the latest candle
            return rates[0]['close']

    def get_quote(self, symbol):
        """Get current quote for a symbol"""
        quote = mt5.symbol_info_tick(symbol)
        time.sleep(2)
        if quote is None:
            print("Error getting quote, error code =", mt5.last_error())
        else:
            print(quote)
            return quote

    def get_historical_data(self, symbol, timeframe, start_time, end_time):
        """Get historical data for a symbol"""
        rates = mt5.copy_rates_range(symbol, timeframe, start_time, end_time)
        if rates is None:
            print("Error getting historical data, error code =", mt5.last_error())
        else:
            return pd.DataFrame(rates)

    def send_order_with_tp(self, symbol, lot, buy, sell, id_position=None, tp=None, sl=None,
                           comment="No specific comment", magic=0):
        # Initialize the bound between MT5 and Python
        mt5.initialize()
        qty = lot

        # Extract filling_mode
        filling_type = mt5.ORDER_FILLING_FOK

        """ OPEN A TRADE """
        if buy and id_position is None:
            request = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": symbol,
                "volume": lot,
                "type": mt5.ORDER_TYPE_BUY,
                "price": mt5.symbol_info_tick(symbol).ask,
                "deviation": 10,
                "magic": magic,
                "comment": comment,
                "type_filling": filling_type,
                "type_time": mt5.ORDER_TIME_GTC
            }
            if tp is not None:
                request["tp"] = tp
            if sl is not None:
                request["sl"] = sl

            result = mt5.order_send(request)
            return result

        if sell and id_position is None:
            request = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": symbol,
                "volume": lot,
                "type": mt5.ORDER_TYPE_SELL,
                "price": mt5.symbol_info_tick(symbol).bid,
                "deviation": 10,
                "magic": magic,
                "comment": comment,
                "type_filling": filling_type,
                "type_time": mt5.ORDER_TIME_GTC
            }
            if tp is not None:
                request["tp"] = tp
            if sl is not None:
                request["sl"] = sl

            result = mt5.order_send(request)
            return result

        """ CLOSE A TRADE """
        if buy and id_position is not None:
            request = {
                "position": id_position,
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": symbol,
                "volume": lot,
                "type": mt5.ORDER_TYPE_SELL,
                "price": mt5.symbol_info_tick(symbol).bid,
                "deviation": 10,
                "magic": magic,
                "comment": comment,
                "type_filling": filling_type,
                "type_time": mt5.ORDER_TIME_GTC
            }
            if tp is not None:
                request["tp"] = tp
            if sl is not None:
                request["sl"] = sl

            result = mt5.order_send(request)
            return result

        if sell and id_position is not None:
            request = {
                "position": id_position,
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": symbol,
                "volume": lot,
                "type": mt5.ORDER_TYPE_BUY,
                "price": mt5.symbol_info_tick(symbol).ask,
                "deviation": 10,
                "magic": magic,
                "comment": comment,
                "type_filling": filling_type,
                "type_time": mt5.ORDER_TIME_GTC
            }
            if tp is not None:
                request["tp"] = tp
            if sl is not None:
                request["sl"] = sl

            result = mt5.order_send(request)
            return result

    def place_order(self, symbol, order_type, volume, price=None, sl=None, tp=None, comment=""):
        """Place an order with optional SL and TP"""
        order_dict = {
            "buy": mt5.ORDER_TYPE_BUY_LIMIT,
            "sell": mt5.ORDER_TYPE_SELL_LIMIT
        }
        order_type = order_dict.get(order_type.lower())
        if order_type is None:
            print("Invalid order type")
            return

        request = {
            "action": mt5.TRADE_ACTION_PENDING,
            "symbol": symbol,
            "volume": volume,
            "type": order_type,
            "price": price,
            "deviation": 20,
            "magic": 100,
            "comment": comment,
            "type_time": mt5.ORDER_TIME_GTC,  # Good till cancel
            "type_filling": mt5.ORDER_FILLING_IOC,
        }

        if price is not None:
            request["price"] = price

        result = mt5.order_send(request)
        time.sleep(2)
        print(result)
        if result.retcode != mt5.TRADE_RETCODE_DONE:
            print("Order failed, retcode =", result.retcode)
        else:
            return result

    def get_available_balance(self):
        """Get available account balance"""
        account_info = mt5.account_info()
        if account_info is None:
            print("Failed to get account balance, error code =", mt5.last_error())
            return None
        else:
            return account_info.balance

    # New function to get symbol information
    def get_symbol_info(self, symbol):
        """Get information about a symbol"""
        info = mt5.symbol_info(symbol)
        if info is None:
            print(f"Failed to get symbol info for {symbol}, error code =", mt5.last_error())
            return None
        else:
            return info

    # New function to calculate the number of lots for a given USD value
    def calculate_lots(self, symbol, usd_amount):
        """Calculate the number of lots for a given USD amount willing to spend on a trade"""
        symbol_info = self.get_symbol_info(symbol)
        # print(symbol_info)
        if symbol_info is None:
            return None

        if not symbol_info.trade_contract_size:
            print(f"Failed to get contract size for {symbol}")
            return None

        price = self.get_latest_close_price(symbol)
        if not price:
            print(f"Failed to get current ask price for {symbol}")
            return None

        one_lot_value = symbol_info.trade_contract_size * price
        lots = usd_amount / one_lot_value
        return lots

    def shutdown(self):
        """Shutdown the MT5 terminal"""
        mt5.shutdown()


if __name__ == "__main__":
    start_time = time.time()

    while True:
        obj = svp()
        wrapper = MT5Wrapper()
        timezone = pytz.timezone("Etc/UTC")
        time_only = (datetime.now() - timedelta(hours=3)).time()
        date_only = (datetime.now() - timedelta(hours=3)).date()
        year = date_only.year
        month = date_only.month
        day = date_only.day

        start = datetime(year, month, day - 3, hour=7, tzinfo=timezone)
        end = datetime(year, month, day-1, hour=10, tzinfo=timezone)
        data = wrapper.get_historical_data("EURUSD", mt5.TIMEFRAME_M1, start, end)


        data = data.rename(columns={'time': 'OpenTime', 'open': 'Open', "high": "High", 'low': 'Low', 'close': 'Close',
                                    'tick_volume': 'Volume'})
        data['OpenTime'] = pd.to_datetime(data['OpenTime'], unit='s')
        data.set_index("OpenTime", inplace=True)
        data.drop(columns=['spread', 'real_volume'], inplace=True)
        lists = obj.make_box(data)


        latest_price = wrapper.get_latest_close_price("EURUSD")
        resistance = lists[0]
        support = lists[1]
        print(resistance)
        temp_resistance = [item for item in resistance if item[0] >= latest_price]
        temp_support = [item for item in support if item[0] <= latest_price]
        try:
            closest_resistance = min(temp_resistance, key=lambda x: abs(float(x[0]) - float(latest_price)))
        except Exception as e:
            closest_resistance = min(resistance, key=lambda x: abs(float(x[0]) - float(latest_price)))

        try:
            closest_support = min(temp_support, key=lambda x: abs(float(x[0]) - float(latest_price)))
        except Exception as e:
            closest_support = min(support, key=lambda x: abs(float(x[0]) - float(latest_price)))

        # closest_resistance = min(resistance, key=lambda x: abs(float(x[0]) - float(latest_price)))
        # closest_support = min(support, key=lambda x: float(x[0]) - float(latest_price))
        # wrapper.login(account_id=5028843863, password="B!Vp1oYx", server="MetaQuotes-Demo")
        sell = closest_resistance[0]
        buy = closest_support[0]
        print(buy)
        print(sell)
        print(latest_price)
        wrapper.place_order("EURUSD", "buy", volume=0.1, price=buy)
        wrapper.place_order("EURUSD", "sell", volume=0.1, price=sell)

        time.sleep(60)

    end_time = time.time()

    print(f"Time taken to execute this program is {end_time-start_time} seconds")