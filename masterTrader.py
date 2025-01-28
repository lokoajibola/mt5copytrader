# -*- coding: utf-8 -*-
"""
Created on Sat Jan 25 19:38:06 2025

CODE FOR THE MASTER TO MIRROR METATRADER 5 TRADES FROM THE SLAVE
SYNCHRONIZES ITS TRADES WITH THE CSV FILE CREATED BY THE MASTER

@author: LK
"""

import socket
import MetaTrader5 as mt5
import time
import pandas as pd

# Paths to MT5 terminals
MASTER_MT5_PATH = "C:/Program Files/FxPro - MetaTrader 5/terminal64.exe"  # Update with the correct path
SLAVE_MT5_PATH = "C:/Program Files/MetaTrader 5/terminal64.exe"  # Update with the correct path

# Master and Slave account credentials
MASTER_LOGIN = 51962256  # Master account login
MASTER_PASSWORD = "1nojf!W@MEUAz8" # Master account password
MASTER_SERVER = "mt5-demo.icmarkets.com"  # Master account server

# SLAVE_LOGIN = 52140021  # Slave account login
# SLAVE_PASSWORD = "tffq!48Wz6O1Pn"  # Slave account password
# SLAVE_SERVER = "mt5-demo.icmarkets.com"   # Slave account server

# CSV file to store open trades
CSV_FILE = "open_trades.csv"

# Initialize MT5
def initialize_mt5():
    if not mt5.initialize(path=MASTER_MT5_PATH,login=MASTER_LOGIN, password=MASTER_PASSWORD, server=MASTER_SERVER):
        print(f"Failed to initialize MT5: {mt5.last_error()}")
        return False
    print("MT5 initialized successfully.")
    return True

# Fetch open trades and save them to CSV
def update_csv_with_open_trades():
    # Get open trades
    trades = mt5.positions_get()
    if trades is None:
        print(f"No trades found or error: {mt5.last_error()}")
        return

    # Create a DataFrame from the trades
    data = []
    for trade in trades:
        data.append({
            "ticket": trade.ticket,
            "symbol": trade.symbol,
            "type": "Buy" if trade.type == mt5.ORDER_TYPE_BUY else "Sell",
            "volume": trade.volume,
            "price": trade.price_open,
            # "Profit": trade.profit,
            "time": trade.time
        })

    df = pd.DataFrame(data)
    df.to_csv(CSV_FILE, index=False)
    print(f"Open trades updated in {CSV_FILE}.")

def main():
    if not initialize_mt5():
        return

    try:
        while True:
            update_csv_with_open_trades()
            time.sleep(10)  # Update every 10 seconds
    except KeyboardInterrupt:
        print("Master script stopped.")
    finally:
        mt5.shutdown()

if __name__ == "__main__":
    main()