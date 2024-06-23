import ccxt
import creds



class binance:
    def __init__(self, login_type = 'public', apikey = creds.BINANCE_API_KEY, secretkey = creds.BINANCE_SECRET_KEY):
        self.login_type = login_type
        self.login = 'fail'
        if login_type == 'private':
            try:
                self.exchange = ccxt.binance({
                    'apiKey': apikey,
                    'secret': secretkey ,
                })
                self.exchange.fetch_balance()
                self.login = 'success'
            except Exception as e:
                print('login error')
                self.login = 'fail'
                print(e)
        elif login_type == 'public':
            self.exchange = ccxt.binance()

    def load_markets(self):
        load_markets = self.exchange.load_markets()
        return load_markets
    
    def fetch_currencies(self):
        fetch_currencies = self.exchange.fetch_currencies()
        return fetch_currencies
    
    def fetch_ticker(self, symbol):
        fetch_ticker = self.exchange.fetch_ticker(symbol)
        return fetch_ticker
    
    def fetch_tickers(self, symbols=None):
        if symbols is None:
            symbols = self.exchange.symbols
        fetch_tickers = self.exchange.fetch_tickers(symbols)
        return fetch_tickers
    
    def fetch_order_book(self, symbol):
        fetch_order_book = self.exchange.fetch_order_book(symbol)
        return fetch_order_book
    
    def fetch_ohlcv(self, symbol, timeframe='1m', since=None, limit=None):
        fetch_ohlcv = self.exchange.fetch_ohlcv(symbol, timeframe, since, limit)
        return fetch_ohlcv
    
    def fetch_status(self):
        fetch_status = self.exchange.fetch_status()
        return fetch_status
    
    def fetch_trades(self):
        fetch_trades = self.exchange.fetch_trades()
        return fetch_trades
    
    def fetch_balance(self):
        try:
            fetch_balance = self.exchange.fetch_balance()
            return fetch_balance
        except Exception as e:
            print(e)

    def create_market_buy_order(self,symbol: str, amount: float, params = {}):
        if self.login == 'success':
            try:
                create_market_buy_order = self.exchange.create_market_buy_order(symbol, amount, params)
                return create_market_buy_order
            except Exception as e:
                print(e)
        else:
            print('login error')
    
    def create_market_sell_order(self,symbol: str, amount: float, params = {}):
        if self.login == 'success':
            try:
                create_market_sell_order = self.exchange.create_market_sell_order(symbol, amount, params)
                return create_market_sell_order
            except Exception as e:
                print(e)
        else:
            print('login error')

    def create_limit_buy_order(self,symbol: str, amount: float, price: float, params = {}):
        if self.login == 'success':
            try:
                create_limit_buy_order = self.exchange.create_limit_buy_order(symbol, amount, price, params)
                return create_limit_buy_order
            except Exception as e:
                print(e)
        else:
            print('login error')

    def create_limit_sell_order(self,symbol: str, amount: float, price: float, params = {}):
        if self.login == 'success':
            try:
                create_limit_sell_order = self.exchange.create_limit_sell_order(symbol, amount, price, params)
                return create_limit_sell_order
            except Exception as e:
                print(e)
        else:
            print('login error')

    def create_order(self,symbol: str, type: str, side: str, amount: float, price: float = None, params = {}):
        if self.login == 'success':
            try:
                create_order = self.exchange.create_order(symbol, type, side, amount, price, params)
                return create_order
            except Exception as e:
                print(e)
        else:
            print('login error')
    
    def fetch_order(self,orderid: str, symbol: None, params = {}):
        if self.login == 'success':
            try:
                fetch_order = self.exchange.fetch_order(orderid,symbol,params)
                return fetch_order
            except Exception as e:
                print(e)
        else:
            print('login error')

    def cancel_order(self,orderid: str, symbol: None, params = {}):
        if self.login == 'success':
            try:
                cancel_order = self.exchange.cancel_order(orderid,symbol,params)
                return cancel_order
            except Exception as e:
                print(e)
        else:
            print('login error')
    
    def fetch_orderbook(self,symbol: str, limit = None, params = {}):
        if self.login == 'success':
            try:
                fetch_orderbook = self.exchange.fetch_order_book(symbol, limit, params)
                return fetch_orderbook
            except Exception as e:
                print(e)
        else:
            print('login error')
    
    def fetch_openorders(self,symbol = None, since = None, limit = None, params= {}): 
        if self.login == 'success':
            try:
                fetch_openorders = self.exchange.fetch_open_orders(symbol,since,limit,params)
                return fetch_openorders
            except Exception as e:
                print(e)
        else:
            print('login error')

    def fetch_closedorders(self,symbol = None, since = None, limit = None, params= {}): 
        if self.login == 'success':
            try:
                fetch_openorders = self.exchange.fetch_closed_orders(symbol,since,limit,params)
                return fetch_openorders
            except Exception as e:
                print(e)
        else:
            print('login error')
    
    def fetch_mytrades(self,symbol = None, since = None, limit = None, params = {}):
        if self.login == 'success':
            try:
                fetch_mytrades = self.exchange.fetch_my_trades(symbol, since, limit, params)
                return fetch_mytrades
            except Exception as e:
                print(e)
        else:
            print('login error')
    
    def deposits(self,code = None, since = None, limit = None, params = {}):
        if self.login == 'success':
            try:
                deposit = self.exchange.fetch_deposits(code,since,limit,params)
                return deposit
            except Exception as e:
                print(e)
        else:
            print('login error')

    def withdrawals(self,code = None, since = None, limit = None, params = {}):
        if self.login == 'success':
            try:
                withdrawal = self.exchange.fetch_withdrawals(code,since,limit,params)
                return withdrawal
            except Exception as e:
                print(e)
        else:
            print('login error')
    
    def create_stop_limit_order(self,symbol: str, side: str, amount: float, price: float, stopPrice: float, params = {}):
        if self.login == 'success':
            try:
                create_stop = self.exchange.create_stop_limit_order(symbol,side,amount,price,stopPrice,params)
            except Exception as e:
                print(e)
        else:
            print('login error')
    
    def create_stop_market_order(self,symbol: str, side: str, amount: float,  stopPrice: float, params = {}):
        if self.login == 'success':
            try:
                create_stop = self.exchange.create_stop_market_order(symbol,side,amount,stopPrice,params)
            except Exception as e:
                print(e)
        else:
            print('login error')
    
    def create_takeprofit(self,symbol: str, type: str, side: str, amount: float, price = None, takeProfitPrice = None, params = {}):
        if self.login == 'success':
            try:
                create_takeprofit = self.exchange.create_take_profit_order(symbol,type,side,amount,price,takeProfitPrice,params)
            except Exception as e:
                print(e)
        else:
            print('login error')
