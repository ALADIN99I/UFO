from .base_agent import Agent
from ..data_collector import FinnhubDataCollector

class DataAnalystAgent(Agent):
    def __init__(self, name, mt5_collector, finnhub_config):
        super().__init__(name)
        self.mt5_collector = mt5_collector
        self.finnhub_collector = FinnhubDataCollector(**finnhub_config)

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
        elif task['source'] == 'finnhub':
            return self.finnhub_collector.get_economic_calendar()
        return "Unknown data source"
