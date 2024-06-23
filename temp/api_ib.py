

"""
Interactive Brokers TWS API

- get account info
- get balance
- place orders
- place bracket orders
- query order
- cancel open order
"""

# Importing built-in libraries
import os, json, pytz, time
import datetime as dt
from datetime import datetime
from threading import Thread
from copy import deepcopy

# Importing third-party libraries
import pandas as pd								# pip install pandas
from ibapi.wrapper import EWrapper
from ibapi.client import EClient
from ibapi.common import OrderId, ListOfContractDescription, BarData, TickerId, TickAttrib, SetOfFloat, SetOfString, ListOfHistoricalTickBidAsk, ListOfHistoricalTick, ListOfHistoricalTickLast
from ibapi.order import Order
from ibapi.account_summary_tags import AccountSummaryTags
from ibapi.ticktype import TickTypeEnum
from ibapi.contract import Contract, ContractDetails
from ibapi.commission_report import CommissionReport
from ibapi.execution import Execution, ExecutionFilter



class IBTWSAPI(EWrapper, EClient):

	ID = "VT_API_TWS_IB"
	NAME = "Interactive Brokers TWS API"
	AUTHOR = "Variance Technologies pvt. ltd."
	EXCHANGE = "SMART"
	BROKER = "IB"
	MARKET = "SMART"

	TIMEZONE = "UTC"

	API_THREAD = None
	MAX_WAIT_TIME = 5

	app = None

	orderId = None
	_candle_data = []
	_completed_orders = []
	_positions={}
	_contract_detail_info = {}
	_expiries_and_strikes = {}
	_open_orders = []
	_tws_orders = {}
	_account = None
	_account_cash_balance = None
	_default_time_in_force = "DAY"
	_commissions = {}
	_executions = {}

	_sec_type = {
		"stock":"STK",
		"stocks":"STK",
		"option":"OPT",
		"options":"OPT",
		"futureContract":"FUT",
		"futureContractOption":"FOP",
		"futureContractOptions":"FOP",
		"Stocks":"STK",
		"Options":"OPT",
		"FutureContract":"FUT",
		"FutureContractOptions":"FOP",
	}

	def __init__(self, creds:dict):
		EClient.__init__(self, self)

		self.CREDS = creds

	# IB override methods
	def error(self, reqId, errorCode, errorString):
		if reqId != -1:
			print("ERROR", reqId, errorCode, errorString)

	def tickPrice(self, reqId, tickType, price, attrib):
		print("Tick price", reqId, TickTypeEnum.to_str(tickType), price)

	def tickSize(self, reqId: TickerId, tickType, size: int):
		print(reqId, TickTypeEnum.to_str(tickType), size)

	## Commision report
	def execDetails(self, reqId: int, contract: Contract, execution: Execution):
		self._executions[contract.symbol] = {'execId':execution.execId}

	def commissionReport(self, commissionReport: CommissionReport):
		self._commissions[commissionReport.execId] = commissionReport.commission
	## Historical data
	def historicalData(self, reqId: int, bar: BarData):
		_ = {
			"datetime":bar.date,
			"open":bar.open,
			"high":bar.high,
			"low":bar.low,
			"close":bar.close,
			"volume":bar.volume
		}
		self._candle_data.append(_)
		# print(bar.date, bar.open, bar.high, bar.low, bar.close,)

	def historicalDataEnd(self, reqId: int, start: str, end: str):
		# print(reqId, start, end)
		...

	## Account
	def accountSummary(self, reqId: int, account: str, tag: str, value: str, currency: str):
		if tag == 'TotalCashValue':
			self._account = account
			self._account_cash_balance = float(value)

	def _get_next_order_id(self):
		"""get the current class variable order_id and increment
		it by one.
		"""
		# reqIds can be used to update the order_id, if tracking is lost.
		# self.reqIds(-1)
		current_order_id = self.orderId
		self.orderId += 1
		return current_order_id

	def nextValidId(self, orderId:int):
		"""
		Method of EWrapper.
		Is called from EWrapper after a successful connection establishment.
		"""
		super().nextValidId(orderId)
		self.orderId = orderId
		return self

	def contractDetails(self, reqId: int, contractDetails:ContractDetails):
		# print(contractDetails.contract.secType, contractDetails.contract.lastTradeDateOrContractMonth, contractDetails.contract.exchange, contractDetails.contract.localSymbol, contractDetails.contractMonth, contractDetails.contract.primaryExchange)

		if contractDetails.contract.strike:
			# print(contractDetails.contract.strike, contractDetails.contract.lastTradeDateOrContractMonth, contractDetails.contract.exchange, contractDetails.contract.symbol, contractDetails.contract.right)
			s_exp = contractDetails.contract.lastTradeDateOrContractMonth
			exp = dt.date(int(s_exp[:4]), int(s_exp[4:6]), int(s_exp[-2:]))
			strike = float(contractDetails.contract.strike)

			if exp not in self._expiries_and_strikes: self._expiries_and_strikes[exp] = []
			if strike not in self._expiries_and_strikes[exp]: self._expiries_and_strikes[exp].append(strike)
				
		if all([
				not self._contract_detail_info, 
				"QBALGO" not in contractDetails.contract.exchange, 
				contractDetails.contract.primaryExchange not in ["SMART","QBALGO"],
				"QBALGO" not in contractDetails.contract.primaryExchange,
			]):
			self._contract_detail_info = {
				"secType":contractDetails.contract.secType,
				"symbol":contractDetails.contract.symbol,
				"expiry":contractDetails.contractMonth,
				"exchange":contractDetails.contract.primaryExchange or contractDetails.contract.exchange,
				"contractId":contractDetails.contract.conId,
				"min_tick":contractDetails.minTick,
				"min_size":contractDetails.mdSizeMultiplier,
				"currency":contractDetails.contract.currency,
				"multiplier":contractDetails.contract.multiplier,
			}
	def position(self, account, contract, pos, avgCost):
		position_data = {
        "account": account,
        "symbol": contract.symbol,
		"secType":contract.secType,
        "contract": contract,
        "position": pos,
        "average_cost": avgCost
    	}
		self._positions[contract.conId] = position_data
	def completedOrder(self, contract: Contract, order: Order, orderState):
		self._completed_orders.append({'symbol':contract.symbol, "order_id":order.permId, "status":orderState.status, "price":order.lmtPrice})

	def openOrder(self, orderId: OrderId, contract: Contract, order: Order, orderState):
		self._open_orders.append({'symbol':contract.symbol, "order_id":order.permId, "status":orderState.status})
	
		if int(orderId) not in self.app._tws_orders:
			self.app._tws_orders[int(orderId)] = {}
			self.app._tws_orders[int(orderId)].update({'symbol':contract.symbol, 'side':order.action, 'type':order.orderType})
	
		# print('openOrder id:', orderId, contract.symbol, contract.secType, '@', contract.exchange, ':', order.action, order.orderType, 'quantity:',order.totalQuantity, orderState.status)

	def orderStatus(self, orderId: OrderId, status: str, filled: float, remaining: float, avgFillPrice: float, permId: int, parentId: int, lastFillPrice: float, clientId: int, whyHeld: str, mktCapPrice: float):
		if int(orderId) in self.app._tws_orders:
			self.app._tws_orders[int(orderId)].update({'perm_id':permId})
	
		# print(self.app._tws_orders)
		if status.upper() == 'FILLED':
			# print('orderStatus - orderid:', orderId, 'status:', status, 'filled', filled, 'remaining', remaining, 'lastFillPrice', lastFillPrice)
			self.app._tws_orders[int(orderId)]['fill_price'] = lastFillPrice
			if self.app is not None:
				symbol = self.app._tws_orders[int(orderId)]['symbol']
				side = self.app._tws_orders[int(orderId)]['side']
				self.app._on_tws_order_filled(orderId, permId, symbol, side, lastFillPrice, filled)

	def securityDefinitionOptionParameter(self, reqId: int, exchange: str, underlyingConId: int, tradingClass: str, multiplier: str, expirations: SetOfString, strikes: SetOfFloat):
		# return super().securityDefinitionOptionParameter(reqId, exchange, underlyingConId, tradingClass, multiplier, expirations, strikes)
		# print("SecurityDefinitionOptionParameter.","ReqId:", reqId, "Exchange:", exchange, "Underlying conId:", underlyingConId, "TradingClass:", tradingClass, "Multiplier:", multiplier,"Expirations:", expirations, "Strikes:", str(strikes))
		# print(expirations)
		# print(strikes)
		# print()
		self._expiries_and_strikes['expiries'] = sorted([dt.datetime.strptime(str(i), "%Y%m%d").date() for i in expirations])
		self._expiries_and_strikes['strikes'] = sorted([float(i) for i in strikes])
	
	# Public methods
	def connect(self) -> None:
		"""
		Connect the system with Interactive brokers TWS desktop app\n
		"""
		super().connect(self.CREDS['host'], self.CREDS['port'], self.CREDS.get('client_id') or 1)
		Thread(target=self.run, daemon=True).start()

		time.sleep(1)

	def connect_app(self, app) -> None:
		self.app = app

	def get_account_info(self) -> dict:
		"""
		Returns account information\n
		"""
		self.reqAccountSummary(1, "All", AccountSummaryTags.AllTags)
		time.sleep(2)
		return self._account

	def get_account_balance(self) -> float:
		"""
		Returns account balance for segment\n
		"""
		self.reqAccountSummary(1, "All", AccountSummaryTags.TotalCashValue)
		time.sleep(5)
		return self._account_cash_balance

	def get_contract_info(self, contract: str, symbol: str, **options) -> None:
		"""
		Returns info of the contract\n
		"""
		c = Contract()
		c.symbol = symbol
		c.secType = self._sec_type[contract]
		if c.secType == "FUT": c.secType = "CONTFUT"
		
		self.reqContractDetails(15, c)

		time.sleep(options.get('sleep') or 1)
		info = deepcopy(self._contract_detail_info)
		self._contract_detail_info = {}
		return info

	def get_options_expiries_and_strike_prices(self, contract: str, symbol: str, exchange: str, sec_type: str, contract_id: int):
		"""
		Downloads options chain\n
		"""
		if contract.lower() in ["stocks", "options"]: exchange = ""
		
		self.reqSecDefOptParams(0, symbol, exchange, sec_type, contract_id)
		
		time.sleep(2)
		data = deepcopy(self._expiries_and_strikes)
		self._expiries_and_strikes = {}
		return data

	def get_candle_data(self, contract:str, symbol:str, timeframe:str, period:str='2d', exchange:str=..., **options) -> pd.DataFrame:
		"""
		Get candle data from the api\n
		"""
		
		_tf = {
			's':"sec",
			'm':"min",
			"h":"hour"

		}
		
		self._candle_data = []

		c = Contract()
		c.symbol = symbol
		c.secType = self._sec_type[contract]
		c.exchange = exchange
		
		if options.get('currency'): c.currency = options['currency']
		if options.get('multiplier'): c.multiplier = options['multiplier']

		if options.get("primary_exchange"): c.primaryExchange = options['primary_exchange']

		if options.get("expiry"): c.lastTradeDateOrContractMonth = options['expiry']
		if options.get("call_put"): c.right = options['call_put']
		if options.get("strike_price"): c.strike = options['strike_price']

		if contract in ['futureContract', "FutureContract"]:
			info = self.get_contract_info(contract, symbol)
			# print(info)

			# c.exchange = info['exchange']
			c.lastTradeDateOrContractMonth = info['expiry']
		
		_timeframe = timeframe[:-1] + ' ' + _tf[timeframe[-1]] + ('s' if timeframe[:-1] != '1' else '')
	
		_period = ' '.join([i.upper() for i in period])
		self.reqHistoricalData(9, c, '', _period, _timeframe, 'MIDPOINT', 0, 2, False, [])

		time.sleep(options.get('sleep') or 4)
		df = pd.DataFrame(self._candle_data)
		# print(df)
		df.index = [datetime.fromtimestamp(int(x), tz=pytz.timezone(self.TIMEZONE)) for x in df.datetime]
		self._candle_data = []
		return df[['open', 'high', 'low', 'close', 'volume']]

	def place_order(
			self, 
			contract: str, 
			symbol: str, 
			side: str, 
			quantity: int, 
			order_type: str="MARKET", 
			price: float=...,
			exchange: str=...,
			**options,
		) -> int:
		"""
		Places order to account\n
		Params:
			symbol		:	str		=	Ticker symbol
			side		:	str		=	Side to execute. ie. BUY or SELL
			quantity	:	int 	=	No of quantity to trade
			order_type	:	str		=	Entry order type. ie. MARKET or LIMIT or STOP
			price		:	float	= 	Entry limit price if LIMIT order is to be set or STOP price if stop order is to be set

		Returns:
			Permenent order ids of order
		"""
		_order_type = {
			"MARKET":"MKT",
			"LIMIT":"LMT",
			"STOP":"STP"
		}

		self._raw_vs_perm_order_id = {}
		
		# Creating contract
		c = Contract()
		c.symbol = symbol

		c.secType = self._sec_type[contract]
		c.exchange = exchange

		if options.get('currency'): c.currency = options['currency']
		if options.get('multiplier'): c.multiplier = options['multiplier']
		if options.get("primary_exchange"):
			c.primaryExchange = options['primary_exchange']

		if contract in ['futureContract', "FutureContract"]:
			info = options['contract_details']
			c.lastTradeDateOrContractMonth = info['expiry']

		if contract in ["options", "futureContractOptions", "option", "futureContractOption", "Options", "FutureContractOptions"]:
			c.lastTradeDateOrContractMonth = options['expiry']
			c.strike = options['strike_price']
			c.right = options['call_put'][0].upper()

		# Creating single order
		order_id = self._get_next_order_id()
		order = Order()
		order.orderId = order_id
		order.action = side.upper()
		order.orderType = _order_type[order_type]
		order.totalQuantity = quantity
		order.transmit = True
		order.eTradeOnly = False
		order.firmQuoteOnly = False

		if order_type == 'LIMIT':
			order.lmtPrice = price
			order.tif = self._default_time_in_force
		
		if order_type == 'STOP':
			order.auxPrice = price
			order.tif = self._default_time_in_force

		self.placeOrder(order_id, c, order)

		time.sleep(options.get('sleep', 2))
		resp = self.app._tws_orders[order_id]
		resp.update({'temp_id':int(order_id), 'quantity':quantity})
		return resp
	
	def replace_order(
			self, 
			contract: str, 
			symbol: str, 
			side: str, 
			quantity: int, 
			order_type: str="MARKET", 
			price: float=...,
			exchange: str=...,
			orderid:str=...,
			**options,
		) -> int:
		"""
		Places order to account\n
		Params:
			symbol		:	str		=	Ticker symbol
			side		:	str		=	Side to execute. ie. BUY or SELL
			quantity	:	int 	=	No of quantity to trade
			order_type	:	str		=	Entry order type. ie. MARKET or LIMIT or STOP
			price		:	float	= 	Entry limit price if LIMIT order is to be set or STOP price if stop order is to be set

		Returns:
			Permenent order ids of order
		"""
		_order_type = {
			"MARKET":"MKT",
			"LIMIT":"LMT",
			"STOP":"STP"
		}

		self._raw_vs_perm_order_id = {}
		
		# Creating contract
		c = Contract()
		c.symbol = symbol

		c.secType = self._sec_type[contract]
		c.exchange = exchange

		if options.get('currency'): c.currency = options['currency']
		if options.get('multiplier'): c.multiplier = options['multiplier']
		if options.get("primary_exchange"):
			c.primaryExchange = options['primary_exchange']

		if contract in ['futureContract', "FutureContract"]:
			info = options['contract_details']
			c.lastTradeDateOrContractMonth = info['expiry']

		if contract in ["options", "futureContractOptions", "option", "futureContractOption", "Options", "FutureContractOptions"]:
			c.lastTradeDateOrContractMonth = options['expiry']
			c.strike = options['strike_price']
			c.right = options['call_put'][0].upper()

		# Creating single order
		order_id = orderid #self._get_next_order_id()
		order = Order()
		order.orderId = order_id
		order.action = side.upper()
		order.orderType = _order_type[order_type]
		order.totalQuantity = quantity
		order.transmit = True
		order.eTradeOnly = False
		order.firmQuoteOnly = False

		if order_type == 'LIMIT':
			order.lmtPrice = price
			order.tif = self._default_time_in_force
		
		if order_type == 'STOP':
			order.auxPrice = price
			order.tif = self._default_time_in_force

		res=self.placeOrder(order_id, c, order)
		print("order placed",res)
		time.sleep(options.get('sleep', 2))
		resp = self.app._tws_orders[order_id]
		resp.update({'temp_id':int(order_id), 'quantity':quantity})
		return resp

	def place_bracket_order(
			self, 
			contract:str, 
			symbol:str, 
			side:str, 
			quantity:int, 
			order_type:str="MARKET", 
			price:float=..., 
			stoploss:float=..., 
			targetprofit:float=...,
			exchange:str=...,
			**options,
		) -> int:
		"""
		Places entry order with stoploss and targetprofit as a child oco order\n
		Params:
			symbol		:	str		=	Ticker symbol
			side		:	str		=	Side to execute. ie. BUY or SELL
			quantity	:	int 	=	No of quantity to trade
			order_type	:	str		=	Entry order type. ie. MARKET or LIMIT or STOP
			price		:	float	= 	Entry limit price if LIMIT order is to be set
			stoploss	:	float	=	Stoploss price
			targetprofit:	float	= 	Targetprofit price

		Returns:
			Permenent order ids of entry order, stoploss, targetprofit
		"""
		_get_exit_side = lambda entry_side : "SELL" if entry_side.upper() == "BUY" else "BUY"
		_order_type = {
			"MARKET":"MKT",
			"LIMIT":"LMT",
			"STOP":"STP"
		}

		self._raw_vs_perm_order_id = {}

		# Creating contract
		c = Contract()
		c.symbol = symbol

		c.secType = self._sec_type[contract]
		c.exchange = exchange
		if options.get('currency'): c.currency = options['currency']
		if options.get('multiplier'): c.multiplier = options['multiplier']

		if options.get("primary_exchange"):
			c.primaryExchange = options['primary_exchange']

		if contract in ['futureContract',  "FutureContract"]:
			info = options['contract_details']
			c.lastTradeDateOrContractMonth = info['expiry']

		if contract in ["options", "futureContractOptions", "option", "futureContractOption", "Options", "FutureContractOptions"]:
			c.lastTradeDateOrContractMonth = options['expiry']
			c.strike = options['strike_price']
			c.right = options['call_put'][0].upper()

		# Creating entry order
		order_id = self._get_next_order_id()
		order = Order()
		order.orderId = order_id
		order.action = side.upper()
		order.orderType = _order_type[order_type]
		order.totalQuantity = quantity
		order.transmit = False
		order.eTradeOnly = False
		order.firmQuoteOnly = False
		# order.whatIf = True 

		if order_type == "LIMIT":
			order.lmtPrice = price
			order.tif = self._default_time_in_force

		# Creating targetprofit order
		if targetprofit:
			tp_order = Order()
			tp_order.orderId = self._get_next_order_id()
			tp_order.action = _get_exit_side(side)
			tp_order.totalQuantity = quantity
			tp_order.orderType = "LMT"
			tp_order.tif = self._default_time_in_force
			tp_order.lmtPrice = targetprofit
			tp_order.parentId = order.orderId
			tp_order.transmit = True if stoploss is None else False
			tp_order.eTradeOnly = False
			tp_order.firmQuoteOnly = False

		# Creating stoploss order
		if stoploss:
			sl_order = Order()
			sl_order.orderId = self._get_next_order_id()
			sl_order.action = _get_exit_side(side)
			sl_order.totalQuantity = quantity
			sl_order.orderType = "STP"
			sl_order.tif = self._default_time_in_force
			sl_order.auxPrice = stoploss
			sl_order.parentId = order.orderId
			sl_order.transmit = True
			sl_order.eTradeOnly = False
			sl_order.firmQuoteOnly = False

		self.placeOrder(order_id, c, order)
		
		if targetprofit is not None:
			self.placeOrder(tp_order.orderId, c, tp_order)

		if stoploss is not None:
			self.placeOrder(sl_order.orderId, c, sl_order)

		time.sleep(options.get('sleep', 5))

		resp = self.app._tws_orders[order_id]
		resp.update({'temp_id':int(order_id), 'quantity':quantity})

		if stoploss: resp.update({'t_sl_id' : sl_order.orderId, 'p_sl_id':self.app._tws_orders[sl_order.orderId]['perm_id']})

		return resp

	def query_order(self, order_id:int) -> dict:
		"""
		Get order information\n
		"""
		self._open_orders = []
		self._completed_orders = []
		
		self.reqCompletedOrders(True)
		self.reqOpenOrders()
		time.sleep(1)

		for i in (self._open_orders + self._completed_orders):
			if int(i['order_id']) == int(order_id):
				return i

	def cancel_order(self, order_id:int) -> None:
		"""
		Cancel open order\n
		"""
		self.cancelOrder(orderId=order_id)

	def get_commission_report(self, symbol:str):
		self.reqExecutions(11, ExecutionFilter())

		time.sleep(2)
		
		exec_id = None
		if symbol in self._executions:
			exec_id = self._executions[symbol]['execId']
		
		if exec_id and (exec_id in self._commissions):
			return float(self._commissions[exec_id])
	def get_positions(self):
		self.reqPositions()
		time.sleep(10)
		print("current holdings in tws")
		#print(self.all_positions)
		print(self._positions)
		return self._positions
	def fetch_positions(self) -> list:
		
		self.reqCompletedOrders(True)
		time.sleep(5)
		o = self._completed_orders[:]
		self._completed_orders.clear()
		return o

	def isConnected(self):
		return super().isConnected()


if __name__ == "__main__":

	creds = {
		"account":"IB",
		"host":"127.0.0.1",
		"port":4001,
		"client_id":3
	}

	api = IBTWSAPI(creds=creds)
	api.connect()
	print("connected")
	positions=api.get_positions()
	print(positions)
	# NOTE Get account info
	# account_info = api.get_account_info()
	# print(account_info)
	
	# NOTE Get account balance
	# balance = api.get_account_balance()
	# print(balance)

	# NOTE Get contract info
	# contract = "Stocks"
	# symbol = "BNP"
	# contract_info = api.get_contract_info(contract=contract, symbol=symbol)
	# print(contract_info)

	# NOTE Get options expiries and strike price
	# contract = "Stocks"
	# symbol = "AAPL"
	# expiries_and_strikes = api.get_options_expiries_and_strike_prices(contract=contract, symbol=symbol)
	# print(expiries_and_strikes)

	# NOTE Get candle data
	# contract = "futureContract"#"Stocks"
	# symbol = "IBEX35"
	# timeframe = "2m"
	# period = "2d"
	# exchange = "SMART"
	# primary_exchange = "MEFFRV"
	# # df = api.get_candle_data(contract=contract, symbol=symbol, timeframe=timeframe, period=period, exchange=exchange, expiry="20221111", strike_price=137.0, call_put="C")
	# df = api.get_candle_data(contract=contract, symbol=symbol, timeframe=timeframe, period=period, exchange=exchange, primary_exchange=primary_exchange)
	# print(df)

	# NOTE Place order
	# contract = "options"
	# symbol = "AAPL"
	# side = "BUY"
	# expiry = "20221021"
	# strike = 142
	# call_put = "CE"
	# quantity = 2
	# order_type = "MARKET"
	# price = 142.5
	# exchange = "SMART"
	# order = api.place_order(contract=contract, symbol=symbol, side=side, quantity=quantity, order_type=order_type, price=price, exchange=exchange, expiry=expiry, strike=strike, call_put=call_put)
	# print(order)

	# NOTE Place bracket order
	"""
	contract = "futureContract"
	symbol = "GC"
	side = "BUY"
	quantity = 2
	order_type = "MARKET"
	price = None
	stoploss = 1824
	targetprofit = None
	exchange = "COMEX"
	opt_options = {
		"expiry":"20221104",
		"strike":1500,
		"call_put":"CE",
	}
	ids = api.place_bracket_order(
		contract=contract, 
		symbol=symbol, 
		side=side, 
		quantity=quantity, 
		order_type=order_type, 
		price=price, 
		stoploss=stoploss, 
		targetprofit=targetprofit, 
		exchange=exchange, 
		#**opt_options
	)
	print(ids)
	"""

	# NOTE Query order
	# order_id = 806994023
	# query = api.query_order(order_id=order_id)
	# print(query)

	# NOTE Cancel order
	# order_id = 419
	# api.cancel_order(order_id=order_id)
	
	# NOTE Get positions report
	# report = api.fetch_positions()
	# print(report)

	# NOTE Get commissions report
	# symbol = "GC"
	# commissions = api.get_commission_report(symbol=symbol)
	# print(commissions)