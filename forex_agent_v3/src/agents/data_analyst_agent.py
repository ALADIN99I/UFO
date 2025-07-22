from .base_agent import Agent
from ..data_collector import FMPDataCollector
import datetime

class DataAnalystAgent(Agent):
    def __init__(self, name, mt5_collector, fmp_api_key):
        super().__init__(name)
        self.mt5_collector = mt5_collector
        self.fmp_collector = FMPDataCollector(fmp_api_key)

    def execute(self, task):
        """
        Executes a data collection task.
        """
        if task['source'] == 'mt5':
            if self.mt5_collector.connect():
                data = self.mt5_collector.get_historical_data(
                    task['symbol'], task['timeframe'], task['num_bars']
                )
                self.mt5_collector.disconnect()
                return data
            return None
        elif task['source'] == 'fmp':
            today = datetime.date.today()
            future_date = today + datetime.timedelta(days=7)
            return self.fmp_collector.get_economic_calendar(today, future_date)
        return "Unknown data source"
