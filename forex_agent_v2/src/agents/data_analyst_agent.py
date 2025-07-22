from .base_agent import Agent
from ..data_collector import MT5DataCollector, FinnhubDataCollector

class DataAnalystAgent(Agent):
    def __init__(self, name, mt5_credentials, finnhub_api_key):
        super().__init__(name)
        self.mt5_collector = MT5DataCollector(**mt5_credentials)
        self.finnhub_collector = FinnhubDataCollector(finnhub_api_key)

    def execute(self, task):
        """
        Executes a data collection task.
        task: a dictionary specifying the task, e.g.,
              {'source': 'mt5', 'symbol': 'EURUSD', 'timeframe': 'M5', 'count': 100}
              {'source': 'finnhub', 'type': 'economic_calendar'}
        """
        if task['source'] == 'mt5':
            self.mt5_collector.connect()
            data = self.mt5_collector.get_price_data(task['symbol'], task['timeframe'], 0, task['count'])
            self.mt5_collector.disconnect()
            return data
        elif task['source'] == 'finnhub':
            return self.finnhub_collector.get_economic_calendar()
        else:
            return "Unknown data source"
