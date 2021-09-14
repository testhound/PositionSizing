import pandas as pd
import numpy as np
import math
import datetime
import time
import dateutil.relativedelta
import os
import fire

class PriceSizeApp:
    def __init__(self,inputf):
        self.API_KEY = 'T133DFH1BDEC1EPU'  # replace demo with your api key
        self.BASE_URL = 'https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY_EXTENDED'
        self.BASE_URL_Rec = 'https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY'
        self.dirP = "Results/"
        self.create_dirs()
        self.s_list = self.read_symbols(inputf)
        self.df_summary = self.create_summary_df()

    def create_dirs(self):
        if not os.path.exists(os.path.dirname(self.dirP)):
            os.makedirs(os.path.dirname(self.dirP))

    def create_summary_df(self):
        df_summary = pd.DataFrame(columns=['Symbol', 'ATR', 'Price'])
        return df_summary

    def read_symbols(self,filename):
        df_symbols = pd.read_csv(filename)
        s_list = df_symbols["Symbol"].str.strip()
        return s_list

    def get_latest_atr(self, symbol):
        interval = "daily"
        period = 90
        base_url = 'https://www.alphavantage.co/query?function=ATR&'
        url = base_url + \
            f"symbol={symbol}&interval={interval}&time_period={period}&apikey={self.API_KEY}&datatype=csv"
        df_atr = pd.read_csv(url)
        # print(df_atr.loc[0])
        if len(df_atr) <= 2:
            a = df_atr.loc[0].to_json()
            print(a)
            if a.count("Thank you") == 1:
                print("------taking a pause for 1 minute-----")
                time.sleep(60)
                return self.get_latest_atr(symbol)
            else:
                print(
                    f"Incorrect API Key or Symbol = {symbol} is not compatible")
                return 0
        return df_atr.loc[0].ATR

    def get_current_close(self, symbol, barsize):
        url_rec = self.BASE_URL_Rec + \
            f'&symbol={symbol}&interval={barsize}min&apikey={self.API_KEY}&datatype=csv'
        df_rec = pd.read_csv(url_rec)

        if len(df_rec) <= 2:
            a = df_rec.loc[0].to_json()
            print(a)
            if a.count("Thank you") == 1:
                print("------taking a pause for 1 minute-----")
                time.sleep(60)
                return self.get_current_close(symbol, barsize)
            else:
                print(
                    f"Incorrect API Key or Symbol = {symbol} is not compatible")
                return 0, 0
        else:
            return df_rec.loc[0].timestamp, df_rec.loc[0].close

    def generate_summary(self, portfolio):
        df_dummy = self.df_summary.copy()
        for sym in self.s_list:
            atr = self.get_latest_atr(sym)
            close = self.get_current_close(sym, 5)[1]
            df_dummy.at[len(df_dummy)] = [sym, atr, close]

        df_dummy['atr_inv'] = 1/df_dummy['ATR']
        atr_sum = df_dummy.ATR.sum()
        df_dummy['atr_pct'] = df_dummy['ATR']/atr_sum

        #portfolio = 5000
        df_dummy['equal_dollar'] = portfolio/len(df_dummy)

        atr_inv_sum = df_dummy.atr_inv.sum()
        df_dummy['equal_volatility'] = df_dummy.atr_inv/atr_inv_sum

        df_dummy['dollars'] = df_dummy['equal_volatility']*portfolio

        df_dummy['shares_exact'] = df_dummy.dollars/df_dummy.Price
        df_dummy['shares_exact'] = pd.to_numeric(
            df_dummy.shares_exact, errors='coerce')
        df_dummy['shares'] = df_dummy['shares_exact'].round()
        self.df_summary = df_dummy.copy()

    def run_price_size_analysis(self, portfolio=5000):
        self.generate_summary(portfolio)
        self.df_summary.to_csv(f'{self.dirP}Summary.csv', index=None)
        print(self.df_summary[['Symbol', 'dollars', 'shares']])


if __name__ == '__main__':
  fire.Fire(PriceSizeApp)

#### Instructions
##1. run_price_size_analysis(self, portfolio=5000)  TO RUN PRICE SIZE ANALYSIS OVER SYMBOL LIST
#    ### python PriceSizeApp.py --inputf='Symbols.csv' run_price_size_analysis
# OR ### python PriceSizeApp.py --inputf='Symbols.csv' run_price_size_analysis 5000
# OR ### python PriceSizeApp.py --inputf='Symbols.csv' run_price_size_analysis --portfolio=5000
#    ###
#    ### python PriceSizeApp.py --inputf='sym_small.csv' run_price_size_analysis
# OR ### python PriceSizeApp.py --inputf='sym_small.csv' run_price_size_analysis 5000
# OR ### python PriceSizeApp.py --inputf='sym_small.csv' run_price_size_analysis --portfolio=5000
#    ###

