# -*- coding: utf-8 -*-
"""
Created on Sat Jan 25 19:38:58 2025

@author: LK
"""

import pandas as pd
import time
import os

# CSV file to monitor
CSV_FILE = "open_trades.csv"

# Function to read the CSV file
def read_csv_file():
    if not os.path.exists(CSV_FILE):
        return pd.DataFrame()  # Return an empty DataFrame if the file doesn't exist
    return pd.read_csv(CSV_FILE)

def main():
    last_data = None  # Store the previous state of the CSV

    try:
        while True:
            # Read the current state of the CSV
            current_data = read_csv_file()

            # Check if the file has been updated
            if last_data is None or not current_data.equals(last_data):
                print("Detected an update in the CSV file!")
                print(current_data)
                last_data = current_data

            time.sleep(5)  # Check for updates every 5 seconds
    except KeyboardInterrupt:
        print("Slave script stopped.")

if __name__ == "__main__":
    main()
