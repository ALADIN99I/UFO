import pandas as pd

class UfoCalculator:
    def __init__(self, currencies):
        self.currencies = currencies

    def calculate_percentage_variation(self, price_data):
        """
        Calculates the percentage variation for each currency cross.
        """
        if 'time' in price_data.columns:
            price_data = price_data.set_index('time')

        variation_data = price_data.pct_change() * 100
        variation_data.fillna(0, inplace=True)
        return variation_data

    def calculate_incremental_sum(self, variation_data):
        """
        Calculates the incremental sum of the percentage variations.
        """
        return variation_data.cumsum()

    def generate_ufo_data(self, incremental_sums):
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
