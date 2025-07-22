import pandas as pd

class PercentageVariationAgent:
    def calculate_variation(self, data):
        """
        Calculates the percentage variation for each currency cross.
        """
        # Ensure the first column is the time index
        if data.columns[0] == 'Time':
            data = data.set_index('Time')

        variation_data = data.pct_change() * 100
        # The first row will have NaNs, so we fill it with 0
        variation_data.fillna(0, inplace=True)
        return variation_data

class IncrementalSummationAgent:
    def calculate_incremental_sum(self, variation_data):
        """
        Calculates the incremental sum of the percentage variations.
        """
        return variation_data.cumsum()

class UfoChartAgent:
    def __init__(self, currencies):
        self.currencies = currencies

    def generate_ufo_chart(self, incremental_sums):
        """
        Generates the UFO market performance data.
        """
        ufo_data = pd.DataFrame(index=incremental_sums.index)

        for currency in self.currencies:
            currency_performance = pd.Series(0, index=incremental_sums.index)
            for cross in incremental_sums.columns:
                if currency in cross:
                    base, quote = cross[:3], cross[3:]
                    if currency == base:
                        currency_performance += incremental_sums[cross]
                    else:
                        currency_performance -= incremental_sums[cross]
            ufo_data[currency] = currency_performance

        return ufo_data
