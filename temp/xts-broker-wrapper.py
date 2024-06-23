from datetime import datetime
from models.Connect import XTSConnect
import pandas as pd
import creds
class TradingAPI:
    def __init__(self, api_key, api_secret, client_id, user_id, xts_api_base_url, source):
        self.api_key = api_key
        self.api_secret = api_secret
        self.client_id = client_id
        self.user_id = user_id
        self.xts_api_base_url = xts_api_base_url
        self.source = source
        self.xt = XTSConnect(api_key, api_secret, source,xts_api_base_url)
        self.logged_in = False

    def login(self):
        if not self.logged_in:
            response = self.xt.interactive_login()
            self.logged_in = True
            return response
        else:
            return "Already logged in."
    def get_ohlc_data(self,exchangeInstrumentID):
        current_date_time = datetime.now()
        current_hour=current_date_time.hour
        current_minute=current_date_time.minute-5
        if(current_minute<0):
            current_minute=60+current_minute
            current_hour=current_hour-1
        next_minute=current_date_time.minute+5
        next_hour=current_date_time.hour
        if(next_minute>=60):
            next_minute=next_minute-60
            next_hour=next_hour+1
            #ext_minute,next_hour)
        current_date_time = current_date_time.replace(hour=current_hour, minute=current_minute, second=0, microsecond=0)
        end_date_time=current_date_time.replace(hour=next_hour, minute=next_minute, second=0, microsecond=0)
        if(creds.market_closed):
            current_date_time = current_date_time.replace(day=13,hour=9, minute=0, second=0, microsecond=0)
            end_date_time=current_date_time.replace(hour=15, minute=0, second=0, microsecond=0)
        formatted_date = current_date_time.strftime('%b %d %Y %H%M%S')
        formatted_date2=end_date_time.strftime('%b %d %Y %H%M%S')
        print(formatted_date,formatted_date2)
        response = self.xt.get_ohlc(
        exchangeSegment=self.xt.EXCHANGE_NSEFO,
        exchangeInstrumentID=exchangeInstrumentID,
        startTime=formatted_date,
        endTime=formatted_date2,
        compressionValue=1)
        print("ohlc response",response)
        response=response["result"]["dataReponse"]
        rows = response.split(',')
        data_list = [row.split('|') for row in rows]
        # Create a Pandas DataFrame
        df = pd.DataFrame(data_list, columns=['ts', 'open', 'high', 'low', 'close', 'v1', 'v2','v3'])
        print(df)
        return df
    
    def subscribe_market_Data(self,exchangeInstrumentID):
        instruments = [
        {'exchangeSegment': 2, 'exchangeInstrumentID': exchangeInstrumentID}]
        response = self.xt.get_quote(
    Instruments=instruments,
    xtsMessageCode=1504,
    publishFormat='JSON')
        print('Subscribe :', response)
    def cancel_orders(self,exchangeInstrumentID):
        response = self.xt.cancelall_order(exchangeInstrumentID=exchangeInstrumentID,exchangeSegment=self.xt.EXCHANGE_NSEFO)
        print("Cancel all Orders: ", response)
    def get_balance(self):
        response=self.xt.get_balance(self.client_id)
        print(response)
        balance = response['result']['BalanceList'][0]['limitObject']['marginAvailable']['CashMarginAvailable']
        net_margin_available = response['result']['BalanceList'][0]['limitObject']['RMSSubLimits']['netMarginAvailable']
        MTM = response['result']['BalanceList'][0]['limitObject']['RMSSubLimits']['MTM']
        unrealized_MTM = response['result']['BalanceList'][0]['limitObject']['RMSSubLimits']['UnrealizedMTM']

        return balance,net_margin_available,MTM,unrealized_MTM
    def get_orderbook(self):
        response = self.xt.get_order_book(self.client_id)
        print("Dealer Order Book: ", response)
        return response
    def check_order_status(self,app_order_id):
        order_history=self.xt.get_order_history(app_order_id)
        if ('type' in order_history) and (order_history['type'] == 'success'):
            if order_history['result']:
                last_order = order_history['result'][-1]
                last_order_status = last_order['OrderStatus']
                print("Last Order Status:", last_order_status)
            else:
                print("No orders in the order history.")
                return None
        else:
            print("Order history request failed. ",order_history)
            return None
        return last_order_status
        """
        for order in result_data['result']:
                if order['AppOrderID'] == app_order_id:
                    return order['OrderStatus']
            return 'Order not found'
        """
    def get_option_symbol(self, exchangeSegment, series, symbol, expiryDate, optionType, strikePrice):
        response = self.xt.get_option_symbol(
            exchangeSegment=exchangeSegment,
            series=series,
            symbol=symbol,
            expiryDate=expiryDate,
            optionType=optionType,
            strikePrice=strikePrice)
        return response["result"][0]
    
    def place_order(self,is_market,instrument_id,side,qty,limit,stop,product_type=None):
        if (product_type!=None):
            if(product_type=="MIS"):
                prod_type=self.xt.PRODUCT_MIS
            elif(product_type=="NRML"):
                prod_type=self.xt.PRODUCT_NRML
        else:
            prod_type=self.xt.PRODUCT_MIS

        if(is_market):
            ordertype=self.xt.ORDER_TYPE_MARKET
        else:
            ordertype=self.xt.ORDER_TYPE_LIMIT

        if(side=="BUY"):
            order_side=self.xt.TRANSACTION_TYPE_BUY
        else:
            order_side=self.xt.TRANSACTION_TYPE_SELL

        """Place Order Request"""
        response = self.xt.place_order(
            exchangeSegment=self.xt.EXCHANGE_NSEFO,
            exchangeInstrumentID=instrument_id,
            productType=prod_type,
            orderType=ordertype,
            orderSide=order_side,
            timeInForce=self.xt.VALIDITY_DAY,
            disclosedQuantity=0,
            orderQuantity=qty,
            limitPrice=limit,
            stopPrice=stop,
            orderUniqueIdentifier="454845",
            clientID=self.client_id)
        print("Place Order: ", response)
        # extracting the order id from response
        if response['type'] != 'error':
            OrderID = response['result']['AppOrderID']
        return OrderID
    
    def place_sl_order(self,instrument_id,side,qty,limit_trigger,stop):
        ordertype=self.xt.ORDER_TYPE_STOPLIMIT

        if(side=="BUY"):
            order_side=self.xt.TRANSACTION_TYPE_BUY
            opp_order_side=self.xt.TRANSACTION_TYPE_SELL
        else:
            order_side=self.xt.TRANSACTION_TYPE_SELL
            opp_order_side=self.xt.TRANSACTION_TYPE_BUY

        """Place Order Request"""
        response = self.xt.place_order(
            exchangeSegment=self.xt.EXCHANGE_NSEFO,
            exchangeInstrumentID=instrument_id,
            productType=self.xt.PRODUCT_MIS,
            orderType=self.xt.ORDER_TYPE_STOPLIMIT,
            orderSide=opp_order_side,
            timeInForce=self.xt.VALIDITY_DAY,
            disclosedQuantity=0,
            orderQuantity=qty,
            limitPrice=stop,
            stopPrice=limit_trigger,
            orderUniqueIdentifier="454845",
            clientID=self.client_id)
        print("SL Place Order: ", response)
        # extracting the order id from response
        if response['type'] != 'error':
            OrderID = response['result']['AppOrderID']
        return OrderID
    def place_combined_order2(self,is_market,instrument_id,side,qty,limit,stop,tp):
        
        instrument_id=int(instrument_id)
        if(is_market):
            ordertype=self.xt.ORDER_TYPE_MARKET
        else:
            ordertype=self.xt.ORDER_TYPE_LIMIT

        if(side=="BUY"):
            order_side=self.xt.TRANSACTION_TYPE_BUY
            opp_order_side=self.xt.TRANSACTION_TYPE_SELL
        else:
            order_side=self.xt.TRANSACTION_TYPE_SELL
            opp_order_side=self.xt.TRANSACTION_TYPE_BUY

        """Place Order Request"""
        response = self.xt.place_order(
            exchangeSegment=self.xt.EXCHANGE_NSEFO,
            exchangeInstrumentID=instrument_id,
            productType=self.xt.PRODUCT_MIS,
            orderType=ordertype,
            orderSide=order_side,
            timeInForce=self.xt.VALIDITY_DAY,
            disclosedQuantity=0,
            orderQuantity=qty,
            limitPrice=limit,
            stopPrice=stop,
            orderUniqueIdentifier="454845",
            clientID=self.client_id)
        print("Place Order: ", response)
        # extracting the order id from response
        if response['type'] != 'error':
            OrderID = response['result']['AppOrderID']

        print("result response",response['result'])

        response = self.xt.place_order(
            exchangeSegment=self.xt.EXCHANGE_NSEFO,
            exchangeInstrumentID=instrument_id,
            productType=self.xt.PRODUCT_MIS,
            orderType=self.xt.ORDER_TYPE_STOPLIMIT,
            orderSide=opp_order_side,
            timeInForce=self.xt.VALIDITY_DAY,
            disclosedQuantity=0,
            orderQuantity=qty,
            limitPrice=stop,
            stopPrice=stop,
            orderUniqueIdentifier="454845",
            clientID=self.client_id)
        print("SL Place Order: ", response)


        # extracting the order id from response
        if response['type'] != 'error':
            SL_OrderID = response['result']['AppOrderID']
            print("SL Order Id: ", SL_OrderID)
        TP_OrderID=0
        if(tp!=0):
            response = self.xt.place_order(
                exchangeSegment=self.xt.EXCHANGE_NSEFO,
                exchangeInstrumentID=instrument_id,
                productType=self.xt.PRODUCT_MIS,
                orderType=self.xt.ORDER_TYPE_LIMIT,
                orderSide=opp_order_side,
                timeInForce=self.xt.VALIDITY_DAY,
                disclosedQuantity=0,
                orderQuantity=qty,
                limitPrice=tp,
                stopPrice=stop,
                orderUniqueIdentifier="454845",
                clientID=self.client_id)
            print("TP Place Order: ", response)


            # extracting the order id from response
            if response['type'] != 'error':
                TP_OrderID = response['result']['AppOrderID']

            print("TP Order Id: ", TP_OrderID)

        return OrderID,TP_OrderID,SL_OrderID
    def get_all_open_positions(self):
        data=self.xt.get_position_netwise(self.client_id)

        filtered_positions = [position for position in data['result']['positionList'] if int(position['Quantity']) != 0]

        # Identify trades needed to square off these positions
        trades_to_square_off = []

        for position in filtered_positions:
            exchange_instrument_id = position['ExchangeInstrumentId']
            product_type = position['ProductType']
            quantity = int(position['Quantity'])
            
            if quantity > 0:
                # Need to sell to square off
                trade = {'exchange_instrument_id': exchange_instrument_id, 'action': 'SELL', 'quantity': quantity,'product_type': product_type}
                trades_to_square_off.append(trade)
            elif quantity < 0:
                # Need to buy to square off
                trade = {'exchange_instrument_id': exchange_instrument_id, 'action': 'BUY', 'quantity': abs(quantity),'product_type': product_type}
                trades_to_square_off.append(trade)

        return trades_to_square_off
    def place_combined_order(self,is_market,instrument_id,side,qty,limit,stop,tp,tick_size):
        instrument_id=int(instrument_id)
        if(is_market):
            ordertype=self.xt.ORDER_TYPE_MARKET
        else:
            ordertype=self.xt.ORDER_TYPE_LIMIT

        if(side=="BUY"):
            order_side=self.xt.TRANSACTION_TYPE_BUY
            opp_order_side=self.xt.TRANSACTION_TYPE_SELL
        else:
            order_side=self.xt.TRANSACTION_TYPE_SELL
            opp_order_side=self.xt.TRANSACTION_TYPE_BUY

        """Place Order Request"""
        response = self.xt.place_order(
            exchangeSegment=self.xt.EXCHANGE_NSEFO,
            exchangeInstrumentID=instrument_id,
            productType=self.xt.PRODUCT_MIS,
            orderType=ordertype,
            orderSide=order_side,
            timeInForce=self.xt.VALIDITY_DAY,
            disclosedQuantity=0,
            orderQuantity=qty,
            limitPrice=limit,
            stopPrice=stop,
            orderUniqueIdentifier="454845",
            clientID=self.client_id)
        print("Place Order: ", response)
        # extracting the order id from response
        if response['type'] != 'error':
            OrderID = response['result']['AppOrderID']
            status=self.check_order_status(OrderID)
            print("order status is",status)
            if(status=="Filled"):
                print("order filled")
        else:
            print("result response",response['result'])
        stop=float(stop)
        if(side=="BUY"):
            lmt=stop-(stop*creds.trigger_perc/100)
        else:
            lmt=stop+(stop*creds.trigger_perc/100)
        lmt=round(round(lmt / tick_size) * tick_size,2)
        lmt = ("{:.2f}".format(lmt))
        print("value of trigger for sl is",lmt)

        response = self.xt.place_order(
            exchangeSegment=self.xt.EXCHANGE_NSEFO,
            exchangeInstrumentID=instrument_id,
            productType=self.xt.PRODUCT_MIS,
            orderType=self.xt.ORDER_TYPE_STOPLIMIT,
            orderSide=opp_order_side,
            timeInForce=self.xt.VALIDITY_DAY,
            disclosedQuantity=0,
            orderQuantity=qty,
            limitPrice=str(lmt),
            stopPrice=str(stop),
            orderUniqueIdentifier="454845",
            clientID=self.client_id)
        print("SL Place Order: ", response)


        # extracting the order id from response
        if response['type'] != 'error':
            SL_OrderID = response['result']['AppOrderID']
            print("SL Order Id: ", SL_OrderID)
        TP_OrderID=0
        if(tp!=0):
            response = self.xt.place_order(
                exchangeSegment=self.xt.EXCHANGE_NSEFO,
                exchangeInstrumentID=instrument_id,
                productType=self.xt.PRODUCT_MIS,
                orderType=self.xt.ORDER_TYPE_LIMIT,
                orderSide=opp_order_side,
                timeInForce=self.xt.VALIDITY_DAY,
                disclosedQuantity=0,
                orderQuantity=qty,
                limitPrice=tp,
                stopPrice=stop,
                orderUniqueIdentifier="454845",
                clientID=self.client_id)
            print("TP Place Order: ", response)


            # extracting the order id from response
            if response['type'] != 'error':
                TP_OrderID = response['result']['AppOrderID']

            print("TP Order Id: ", TP_OrderID)

        return OrderID,TP_OrderID,SL_OrderID
    
    def modify_sl_order(self,OrderID,qty,stop,trigger):
        """Modify Order Request"""
        response = self.xt.modify_order(
            appOrderID=OrderID,
            modifiedProductType=self.xt.PRODUCT_MIS,
            modifiedOrderType=self.xt.ORDER_TYPE_STOPLIMIT,
            modifiedOrderQuantity=qty,
            modifiedDisclosedQuantity=0,
            modifiedLimitPrice=stop,
            modifiedStopPrice=trigger,
            modifiedTimeInForce=self.xt.VALIDITY_DAY,
            orderUniqueIdentifier="454845",
            clientID=self.client_id
        )
        print("Modify Order: ", response)
        if response['type'] != 'error':
            SL_OrderID = response['result']['AppOrderID']
            print("SL Order Id: ", SL_OrderID)
    def logout(self):
        if self.logged_in:
            response = self.xt.interactive_logout(clientID=self.client_id)
            self.logged_in = False
            return "Logged out."
        else:
            return "Not logged in."


