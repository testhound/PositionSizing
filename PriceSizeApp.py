import numpy as np
import pandas as pd
import os
import fire

from AlphaVantageProvider import AlphaVantageProvider
from BarChartProvider import BarChartProvider

class PriceSizeApp:
    def __init__(self,inputf):
        self.BARCHART_API_KEY = "9bff8ed715c16109a1ce5c63341bb860"
        self.dirP = "Results/"
        self.create_dirs()
        self.s_list = self.read_symbols(inputf)
        self.df_summary = self.create_summary_df()

        self.period = 90
        self.interval = "daily"
        self.data_provider = BarChartProvider(self.BARCHART_API_KEY)

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

    def generate_summary(self, portfolio):
        df_dummy = self.df_summary.copy()
        for sym in self.s_list:
            atr = self.data_provider.get_latest_atr(sym, self.interval, self.period)
            # print(sym, atr)
            close = self.data_provider.get_current_close(sym, 5)[1]
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

