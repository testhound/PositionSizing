from DataProvider import DataProvider
import pandas as pd
import datetime

class BarChartProvider(DataProvider):
    def __init__(self, api_key):
        super(BarChartProvider, self).__init__(api_key)
        self.base_url = f"https://ondemand.websol.barchart.com/getHistory.csv?apikey={self.apikey}"
        # self.ondemand = Client('https://ondemand.websol.barchart.com/service?wsdl')

    def __calculate_tr(self, high, low, previous_close):
        tr = high - low if (high - low) > (high - previous_close) else (high - previous_close)
        return tr if tr > (previous_close - low) else (previous_close - low)
    
    def __get_barchart_period(self, date):
        return date.strftime("%Y%m%d")

    def get_latest_atr(self, symbol, interval, period):
        # will have to cacluate ATR: 
            # https://www.investopedia.com/articles/trading/08/average-true-range.asp
            # https://www.fmlabs.com/reference/default.htm?url=ATR.htm
        if interval == "weekly":
            period *= 7
        today = datetime.datetime.today()
        end_period = self.__get_barchart_period(today)
        start_period = self.__get_barchart_period(today - datetime.timedelta(period*2))
        data = self.datatype_to_pandas(
            self.base_url + f"&symbol={symbol.upper()}&type={interval}&startDate={start_period}&endDate={end_period}&maxRecords={period+1}&interval=1&order=asc"
        )

        # calculate trading range values
        trading_range = [None]
        for index, row in data.iterrows():
            if index == 0:
                continue
            trading_range.append(self.__calculate_tr(row.high, row.low, data.loc[index-1].close))
        data["tr"] = trading_range
        # determine ATR
        data["atr_ema"] = data.tr.ewm(span=14).mean()
        data["atr_sma"] = data.tr.rolling(window=period).mean()

        return data.loc[len(data)-1].atr_sma

    def get_current_close(self, symbol, barsize):
        today = datetime.datetime.today()
        end = self.__get_barchart_period(today + datetime.timedelta(1))
        start = self.__get_barchart_period(today)
        data = self.datatype_to_pandas(
            self.base_url + f"&symbol={symbol.upper()}&type=minutes&startDate={start}&endDate={end}&maxRecords=1&interval={barsize}&order=desc"
        )
        return data.loc[0].timestamp, data.loc[0].close

if __name__ == '__main__':
    provider = BarChartProvider("9bff8ed715c16109a1ce5c63341bb860")
    for i in range(1, 90):
        print(i, provider.get_latest_atr("NFLX", "daily", 90, i, i))
    # print(provider.get_current_close("INTC", 5))

    # qqq - ema: 61 and 7, sma: 73
    # aapl - ema: 30, sma: 37           # 61 was ok
    # 