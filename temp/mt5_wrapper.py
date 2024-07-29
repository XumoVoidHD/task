from datetime import datetime
import time
import MetaTrader5 as mt5
import pandas as pd

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
        session=mt5.login(account_id, password=password, server=server)
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
            print("Error getting historical dataa, error code =", mt5.last_error())
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
        """Get historical dataa for a symbol"""
        rates = mt5.copy_rates_range(symbol, timeframe, start_time, end_time)
        if rates is None:
            print("Error getting historical dataa, error code =", mt5.last_error())
        else:
            return pd.DataFrame(rates)
    def send_order_with_tp(self,symbol, lot, buy, sell, id_position=None, tp=None, sl=None, comment="No specific comment", magic=0):
        # Initialize the bound between MT5 and Python
        mt5.initialize()
        qty=lot

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
            "buy": mt5.ORDER_TYPE_BUY,
            "sell": mt5.ORDER_TYPE_SELL
        }
        order_type = order_dict.get(order_type.lower())
        if order_type is None:
            print("Invalid order type")
            return

        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": symbol,
            "volume": volume,
            "type": order_type,
            "price": mt5.symbol_info_tick(symbol).ask if order_type == mt5.ORDER_TYPE_BUY else mt5.symbol_info_tick(symbol).bid,
            "sl": sl,
            "tp": tp,
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
        #print(symbol_info)
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
