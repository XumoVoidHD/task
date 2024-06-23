import pandas as pd
import yfinance as yf


start_date = "2016-03-22"
end_date = "2024-06-07"
symbol = "AAPL"
rsi_buy_threshold = 30
rsi_sell_threshold = 70
ema_short = 20
ema_long = 50
buy_weight = 10
capital = 10000


class Stocks:
    def __init__(self, symbol, quantity):
        self.symbol = symbol
        self.quantity = quantity
        self.length = 0
        self.data = pd.DataFrame()
        self.capital = capital
        self.holdValue = 0

    def prices(self):
        self.data = yf.download(self.symbol, start=start_date, end=end_date)
        self.data = self.data.drop(columns=['Volume', 'Open', 'Adj Close', 'High', 'Low'])
        self.data = self.data.reset_index()

    def showData(self):
        print(self.symbol)
        with pd.option_context('display.max_rows', None, 'display.max_columns', None):
            print(self.data)

    def hold(self):
        self.holdValue = self.data.at[self.length-1, 'Close'] * int(capital // self.data.at[0, 'Close'])

    def generateEMA(self):
        self.prices()
        self.length = len(self.data)
        self.data['ema20'] = [0.0] * self.length
        self.data['ema50'] = [0.0] * self.length
        self.data['bullish'] = [0] * self.length
        #self.showData()

        for i in range(ema_short, self.length):
            self.data.loc[i, 'ema20'] = self.data.loc[range(i - ema_short, i + 1), 'Close'].mean()

        for i in range(ema_long, self.length):
            values50 = self.data.loc[range(i - ema_long, i), 'Close'].mean()
            self.data.loc[i, 'ema50'] = float(values50)
            if self.data.loc[i, 'ema20'] > self.data.loc[i, 'ema50']:
                self.data.loc[i, 'bullish'] = 1
            else:
                self.data.loc[i, 'bullish'] = -1

    def generateRSI(self):

        self.data['Upward Movement'] = [0.0] * self.length
        self.data['Signal'] = [0] * self.length
        self.data['Downward Movement'] = [0.0] * self.length
        self.data['Average Upward Movement'] = [0.0] * self.length
        self.data['Average Downward Movement'] = [0.0] * self.length
        self.data['Relative Strength'] = [0.0] * self.length
        self.data['RSI'] = [0.0] * self.length

        for i in range(1, self.length):
            pre = float(self.data.at[i - 1, 'Close'])
            post = float(self.data.at[i, 'Close'])
            if post > pre:
                self.data.at[i, 'Upward Movement'] = post - pre
            elif pre >= post:
                self.data.at[i, 'Downward Movement'] = pre - post

        period = 14
        self.data.at[period, 'Average Upward Movement'] = self.data.loc[
            range(0, period + 1), 'Upward Movement'].mean()
        self.data.at[period, 'Average Downward Movement'] = self.data.loc[
            range(0, period + 1), 'Downward Movement'].mean()
        self.data.at[period, 'Relative Strength'] = self.data.at[
                                                        period, 'Average Upward Movement'] / \
                                                    self.data.at[
                                                        period, 'Average Downward Movement']
        self.data.at[period, 'RSI'] = 100 - (
                100 / (self.data.at[period, 'Relative Strength'] + 1))

        for i in range(period + 1, self.length):
            self.data.at[i, 'Average Upward Movement'] = (self.data.at[
                                                           i - 1, 'Average Upward Movement'] * (
                                                               period - 1) + self.data.at[
                                                           i, 'Upward Movement']) / period
            self.data.at[i, 'Average Downward Movement'] = (self.data.at[
                                                                i - 1, 'Average Downward Movement'] * (
                                                                    period - 1) +
                                                            self.data.at[
                                                                i, 'Downward Movement']) / period
            self.data.at[i, 'Relative Strength'] = self.data.at[i, 'Average Upward Movement'] / \
                                                   self.data.at[i, 'Average Downward Movement']
            self.data.at[i, 'RSI'] = 100 - (100 / (self.data.at[i, 'Relative Strength'] + 1))

    def generateSignal(self):
        self.generateEMA()
        self.generateRSI()
        for i in range(0, self.length):
            if self.capital > (self.data.at[i, 'Close'] * buy_weight):
                if self.data.at[i, 'RSI'] <= rsi_buy_threshold or self.data.at[i, 'bullish'] == 1:
                    self.data.at[i, 'Signal'] = 1
                    self.capital -= self.data.at[i, 'Close'] * buy_weight
                    self.quantity += buy_weight
                elif self.data.at[i, 'RSI'] >= rsi_sell_threshold or self.data.at[i, 'bullish'] == -1:
                    self.data.at[i, 'Signal'] = -1
                    self.capital += self.data.at[i, 'Close'] * self.quantity
                    self.quantity = 0

    def finalProfitLoss(self):
        self.generateSignal()
        self.hold()
        # self.showData()
        print(f"Initial Capital: {capital}")
        print(f"{self.symbol} Stock Owned: {self.quantity}")
        print(f"Final Capital: {self.capital}")
        print(f"Portfolio Value: {self.capital + (self.quantity * self.data.at[self.length-1, 'Close'])}")
        print(f"Hold Value: {self.holdValue}")

        if self.holdValue > self.capital + (self.quantity * self.data.at[self.length-1, 'Close']):
            return 0
        else:
            return 1


if __name__ == "__main__":
    wins = 0
    company_list = [
        "AAPL", "MSFT", "AMZN", "GOOGL", "GOOG", "NVDA", "TSLA", "META", "UNH",
        "JNJ", "V", "XOM", "WMT", "JPM", "PG", "MA", "HD", "CVX", "MRK", "ABBV", "PEP",
        "KO", "LLY", "BAC", "AVGO", "TMO", "COST", "DIS", "PFE", "CSCO", "ACN", "ABT",
        "DHR", "NFLX", "LIN", "NKE", "MCD", "NEE", "ADBE", "TXN", "PM", "ORCL", "AMD",
        "HON", "AMGN", "UNP", "MDT", "IBM", "SBUX", "QCOM", "GS", "LOW", "MS", "BLK",
        "BMY", "CAT", "GE", "RTX", "INTC", "ISRG", "CHTR", "AMT", "GILD", "NOW", "BKNG",
        "PLD", "PYPL", "SYK", "EL", "ZTS", "SPGI", "TMUS", "ADI", "LRCX", "SCHW", "CB",
        "REGN", "EQIX", "MU", "MMC", "APD", "FDX", "CL", "MDLZ", "TGT", "CI", "DUK",
        "ECL", "EW", "FIS", "MAR", "GM", "NSC", "SO", "PNC", "SHW", "TFC", "USB", "ITW",
        "HUM"
    ]
    for symbol in company_list:
        stock = Stocks(symbol, 0)
        wins += stock.finalProfitLoss()

    print(f"Wins: {wins}")