from .base_agent import Agent
from ..data_collector import EconomicCalendarCollector
import pandas as pd

class DataAnalystAgent(Agent):
    def __init__(self, name, mt5_collector):
        super().__init__(name)
        self.mt5_collector = mt5_collector
        self.economic_calendar_collector = EconomicCalendarCollector()

    def execute(self, task):
        """
        Executes a data collection task.
        """
        if task['source'] == 'mt5':
            data = {}
            if self.mt5_collector.connect():
                for timeframe in task['timeframes']:
                    df = self.mt5_collector.get_historical_data(
                        task['symbol'], timeframe, task['num_bars']
                    )
                    data[timeframe] = df
                self.mt5_collector.disconnect()
                return data
            return None
        elif task['source'] == 'economic_calendar':
            return self.economic_calendar_collector.get_economic_calendar()
        return pd.DataFrame()
