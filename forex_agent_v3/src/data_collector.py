import pandas as pd
try:
    import MetaTrader5 as mt5
except ImportError:
    from . import mock_metatrader5 as mt5

class MT5DataCollector:
    def __init__(self, login, password, server, path):
        self.login = int(login)
        self.password = password
        self.server = server
        self.path = path

    def connect(self):
        """Connects to the MetaTrader 5 terminal."""
        if not mt5.initialize(path=self.path, login=self.login, password=self.password, server=self.server):
            print(f"Failed to initialize MT5: {mt5.last_error()}")
            return False
        print("MT5 initialized successfully.")
        return True

    def disconnect(self):
        """Shuts down the connection to the MetaTrader 5 terminal."""
        mt5.shutdown()
        print("MT5 connection shut down.")

    def get_historical_data(self, symbol, timeframe, num_bars=1000):
        """Gets historical bar data for a given symbol and timeframe."""
        rates = mt5.copy_rates_from_pos(symbol, timeframe, 0, num_bars)
        if rates is None:
            print(f"Failed to get rates for {symbol}: {mt5.last_error()}")
            return None

        rates_df = pd.DataFrame(rates)
        rates_df['time'] = pd.to_datetime(rates_df['time'], unit='s')
        return rates_df

    def get_live_data(self, symbol, timeframe, prev_time=None):
        """
        Gets the latest bar data for live trading simulation.
        If prev_time is provided, it will only return a new bar if the time has changed.
        """
        latest_rate = mt5.copy_rates_from_pos(symbol, timeframe, 0, 1)
        if latest_rate is None or len(latest_rate) == 0:
            return None

        rates_df = pd.DataFrame(latest_rate)
        rates_df['time'] = pd.to_datetime(rates_df['time'], unit='s')

        if prev_time is not None and rates_df['time'].iloc[0] == prev_time:
            return None  # No new bar yet

        return rates_df

import finnhub

import time

class FinnhubDataCollector:
    def __init__(self, api_key, cache_duration=3600):
        self.api_key = api_key
        self.client = finnhub.Client(api_key=self.api_key)
        self.cache = None
        self.last_cache_time = 0
        self.cache_duration = cache_duration

    def get_economic_calendar(self):
        """
        Gets economic calendar data, using a cache to avoid excessive API calls.
        """
        current_time = time.time()
        if self.cache is not None and (current_time - self.last_cache_time) < self.cache_duration:
            print("Returning cached economic calendar data.")
            return self.cache

        print("Fetching fresh economic calendar data from Finnhub.")
        try:
            economic_calendar = self.client.economic_calendar()
            self.cache = pd.DataFrame(economic_calendar.get('economicCalendar', []))
            self.last_cache_time = current_time
            return self.cache
        except Exception as e:
            print(f"Error fetching economic calendar from Finnhub: {e}")
            return pd.DataFrame()
