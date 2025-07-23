# This is a mock implementation of the MetaTrader5 library
# to allow for development on non-Windows platforms.

import pandas as pd

TIMEFRAME_M5 = 5

def initialize(login, password, server):
    print(f"Mock MT5: Initializing with login={login}, server={server}")
    return True

def shutdown():
    print("Mock MT5: Shutting down.")

def copy_rates_from_pos(symbol, timeframe, start_pos, count):
    print(f"Mock MT5: Fetching {count} bars of {symbol} on timeframe {timeframe}...")
    data = {
        'time': [pd.to_datetime('2023-01-02 00:00:00') + pd.Timedelta(minutes=5*i) for i in range(count)],
        'open': [1.0655 + i*0.0005 for i in range(count)],
        'high': [1.0660 + i*0.0005 for i in range(count)],
        'low': [1.0650 + i*0.0005 for i in range(count)],
        'close': [1.0658 + i*0.0005 for i in range(count)],
    }
    return pd.DataFrame(data).to_records(index=False)

def last_error():
    return "No error"
