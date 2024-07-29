import math
from ib_insync import IB, Stock, Forex, util, MarketOrder
#import creds
from datetime import datetime
import random
import pytz
import time
from ib_insync import MarketOrder, LimitOrder, StopOrder, Order

timeZ_Ny = pytz.timezone('America/New_York')

class IBWrapper:
    def __init__(self,port,i):
        self.ib = IB()
        self.counter = 1
        self.connect(port)
        self.i=i
    def connect(self,port):
        self.ib = self.login(port)
        
    def disconnect(self):
        self.ib.disconnect()
    def get_account_balance(self):
        """
        Get the account balance information.
        """
        account_balance = self.ib.accountValues()
        for av in account_balance:
            if av.tag == 'AvailableFunds':
                print("Account Balance:-",float(av.value))
                return float(av.value)
    def get_account_summary(self):
        return self.ib.accountSummary()
        
    def get_positions(self):
        return self.ib.positions()
    def place_market_order(self,contract,qty,side):
        buy_order = MarketOrder(side, qty)
        buy_trade = self.ib.placeOrder(contract, buy_order)
        print("waiting for order to be placed")
        #while not buy_trade.isDone():
        #self.ib.sleep(1)
        # Get the fill price of the buy order
        print("order placed successfully")
        fill_price = buy_trade.orderStatus.avgFillPrice
        print(fill_price)
        print(buy_trade)
        return buy_trade,fill_price
    def place_limit_order_at_mid_price(self, contract, qty, side,take_profit_price, stop_loss_price,cashqty=0):
        """
        Place a limit order at the mid price between the current bid and ask.

        Parameters:
        - contract: The contract object to trade.
        - qty: Quantity of the contract to trade.
        - side: 'BUY' or 'SELL'

        Returns:
        - trade: The trade object returned by placing the order.
        - mid_price: The mid price at which the limit order was placed.
        """
        # Request market dataa
        market_data = self.ib.reqMktData(contract, '', False, False)
        self.ib.sleep(2)  # Wait a bit for the market dataa to update

        # Calculate mid price
        if market_data.bid and market_data.ask:
            mid_price = (market_data.bid + market_data.ask) / 2
            print(f"Mid price calculated: {mid_price}")
        else:
            print("Could not fetch bid and ask prices to calculate mid price.Placing market orders")
            self.place_oco_order(contract,qty,side,take_profit_price,stop_loss_price,cashqty)
        contract_details = self.ib.reqContractDetails(contract)
        min_tick = contract_details[0].minTick
        take_profit_price=self.get_valid_precision(take_profit_price,min_tick)
        stop_loss_price=self.get_valid_precision((stop_loss_price-min_tick),min_tick)
        mid_price=self.get_valid_precision(mid_price,min_tick)
        print("precised mid price is",mid_price)
        # Place limit order at mid price
        limit_order = LimitOrder(side, qty, mid_price)
        market_trade = self.ib.placeOrder(contract, limit_order)
        print(f"Placing limit order at mid price: {mid_price}")
        while not market_trade.isDone():
            self.ib.sleep(1)  # Wait for the market order to complete
        
        print("Market order placed successfully.")
        fill_price = market_trade.orderStatus.avgFillPrice
        print(f"Fill price: {fill_price}")
        
        # Prepare the OCO orders
        # Inverting side for the OCO orders based on the initial market order
        oco_side = "SELL" if side.upper() == "BUY" else "BUY"
        
        # Create take profit limit order
        take_profit_order = LimitOrder(oco_side, qty, take_profit_price)
        take_profit_order.orderType = 'LMT'
        take_profit_order.tif = 'GTC'  # Good-Til-Cancelled
        
        # Create stop loss order
        stop_loss_order = StopOrder(oco_side, qty, stop_loss_price)
        stop_loss_order.orderType = 'STP'
        stop_loss_order.tif = 'GTC'  # Good-Til-Cancelled
        
        # Set the OCO order ID
        ocoId = (self.i*10000)+self.counter
        self.counter += 1
        take_profit_order.ocaGroup = f"OCO_{ocoId}"
        stop_loss_order.ocaGroup = f"OCO_{ocoId}"
        take_profit_order.ocaType = 1  # Cancel all remaining orders in the group when one executes
        stop_loss_order.ocaType = 1
        
        # Place the OCO orders
        tp_trade = self.ib.placeOrder(contract, take_profit_order)
        sl_trade = self.ib.placeOrder(contract, stop_loss_order)
        
        print("OCO orders placed.")
        return market_trade,tp_trade, sl_trade
    def count_digits_before_decimal(self,number):
        if isinstance(number, (int, float)):
            str_number = str(number)
            if '.' in str_number:
                digits_before_decimal = len(str_number.split('.')[0])
                digits_after_decimal = len(str_number.split('.')[1])
                return digits_before_decimal,digits_after_decimal
            else:
                return len(str_number),0
        else:
            raise ValueError("Input must be an integer or a float")

    def get_valid_precision(self,price: float, min_tick: float) -> float:
        """
        Convert the price into a valid tick size with precision\n
        """
        print("price:-",price,"min_tick:-",min_tick)

        valid_price = int(price / min_tick) * min_tick
        print("valid price 1",valid_price)
        #digits,decimals=self.count_digits_before_decimal(min_tick)
        #valid_price=round(valid_price,decimals)
        print("valid price 2",valid_price)

        return valid_price
    def floor_decimal(self,value, decimals):
        factor = 10 ** decimals
        return math.floor(value * factor) / factor
    def get_valid_precision_sl(self,price: float, min_tick: float) -> float:
        """
        Convert the price into a valid tick size with precision\n
        """
        print("price:-",price,"min_tick:-",min_tick)
        valid_price = int(price / min_tick) * min_tick
        print("valid price 1",valid_price)
        digits,decimals=self.count_digits_before_decimal(min_tick)
        valid_price=self.floor_decimal(valid_price,decimals)
        print("valid price 2",valid_price)

        return valid_price
    def place_oco_order_limit(self, contract, qty, side,limit_price, take_profit_price, stop_loss_price):
        """
        Places an OCO order consisting of a take profit and a stop loss order
        following a market order execution.
        
        Parameters:
        - contract: The contract object to trade.
        - qty: Quantity of the contract to trade.
        - side: Buy or Sell for the initial market order.
        - take_profit_price: Price level to take profit.
        - stop_loss_price: Price level to stop loss.
        """
        # Place the initial market order
        limit_order = LimitOrder(side, qty, limit_price)
        market_trade = self.ib.placeOrder(contract, limit_order)
        print(f"Placing limit order at mid price: {limit_price}")
        
        #while not market_trade.isDone():
        #    self.ib.sleep(1)  # Wait for the market order to complete
        
        print("Market order placed successfully.")
        fill_price = market_trade.orderStatus.avgFillPrice
        print(f"Fill price: {fill_price}")
        
        # Prepare the OCO orders
        # Inverting side for the OCO orders based on the initial market order
        oco_side = "SELL" if side.upper() == "BUY" else "BUY"
        
        # Create take profit limit order
        take_profit_order = LimitOrder(oco_side, qty, take_profit_price)
        take_profit_order.orderType = 'LMT'
        take_profit_order.tif = 'GTC'  # Good-Til-Cancelled
        
        # Create stop loss order
        stop_loss_order = StopOrder(oco_side, qty, stop_loss_price)
        stop_loss_order.orderType = 'STP'
        stop_loss_order.tif = 'GTC'  # Good-Til-Cancelled
        random_id = random.randint(0, 9999)
        # Set the OCO order ID
        ocoId = ((self.i*10000)+self.counter)
        self.counter += 1
        take_profit_order.ocaGroup = f"OCO_{ocoId}"
        stop_loss_order.ocaGroup = f"OCO_{ocoId}"
        take_profit_order.ocaType = 1  # Cancel all remaining orders in the group when one executes
        stop_loss_order.ocaType = 1
        
        # Place the OCO orders
        tp_trade = self.ib.placeOrder(contract, take_profit_order)
        sl_trade = self.ib.placeOrder(contract, stop_loss_order)
        self.ib.sleep(2)
        print("tp trade",tp_trade)
        print("sl trade",sl_trade)
        print(f"TP Order Status: {tp_trade.orderStatus.status}, SL Order Status: {sl_trade.orderStatus.status}")
        print("OCO orders placed.")
        return market_trade,tp_trade, sl_trade
    def place_oco_order(self, contract, qty, side, take_profit_price, stop_loss_price,cashqty=0):
        """
        Places an OCO order consisting of a take profit and a stop loss order
        following a market order execution.
        
        Parameters:
        - contract: The contract object to trade.
        - qty: Quantity of the contract to trade.
        - side: Buy or Sell for the initial market order.
        - take_profit_price: Price level to take profit.
        - stop_loss_price: Price level to stop loss.
        """
        # Place the initial market order
        if cashqty==0:
            market_order = MarketOrder(side, qty)
        else:
            market_order = MarketOrder(side, qty,cashQty=qty)
        contract_details = self.ib.reqContractDetails(contract)
        #min_tick = contract_details[0].minTick
        #take_profit_price=self.get_valid_precision(take_profit_price,min_tick)
        #stop_loss_price=self.get_valid_precision_sl((stop_loss_price-min_tick),min_tick)
        print("tp:-",take_profit_price,"sl:-",stop_loss_price)
        market_trade = self.ib.placeOrder(contract, market_order)
        print("Waiting for market order to be placed...")
        
        #while not market_trade.isDone():
        #    self.ib.sleep(1)  # Wait for the market order to complete
        
        print("Market order placed successfully.")
        fill_price = market_trade.orderStatus.avgFillPrice
        print(f"Fill price: {fill_price}")
        
        # Prepare the OCO orders
        # Inverting side for the OCO orders based on the initial market order
        oco_side = "SELL" if side.upper() == "BUY" else "BUY"
        
        # Create take profit limit order
        take_profit_order = LimitOrder(oco_side, qty, take_profit_price)
        take_profit_order.orderType = 'LMT'
        take_profit_order.tif = 'GTC'  # Good-Til-Cancelled
        
        # Create stop loss order
        stop_loss_order = StopOrder(oco_side, qty, stop_loss_price)
        stop_loss_order.orderType = 'STP'
        stop_loss_order.tif = 'GTC'  # Good-Til-Cancelled
        random_id = random.randint(0, 9999)
        # Set the OCO order ID
        ocoId = ((self.i*10000)+self.counter)
        self.counter += 1
        take_profit_order.ocaGroup = f"OCO_{ocoId}"
        stop_loss_order.ocaGroup = f"OCO_{ocoId}"
        take_profit_order.ocaType = 1  # Cancel all remaining orders in the group when one executes
        stop_loss_order.ocaType = 1
        
        # Place the OCO orders
        tp_trade = self.ib.placeOrder(contract, take_profit_order)
        sl_trade = self.ib.placeOrder(contract, stop_loss_order)
        self.ib.sleep(2)
        print("tp trade",tp_trade)
        print("sl trade",sl_trade)
        print(f"TP Order Status: {tp_trade.orderStatus.status}, SL Order Status: {sl_trade.orderStatus.status}")
        print("OCO orders placed.")
        return market_trade,tp_trade, sl_trade
    def close_all_positions(self):
        print("closing all positions")
        positions = self.ib.positions()
        for position in positions:
            contract = position.contract
            [contract] = self.ib.qualifyContracts(contract)
            self.ib.sleep(1)
            size = position.position
            if size > 0:  # Long position
                order = MarketOrder('SELL', abs(size))
            else:  # Short position
                order = MarketOrder('BUY', abs(size))
            trade = self.ib.placeOrder(contract, order)
            print(trade)
    
    def login(self,port):
        print("trying to login")
        while True:
            try:
                random_id = random.randint(0, 9999)
                ib = IB()
                ibs = ib.connect('127.0.0.1', port, clientId=random_id)
                print(datetime.now(timeZ_Ny), " : ", "connected ")
                return ibs
            except Exception as e:
                print(e)
                print(datetime.now(timeZ_Ny), " : ", "retrying to login in 60 seconds")
                time.sleep(65)
                pass

    def is_connected(self):
        if self.ib.isConnected():
            print(datetime.now(timeZ_Ny), " : ", "connected")
        else:
            self.ib = self._login()
    def get_historical_data(self, contract,duration='1 D',size='1 min'):
        """
        endDateTime: Can be set to '' to indicate the current time,
                or it can be given as a datetime.date or datetime.datetime,
                or it can be given as a string in 'yyyyMMdd HH:mm:ss' format.
                If no timezone is given then the TWS login timezone is used.
            durationStr: Time span of all the bars. Examples:
                '60 S', '30 D', '13 W', '6 M', '10 Y'.
            barSizeSetting: Time period of one bar. Must be one of:
                '1 secs', '5 secs', '10 secs' 15 secs', '30 secs',
                '1 min', '2 mins', '3 mins', '5 mins', '10 mins', '15 mins',
                '20 mins', '30 mins',
                '1 hour', '2 hours', '3 hours', '4 hours', '8 hours',
                '1 day', '1 week', '1 month'.
            whatToShow: Specifies the source for constructing bars.
                Must be one of:
                'TRADES', 'MIDPOINT', 'BID', 'ASK', 'BID_ASK',
                'ADJUSTED_LAST', 'HISTORICAL_VOLATILITY',
                'OPTION_IMPLIED_VOLATILITY', 'REBATE_RATE', 'FEE_RATE',
                'YIELD_BID', 'YIELD_ASK', 'YIELD_BID_ASK', 'YIELD_LAST'.
                For 'SCHEDULE' use :meth:`.reqHistoricalSchedule`.
        """
        bars = self.ib.reqHistoricalData(
            contract,
            endDateTime='',
            durationStr=duration,
            barSizeSetting=size,
            whatToShow='TRADES',
            useRTH=True
        )
        return bars
    @staticmethod
    def get_random():
        random_id = random.randint(0, 9999)
        return random_id
