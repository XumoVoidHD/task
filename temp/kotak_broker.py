from neo_api_client import NeoAPI
import pandas as pd
import requests
import creds
class NeoClientWrapper:
    def __init__(self, consumer_key="", consumer_secret="", environment='prod',
                 access_token=None, neo_fin_key=None):
        self.client = NeoAPI(consumer_key=consumer_key, consumer_secret=consumer_secret,
                             environment=environment)
        self.setup_callbacks()
        self.ltp_dict = {}


    def setup_callbacks(self):
        self.client.on_message = self.on_message
        self.client.on_error = self.on_error
        self.client.on_close = self.on_close
        self.client.on_open = self.on_open


    def on_message(self, message):
            print("Message:", message)

            if 'type' in message and message['type'] == 'quotes' and 'dataa' in message:
                data_list = message['dataa']
                if len(data_list) == 1:
                    data = data_list[0]
                    if 'trading_symbol' in data and 'last_traded_price' in data:
                        print(data['trading_symbol'], data['last_traded_price'])
                        self.ltp_dict[data['trading_symbol']] = data['last_traded_price']
                    else:
                        print("Missing keys in 'dataa' dictionary:", data)
                else:
                    print("Invalid 'dataa' list length:", len(data_list))
            else:
                print("Invalid message format:", message)

    def on_error(self, error_message):
        print("Error:", error_message)

    def on_close(self, message):
        print("Closed:", message)

    def on_open(self, message):
        print("Opened:", message)

    def login(self, mobilenumber=None, pan=None, userid=None, password=None):
        credentials = {"mobilenumber": mobilenumber, "password": password}
        self.client.login(**{k: v for k, v in credentials.items() if v is not None})
        otp=input("Enter Otp received")
        self.session_2fa(otp)
        

    def session_2fa(self, OTP):
        self.client.session_2fa(OTP=OTP)

    def place_order(self, exchange_segment, product, price, order_type, quantity, validity, trading_symbol,
                    transaction_type, amo="NO", disclosed_quantity="0", market_protection="0", pf="N",
                    trigger_price="0", tag=None):
        print("placing orders")
        oid=self.client.place_order(exchange_segment=exchange_segment, product=product, price=price,
                                order_type=order_type, quantity=quantity, validity=validity,
                                trading_symbol=trading_symbol, transaction_type=transaction_type,
                                amo=amo, disclosed_quantity=disclosed_quantity,
                                market_protection=market_protection, pf=pf, trigger_price=trigger_price, tag=tag)
        return oid

    def modify_order(self, order_id, price=None, quantity=None, disclosed_quantity=None,
                     trigger_price=None, validity=None):
        self.client.modify_order(order_id=order_id, price=price, quantity=quantity,
                                 disclosed_quantity=disclosed_quantity, trigger_price=trigger_price,
                                 validity=validity)

    def cancel_order(self, order_id, isVerify=False):
        self.client.cancel_order(order_id=order_id, isVerify=isVerify)

    def order_report(self):
        return self.client.order_report()

    def order_history(self, order_id):
        return self.client.order_history(order_id=order_id)

    def trade_report(self, order_id=None):
        return self.client.trade_report(order_id=order_id)

    def positions(self):
        return self.client.positions()

    def holdings(self):
        return self.client.holdings()

    def limits(self, segment="", exchange="", product=""):
        return self.client.limits(segment=segment, exchange=exchange, product=product)

    def margin_required(self, exchange_segment, price, order_type, product, quantity, instrument_token,
                        transaction_type):
        return self.client.margin_required(exchange_segment=exchange_segment, price=price,
                                           order_type=order_type, product=product, quantity=quantity,
                                           instrument_token=instrument_token, transaction_type=transaction_type)

    def scrip_master(self, exchange_segment=None):
        if exchange_segment:
            return self.client.scrip_master(exchange_segment=exchange_segment)
        else:
            return self.client.scrip_master()

    def search_scrip(self, exchange_segment, symbol=None, expiry=None, option_type=None, strike_price=None):
        return self.client.search_scrip(exchange_segment=exchange_segment, symbol=symbol, expiry=expiry,
                                        option_type=option_type, strike_price=strike_price)

    def quotes(self, instrument_tokens, quote_type=None, isIndex=False, session_token=None, sid=None, server_id=None):
        return self.client.quotes(instrument_tokens=instrument_tokens, quote_type=quote_type, isIndex=isIndex,
                                  session_token=session_token, sid=sid, server_id=server_id)

    def subscribe(self, instrument_tokens, isIndex=False, isDepth=False):
        self.client.subscribe(instrument_tokens=instrument_tokens, isIndex=isIndex, isDepth=isDepth)

    def un_subscribe(self, instrument_tokens, isIndex=False, isDepth=False):
        self.client.un_subscribe(instrument_tokens=instrument_tokens, isIndex=isIndex, isDepth=isDepth)

    def subscribe_to_orderfeed(self):
        self.client.subscribe_to_orderfeed()
    def fetch_token_info(self):
        url = f"{self.base_url}/scripmaster/1.1/filename"
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            # Process the response to extract cash and FNO URLs
            cash_url = response.json()['Success']['cash']
            fno_url = response.json()['Success']['fno']
            cash_df = pd.read_csv(cash_url, sep='|')
            fno_df = pd.read_csv(fno_url, sep='|')
            # Further processing based on your needs
            print("Token info fetched successfully.")
            return cash_df, fno_df
        except Exception as e:
            print(f"Exception when fetching token info: {e}")
            return None, None
        
    def place_oco_order(self,trading_symbol,qty,transaction_type,tp,sl,exchange_segment="nse_cm",product="MIS"):
        if(transaction_type=="B"):
            print(tp,sl)
            market_order=self.place_order(exchange_segment="nse_cm", product="MIS", price="0", order_type="MKT", quantity=qty, validity="DAY", trading_symbol=trading_symbol,
                            transaction_type="B", amo="NO", disclosed_quantity="0", market_protection="0", pf="N",
                            trigger_price="0")
            sl_order=self.place_order(exchange_segment="nse_cm", product="MIS", price=sl, order_type="SL-M", quantity=qty, validity="DAY", trading_symbol=trading_symbol,
                            transaction_type="S", amo="NO", disclosed_quantity="0", market_protection="0", pf="N",
                            trigger_price=sl)
            tp_order=self.place_order(exchange_segment="nse_cm", product="MIS", price=tp, order_type="L", quantity=qty, validity="DAY", trading_symbol=trading_symbol,
                            transaction_type="S", amo="NO", disclosed_quantity="0", market_protection="0", pf="N",
                            trigger_price="0")
            return market_order,sl_order,tp_order
        else:
            print(tp,sl)
            market_order=self.place_order(exchange_segment="nse_cm", product="MIS", price="0", order_type="MKT", quantity=qty, validity="DAY", trading_symbol=trading_symbol,
                            transaction_type="S", amo="NO", disclosed_quantity="0", market_protection="0", pf="N",
                            trigger_price="0")
            sl_order=self.place_order(exchange_segment="nse_cm", product="MIS", price=sl, order_type="SL-M", quantity=qty, validity="DAY", trading_symbol=trading_symbol,
                            transaction_type="B", amo="NO", disclosed_quantity="0", market_protection="0", pf="N",
                            trigger_price=sl)
            tp_order=self.place_order(exchange_segment="nse_cm", product="MIS", price=tp, order_type="L", quantity=qty, validity="DAY", trading_symbol=trading_symbol,
                            transaction_type="B", amo="NO", disclosed_quantity="0", market_protection="0", pf="N",
                            trigger_price="0")
            return market_order,sl_order,tp_order

    
    def logout(self):
        self.client.logout()


"""
kotak=NeoClientWrapper(consumer_key=creds.kotak_consumer_key,consumer_secret=creds.kotak_consumer_secret)
kotak.login(mobilenumber=creds.kotak_mobile_number,password=creds.kotak_password)
print(kotak.client)
try:
    order_details=kotak.place_order(exchange_segment="nse_cm", product="MIS", price="0", order_type="MKT", quantity="1", validity="DAY", trading_symbol="TCS-EQ",
                       transaction_type="B", amo="NO", disclosed_quantity="0", market_protection="0", pf="N",
                       trigger_price="0")
except Exception as e:
    print(e)
print(order_details)
"""