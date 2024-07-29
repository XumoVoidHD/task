from datetime import datetime, timedelta
import threading
import time
import requests
import creds
import pandas as pd
import concurrent.futures
import pyotp
from SmartApi import SmartConnect
import calendar,os
from custom_logger import logger_f

from rate_limiter import RateLimiter

lock = threading.Lock()
class Angel_Broker:
    def __init__(self) -> None:
        self.rate_limiter = RateLimiter(rate=3, per=1)
        self.trade_list=[]
        self.ORDERS=[]
        self.tick_size={}
        self.sl_order_ids={}
        self.token_info=pd.read_excel("alltokens.xlsx")
        pass    
    def download_symbol_data(self):
        url = "https://margincalculator.angelbroking.com/OpenAPI_File/files/OpenAPIScripMaster.json"
        d = requests.get(url).json()
        token_df = pd.DataFrame.from_dict(d)
        token_df["expiry"] = pd.to_datetime(token_df["expiry"])
        token_df = token_df.astype({"strike":float})
        token_df.to_excel("alltokens.xlsx")
        df=token_df
        self.token_info= df[(df['exch_seg']=="NFO") & (df["instrumenttype"]==("OPTIDX" or "OPTSTK")) & ((df["name"]==("BANKNIFTY")) | (df["name"]==("MIDCPNIFTY")) | (df["name"]==("FINNIFTY")) | (df["name"]==("NIFTY")))]
        print("token_info saved")
        print(self.token_info)
        self.token_info.to_excel("tokens.xlsx")
    def login(self):
        attempts = 10
        while attempts > 0:
            attempts = attempts-1
            qrOtp = creds.qrOtp
            totp = pyotp.TOTP(qrOtp)
            totp = totp.now()
            obj = SmartConnect(api_key = creds.API_KEY)
            data = obj.generateSession(creds.USER_NAME,creds.PWD,totp)
            print(data)
            self.refresh_token = data['dataa']['refreshToken']
            if data['status']:
                print("logged in successfully")
                return obj
            time.sleep(2)
        return obj
    def orderbook(self,sym,token,type,qty):
        new_dict = {"variety": str("NORMAL"), 
                    "tradingsymbol" : str(sym),
                    "symboltoken" : str(token),
                    "transactiontype": str(type), 
                    "exchange": str("NSE"),
                    "ordertype": str("MARKET"), 
                    "producttype": str("INTRADAY"),
                    "duration": str("DAY"), 
                    "price": str("0"),
                    "quantity": str(qty),
                    "triggerprice": str("0")}
        
        self.trade_list.append(new_dict)
    def get_ltp(self,share,token_id,exchange="NSE"):
        ltp=self.obj.ltpData(exchange,share,token_id)["dataa"]
        print(ltp)
        ltp=ltp["ltp"]
        return ltp
    def place_sl(self, symbol, symboltoken, quantity, direction, fill_price, sl_price, reversal_perc):
        # Place initial SL order
        if direction.lower() == 'buy':
            opp_direction="SELL"
        else:
            opp_direction="BUY"
        new_dict = {
            "variety": "STOPLOSS",
            "tradingsymbol": symbol,
            "symboltoken": symboltoken,
            "transactiontype": opp_direction,
            "exchange": "NSE",
            "ordertype": "STOPLOSS_MARKET",
            "producttype": "INTRADAY",
            "duration": "DAY",
            "price": str("0"),
            "quantity": quantity,
            "triggerprice": str(sl_price)
        }
        #limit_orderid = self.obj.placeOrderFullResponse(new_dict)
        #print("stoploss order placed successfully:-",limit_orderid)
        #limit_orderid=limit_orderid['dataa']['orderid']
    def place_sl_and_trail(self, symbol, symboltoken, quantity, direction, fill_price, sl_price, reversal_perc):
        print(fill_price)
        # Place initial SL order
        if direction.lower() == 'buy':
            opp_direction="SELL"
        else:
            opp_direction="BUY"
        new_dict = {
            "variety": "STOPLOSS",
            "tradingsymbol": symbol,
            "symboltoken": symboltoken,
            "transactiontype": opp_direction,
            "exchange": "NSE",
            "ordertype": "STOPLOSS_MARKET",
            "producttype": "INTRADAY",
            "duration": "DAY",
            "price": str("0"),
            "quantity": quantity,
            "triggerprice": str(sl_price)
        }
        self.rate_limiter.wait() 
        limit_orderid = self.obj.placeOrderFullResponse(new_dict)
        print("stoploss order placed successfully:-",sl_price,limit_orderid)
        limit_orderid=limit_orderid['dataa']['orderid']
        # Tr
        # ailing SL logic
        while True:
            self.rate_limiter.wait() 
            close = self.get_ltp(symbol, symboltoken)
            print("close price:-",close)
            # Determine the new SL price based on the reversal percentage
            if direction.lower() == "buy":
                print("calculating sl for buy")
                new_sl_price = close - (close * reversal_perc / 100)
                price_check=close + (close * reversal_perc / 100)
            else:  # direction == "SELL"
                print("calculating sl for sell")
                new_sl_price = close + (close * reversal_perc / 100)
                price_check=close - (close * reversal_perc / 100)
            print("new_sl_price",new_sl_price)
            tick_size=self.tick_size[symbol]
            print("tick_size",tick_size)
            num_ticks = int(new_sl_price / tick_size)
            print("num ticks",num_ticks)
            # Adjust SL to be a multiple of the tick size
            new_sl_price = num_ticks * tick_size
            new_sl_price=round(new_sl_price,2)
            print("precised sl price",new_sl_price)
            # Check conditions to update SL: new SL must be higher than old SL for BUY, lower for SELL
            if (direction == "BUY" and new_sl_price > fill_price and new_sl_price>sl_price) or (direction == "SELL" and new_sl_price < fill_price and new_sl_price<sl_price):
                # Modify the existing SL order with the new SL price
                #modify_dict = new_dict.copy()
                modify_dict = {
                    "variety": "STOPLOSS",
                    "orderid": limit_orderid,
                    "ordertype": "STOPLOSS_MARKET",
                    "producttype": "INTRADAY",
                    "duration": "DAY",
                    "price": str(new_sl_price),
                    "quantity": quantity,
                    "tradingsymbol": symbol,
                    "symboltoken": symboltoken,
                    "transactiontype": opp_direction,
                    "exchange": "NSE",
                    "triggerprice": str(new_sl_price)
                }
                #modify_dict["orderid"]=str(limit_orderid)
                modify_result = self.obj.modifyOrder(modify_dict)
                if str(modify_result["status"])=="True":
                    print(f"stoploss trailed for {symbol} at {new_sl_price}")
                else:
                    print("error trailing sl")
                    print(modify_result)
                # Update the SL price for the next iteration
                sl_price = new_sl_price
            import time
            time.sleep(creds.wait_time_for_ts)  # Adjust sleep time as necessary


    def fetch_and_place_limit_sl_orders(self):
        order_ids=self.ORDERS
        order_data = self.obj.orderBook()['dataa']
        df_orders = pd.DataFrame(order_data)
        
        # Filter orders by provided order IDs
        filtered_orders = df_orders[df_orders['orderid'].isin(order_ids)]
        
        orders_placed_this_second = 0
        time_last_order = time.time()

        # Process each order to place SL order
        for index, order in filtered_orders.iterrows():
            

            average_price = order['averageprice']
            direction = order['transactiontype']
            tradingsymbol = order['tradingsymbol']
            symboltoken = order["symboltoken"]
            quantity = order["quantity"]
            
            reversal_perc = self.symbol_params[tradingsymbol]["reversal_perc"]
            # Determine SL price based on direction
            sl_price_adjustment = average_price * (self.symbol_params[tradingsymbol]["stoploss_perc"] / 100)
            sl_price = average_price - sl_price_adjustment if direction.lower() == 'buy' else average_price + sl_price_adjustment
            tick_size = self.tick_size[tradingsymbol]
            num_ticks = round(sl_price / tick_size)
            sl_price = num_ticks * tick_size  # Adjust SL to be a multiple of the tick size

            sl_order_thread = threading.Thread(target=self.place_sl_and_trail, args=(tradingsymbol, symboltoken, quantity, direction, average_price, sl_price, reversal_perc))
            
            sl_order_thread.start()

            orders_placed_this_second += 1
            if orders_placed_this_second == 1:
                time_last_order = time.time()  
    def checkorderstatus(self,obj):
        orderbook=obj.orderBook()['dataa']
        if(len(orderbook)!=0):

            new = pd.DataFrame(orderbook)
            first_column = new.pop('averageprice')
            new.insert(0, 'averageprice', first_column)
            first_column = new.pop('orderstatus')
            new.insert(0, 'orderstatus', first_column)
            first_column = new.pop('unfilledshares')
            new.insert(0, 'unfilledshares', first_column)
            first_column = new.pop('lotsize')
            new.insert(0, 'lotsize', first_column)
            first_column = new.pop('transactiontype')
            new.insert(0, 'transactiontype', first_column)
            first_column = new.pop('tradingsymbol')
            new.insert(0, 'tradingsymbol', first_column)

            unf=new[new['unfilledshares'] > str(0)]
            sts=new['orderstatus'].to_list()
            mylist = list(set(sts))

            print("orderbook exporting......")
            
            with pd.ExcelWriter(f"orderbook.xlsx") as writer:
                unf.to_excel(writer,sheet_name='UnFilled')
                for i in mylist:
                    status=new[new['orderstatus'] == str(i)]
                    status.to_excel(writer,sheet_name=str(i))
                new.to_excel(writer, sheet_name='ALL')
            print(f"orderbook exported successfully")
        else:
            print("Empty OrderBook")
    def mul_order(self,obj,trade_list):

        def place_order(orderparams):

            try:
                with lock:
                    orderID = obj.placeOrder(orderparams)
                print("The order id is: {}".format(orderID))
                self.ORDERS.append(orderID)
            except Exception as e:  
                time.sleep(1) 
                try:
                    with lock:
                        orderID = obj.placeOrder(orderparams)
                    print("The order id is: {}".format(orderID))
                    self.ORDERS.append(orderID)
                except Exception as e: 
                    time.sleep(1)
                    try:
                        with lock:
                            orderID = obj.placeOrder(orderparams)
                        self.ORDERS.append(orderID)
                        print("The order id is: {}".format(orderID))
                    except Exception as e:
                        print("Order placement failed: {}".format(e))
        def place_multiple_orders(tradeList):
            with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
                executor.map(place_order, tradeList)
        start = datetime.now()
        place_multiple_orders(trade_list)
        end = datetime.now()
        print("orders sent to exchange in",end - start)
    def gettokenid(self,sym):
        print("searching ",sym)
        df=self.token_info
        token=df[(df['symbol']==sym)]
        print("sym=",sym)
        print("token",token["token"].iloc[0])
        return token["token"].iloc[0],token["tick_size"].iloc[0]
    def save_dataframe_to_daily_folder(self,df):
        """
        Saves a DataFrame to a daily folder within a trades folder in the current working directory.
        
        Parameters:
        - df (pd.DataFrame): The DataFrame to save.
        """
        # Use the current working directory as the base path
        base_path = os.getcwd()
        
        # The rest of the function remains the same
        storage_path = os.path.join(base_path, "storage")
        trades_path = os.path.join(storage_path, "trades")
        os.makedirs(trades_path, exist_ok=True)
        
        today_str = datetime.now().strftime('%Y-%m-%d')
        daily_folder_path = os.path.join(trades_path, today_str)
        os.makedirs(daily_folder_path, exist_ok=True)
        
        file_path = os.path.join(daily_folder_path, "trades_data.csv")
        df.to_csv(file_path, index=False)
        print(f"DataFrame saved to {file_path}")
    def wait_until(self,target_time):
        """
        Wait until a specific target time.
        
        Parameters:
        - target_time (str): The target time in the format 'HH:MM', e.g., '14:30'
        """
        print("Wait until",target_time)
        # Convert target_time string to a datetime object for today
        now = datetime.now()
        target_hour, target_minute,target_seconds = map(int, target_time.split(':'))
        target_datetime = datetime(now.year, now.month, now.day, target_hour, target_minute)

        # If the target time is already passed for today, set it for the next day
        if now > target_datetime:
            return True
            #return False
        
        # Loop until the current time is greater than or equal to the target time
        while datetime.now() < target_datetime:
            time.sleep(1)  # Sleep for a short period to avoid busy waiting

        print(f"Reached the target time: {target_time}")
        return True
    def main(self):
        self.obj=self.login()
        self.margin=self.obj.rmsLimit()
        self.net_balance=self.margin["dataa"]["net"]
        print("margin",self.net_balance)
        self.input=pd.read_excel("input.xlsx")
        no_of_orders=len(self.input)
        print(no_of_orders)
        #orders_by_time = self.input.groupby('TIME').apply(lambda x: x[['SHARE', 'Direction', 'Reversal_perc','Stoploss_perc','Atr']].to_dict('records')).to_dict()
        orders_by_time = {time: group[['SHARE', 'Direction', 'Reversal_perc', 'Stoploss_perc','stock_margin']].to_dict('records') for time, group in self.input.groupby('TIME')}
        print("dict",orders_by_time)
        self.symbol_params={}
        for time, orders in orders_by_time.items():
            if(not self.wait_until(str(time))):
                continue
            print(f"Placing orders for time {time}:")
            for order in orders:
                share = order['SHARE']
                direction = order['Direction']
                reversal_perc = order['Reversal_perc']
                stoploss_perc = order['Stoploss_perc']
                stock_margin=order['stock_margin']
                self.symbol_params[share] = {'reversal_perc': reversal_perc, 'stoploss_perc': stoploss_perc}

                #atr = order['Atr']
                try:
                    order["Token_id"],tick_size=self.gettokenid(share)
                except Exception as e:
                    print(e)
                    continue
                print("tick size for ",share,"is",tick_size)
                self.tick_size[share]=(tick_size/100)
                token_id=order["Token_id"]
                ltp=self.obj.ltpData("NSE",share,token_id)["dataa"]["close"]
                #bal=(float(self.net_balance)*creds.margin)/no_of_orders
                qty=int(stock_margin/ltp)
                print(f"Order details - SHARE: {share}, Direction: {direction}, Reversal_perc: {reversal_perc}, Stoploss_perc: {stoploss_perc}, qty:{qty}")
                
                self.orderbook(share,token_id,direction,qty)
            
            tl=pd.DataFrame(self.trade_list)
            if(len(tl)>0):
                tl['rank'] = tl.groupby(['tradingsymbol','quantity', 'transactiontype']).cumcount()
                tl=tl.sort_values(['tradingsymbol', 'rank'])
                #tl.to_csv(f"{n}t.csv")
                tl.drop("rank", axis=1, inplace=True)
                creds.trade_list= tl.to_dict('records')
            self.mul_order(self.obj,self.trade_list)
            self.save_dataframe_to_daily_folder(pd.DataFrame(self.trade_list))
            self.fetch_and_place_limit_sl_orders()
logger_f("main")
ab=Angel_Broker()
ab.main()