from abc import ABC, abstractmethod
import pandas as pd

class DataProvider(ABC):
    def __init__(self, api_key, datatype="csv"):
        self.apikey = api_key
        self.datatype = datatype
    
    def datatype_to_pandas(self, url):
        if self.datatype.lower() == "csv":
            return pd.read_csv(url)
        else:
            print("Invalid data type.")
    
    @abstractmethod
    def get_latest_atr(self, symbol, interval, period):
        pass

    @abstractmethod
    def get_current_close(self, symbol, barsize):
        pass
