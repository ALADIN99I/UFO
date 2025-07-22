import pandas as pd

class DataIngestionAgent:
    def __init__(self, file_path):
        self.file_path = file_path

    def load_data(self):
        """
        Loads the Forex data from a CSV file.
        """
        try:
            data = pd.read_csv(self.file_path)
            # In a real scenario, we would have more sophisticated data cleaning and pre-processing here.
            # For now, we'll just handle potential missing values.
            data.fillna(method='ffill', inplace=True)
            data.fillna(method='bfill', inplace=True)
            return data
        except FileNotFoundError:
            print(f"Error: The file at {self.file_path} was not found.")
            return None
