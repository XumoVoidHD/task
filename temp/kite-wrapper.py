import logging
import os
import json
from kiteconnect import KiteConnect
import numpy as np
import pandas as pd
import creds
class Broker:
    def __init__(self,client_id,api_key,secret_key):
        logging.basicConfig(level=logging.DEBUG)
        self.api_key=api_key
        self.secret_key=secret_key
        self.client_id=client_id
        self.kite = KiteConnect(api_key=api_key)
        self.data_file = 'request_token.json'

    def _get_stored_data(self):
        if os.path.exists(self.data_file):
            with open(self.data_file, 'r') as file:
                data = json.load(file)
                return data
        return {}
    def _store_data(self, data):
        with open(self.data_file, 'w') as file:
            json.dump(data, file)
    def _save_keys(self):
        data=self._get_stored_data()
        if self.client_id not in data:
            data[self.client_id] = {'access_token': self.access_token}
        else:
            data[self.client_id]['access_token']=self.access_token
        self._store_data(data)
    def _force_login(self,request_token):
        try:
            data = self.kite.generate_session(request_token, api_secret=self.secret_key)
            print(data)
            self.access_token=str(data["access_token"])
            self.kite.set_access_token(self.access_token)
            self._save_keys()
            print("Logged in successfully")
        except Exception as e:
            logging.error("Login failed: {}".format(str(e)))
    def _login(self):
        stored_request_data = self._get_stored_data()

        if self.client_id in stored_request_data:
            stored_request_token=stored_request_data[self.client_id]["access_token"]
            print("Using stored request token.")
            self.access_token = stored_request_token
            self.kite.set_access_token(self.access_token)
            try:
                self.fetch_orders()
            except:
                login_url=self.kite.login_url()
                print(login_url)
                request_token = input("Enter request token: ")
                self._force_login(request_token)
        else:
            login_url=self.kite.login_url()
            print(login_url)
            request_token = input("Enter request token: ")
            self._force_login(request_token)

    def get_ohlc_data(self,exchange,symbol):
        print("getting ohlc dataa")
        sym=exchange+":"+symbol
        instrument_list=[sym]
        data=self.kite.ohlc(instrument_list)
        values=data[sym]
        instrument_token=values["instrument_token"]
        last_price=values["last_price"]
        ohlc=values["ohlc"]
        return instrument_token,last_price,ohlc
    def place_sl_order(self,symbol,side,qty,limit_trigger,stop):
        if(side=="BUY"):
            opp_transaction_type="SELL"
        else:
            opp_transaction_type="BUY"
        variety=self.kite.VARIETY_REGULAR
        try:
            sl_order_id = self.kite.place_order(
                tradingsymbol=symbol,
                exchange=self.kite.EXCHANGE_NFO,
                transaction_type=opp_transaction_type,
                quantity=qty,
                variety=variety,
                order_type=self.kite.ORDER_TYPE_SLM,
                price=stop,
                trigger_price=limit_trigger,
                product=self.kite.PRODUCT_MIS,
                validity=self.kite.VALIDITY_DAY
            )
            logging.info("Equity Order placed. ID is: {}".format(sl_order_id))
        except Exception as e:
            logging.error("Equity Order placement failed: {}".format(str(e)))
    def place_options_order(self,symbol,transaction_type,qty,trigger_price,is_market=1,limit=0):
        if(transaction_type=="BUY"):
            opp_transaction_type="SELL"
        else:
            opp_transaction_type="BUY"
        if(creds.market_closed==1):
            variety=self.kite.VARIETY_AMO
        else:
            variety=self.kite.VARIETY_REGULAR

        if(is_market):
            ordertype=self.kite.ORDER_TYPE_MARKET
        else:
            ordertype=self.kite.ORDER_TYPE_LIMIT
        try:
            order_id = self.kite.place_order(
                tradingsymbol=symbol,
                exchange=self.kite.EXCHANGE_NFO,
                transaction_type=transaction_type,
                quantity=qty,
                variety=variety,
                order_type=ordertype,
                price=limit,
                #trigger_price=trigger_price,
                product=self.kite.PRODUCT_MIS,
                validity=self.kite.VALIDITY_DAY
            )
            logging.info("Equity Order placed. ID is: {}".format(order_id))
        except Exception as e:
            logging.error("Equity Order placement failed: {}".format(str(e)))
        return order_id
    def place_options_order_combined(self,symbol,transaction_type,qty,trigger_price,is_market=1,limit=0):
        if(transaction_type=="BUY"):
            opp_transaction_type="SELL"
        else:
            opp_transaction_type="BUY"
        if(creds.market_closed==1):
            variety=self.kite.VARIETY_AMO
        else:
            variety=self.kite.VARIETY_REGULAR

        if(is_market):
            ordertype=self.kite.ORDER_TYPE_MARKET
        else:
            ordertype=self.kite.ORDER_TYPE_LIMIT
        try:
            order_id = self.kite.place_order(
                tradingsymbol=symbol,
                exchange=self.kite.EXCHANGE_NFO,
                transaction_type=transaction_type,
                quantity=qty,
                variety=variety,
                order_type=ordertype,
                price=limit,
                trigger_price=trigger_price,
                product=self.kite.PRODUCT_MIS,
                validity=self.kite.VALIDITY_DAY
            )
            logging.info("Equity Order placed. ID is: {}".format(order_id))
        except Exception as e:
            logging.error("Equity Order placement failed: {}".format(str(e)))

        ##sl order

        try:
            sl_order_id = self.kite.place_order(
                tradingsymbol=symbol,
                exchange=self.kite.EXCHANGE_NFO,
                transaction_type=opp_transaction_type,
                quantity=qty,
                variety=variety,
                order_type=self.kite.ORDER_TYPE_SL,
                price=trigger_price,
                trigger_price=trigger_price,
                product=self.kite.PRODUCT_MIS,
                validity=self.kite.VALIDITY_DAY
            )
            logging.info("Equity Order placed. ID is: {}".format(sl_order_id))
        except Exception as e:
            logging.error("Equity Order placement failed: {}".format(str(e)))
        return order_id,sl_order_id
    def modify_sl(self,order_id,limit,trig):
        variety=self.kite.VARIETY_REGULAR
        self.kite.modify_order(variety,order_id,trigger_price=trig,price=limit)
    def cancel_order(self,order_id):
        variety=self.kite.VARIETY_REGULAR
        self.kite.cancel_order(variety,order_id)
    def check_order_status(self,orderid):
        order_history=self.kite.order_history(orderid)
        if str(order_history["status"])=="success":
            data=order_history["dataa"]
            latest_data=data[-1]
            status=latest_data["status"]
            pending_quantity=latest_data["pending_quantity"]
            filled_quantity=latest_data["filled_quantity"]
            print("status:- ",status,"pending quantity:- ",pending_quantity,"filled_quantity:- ",filled_quantity)
            return status

    def get_symbol_info(self,tradingsymbol):
        df_inst = pd.read_csv("https://api.kite.trade/instruments")
        df = df_inst[df_inst['segment'] == "NFO-OPT"]
        df = df[df['tradingsymbol']==tradingsymbol]
        instrument_token = df.instrument_token.values[0]
        tick_size=df.tick_size.values[0]
        tradingsym = df.tradingsymbol.values[0]
        next_expiry=df.expiry.values[0]
        
        return tradingsym,instrument_token,tick_size,next_expiry
    def get_trading_symbol(self,symbol,strike,option_type,expiry_index=0):
        df_inst = pd.read_csv("https://api.kite.trade/instruments")
        df = df_inst[df_inst['segment'] == "NFO-OPT"]
        df = df[df['name']==symbol]
        df['expiry'] = pd.to_datetime(df['expiry'])
        expirylist = list(set(df[['tradingsymbol', 'expiry']].sort_values(by=['expiry'])['expiry'].values))
        expirylist = np.array([np.datetime64(x, 'D') for x in expirylist])
        expirylist = np.sort(expirylist)
        today = np.datetime64('today', 'D') + np.timedelta64(0,'D')
        expirylist = expirylist[expirylist >= today]
        next_expiry = expirylist[expiry_index]
        print("Selected expiry :", next_expiry)
        df = df[(df['expiry'] == next_expiry)]
        RHATM = int((round((strike) / 100) * 100))
        tradingsymbol = df[df['strike'] == RHATM]
        tradingsymbol = tradingsymbol[tradingsymbol['instrument_type'] == option_type]
        print(tradingsymbol)
        instrument_token = tradingsymbol.instrument_token.values[0]
        tick_size=tradingsymbol.tick_size.values[0]
        tradingsym = tradingsymbol.tradingsymbol.values[0]
        
        return tradingsym,instrument_token,tick_size,next_expiry

    def place_equity_order(self, symbol, transaction_type, quantity):
        try:
            order_id = self.kite.place_order(
                tradingsymbol=symbol,
                exchange=self.kite.EXCHANGE_NSE,
                transaction_type=transaction_type,
                quantity=quantity,
                variety=self.kite.VARIETY_AMO,
                order_type=self.kite.ORDER_TYPE_MARKET,
                product=self.kite.PRODUCT_CNC,
                validity=self.kite.VALIDITY_DAY
            )
            logging.info("Equity Order placed. ID is: {}".format(order_id))
        except Exception as e:
            logging.error("Equity Order placement failed: {}".format(str(e)))
    def fetch_orders(self):
        orders = self.kite.orders()
        logging.info("Fetched Orders: {}".format(orders))
        return orders
    def get_position_details(self,trading_symbol):
        data=self.get_positions()
        open_positions = [pos for pos in data['day'] if pos['quantity'] > 0]
        df = pd.DataFrame(open_positions)
        df = df[df['tradingsymbol']==trading_symbol]
        print(df)
        return df
    def get_positions(self):
        positions=self.kite.positions()
        return positions
    def get_instruments(self):
        instruments = self.kite.instruments()
        logging.info("Fetched Instruments: {}".format(instruments))
        return instruments
