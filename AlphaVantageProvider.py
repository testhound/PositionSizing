from DataProvider import DataProvider
import time

class AlphaVantageProvider(DataProvider):
    def __init__(self, api_key, datatype="csv"):
        super(AlphaVantageProvider, self).__init__(api_key)
        self.datatype = datatype
        self.base_url = \
            'https://www.alphavantage.co/query?function={function}&apikey={key}&datatype={type}&'.format(function="{function}", key=self.apikey, type=self.datatype)

    def get_latest_atr(self, symbol, interval, period):
        url = self.base_url.format(function="ATR")
        url += f"symbol={symbol}&interval={interval}&time_period={period}"
        data = self.datatype_to_pandas(url)
        if len(data) <= 2:
            jdata = data.loc[0].to_json()
            if jdata.count("Thank you") == 1:
                print("Pausing for 1 minute")
                time.sleep(60)
                return self.get_latest_atr(symbol, interval, period)
            else:
                print(f"Incorrect API key or symbol={symbol} is not available.")
                return 0
        else:
            return data.loc[0].ATR

    def get_current_close(self, symbol, barsize):
        url = self.base_url.format(function="TIME_SERIES_INTRADAY")
        url += f"symbol={symbol}&interval={barsize}min"
        data = self.datatype_to_pandas(url)
        if len(data) <= 2:
            jdata = data.loc[0].to_json()
            if jdata.count("Thank you") == 1:
                print("Pausing for 1 minute")
                time.sleep(60)
                return self.get_current_close(symbol, barsize)
            else:
                print(f"Incorrect key or symbol={symbol} is not available.")
                return 0, 0
        else:
            return data.loc[0].timestamp, data.loc[0].close


if __name__ == '__main__':
    a = AlphaVantageProvider("T133DFH1BDEC1EPU")
    print(a.get_latest_atr("INTC", "daily", 90))
    print(a.get_current_close("INTC", 5))