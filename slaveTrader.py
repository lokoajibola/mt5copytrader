# -- coding: utf-8 --
"""
Created on Sat Jan 25 19:38:58 2025

CODE FOR THE SLAVE TO COPY METATRADER 5 TRADES FROM THE MASTER
SYNCHRONIZES ITS TRADES WITH THE CSV FILE CREATED BY THE MASTER

@author: LK
"""

import pandas as pd
import time
import os
import socket
import MetaTrader5 as mt5
import time
import pandas as pd
from pandas.errors import EmptyDataError


# Paths to MT5 terminals
MASTER_MT5_PATH = "C:/Program Files/FxPro - MetaTrader 5/terminal64.exe"  # Update with the correct path
SLAVE_MT5_PATH = "C:/Program Files/MetaTrader 5/terminal64.exe"  # Update with the correct path

# # Master and Slave account credentials
# MASTER_LOGIN = 51962256  # Master account login
# MASTER_PASSWORD = "1nojf!W@MEUAz8" # Master account password
# MASTER_SERVER = "mt5-demo.icmarkets.com"  # Master account server

SLAVE_LOGIN = 52140021  # Slave account login
SLAVE_PASSWORD = "tffq!48Wz6O1Pn"  # Slave account password
SLAVE_SERVER = "mt5-demo.icmarkets.com"   # Slave account server

# CSV file to monitor
CSV_FILE = "open_trades.csv"
# Initialize MT5
def initialize_mt5():
    if not mt5.initialize(path=SLAVE_MT5_PATH,login=SLAVE_LOGIN, password=SLAVE_PASSWORD, server=SLAVE_SERVER):
        print(f"Failed to initialize MT5: {mt5.last_error()}")
        return False
    print("MT5 initialized successfully.")
    return True

# Function to read the CSV file
def read_csv_file():
    if not os.path.exists(CSV_FILE):
        return pd.DataFrame()  # Return an empty DataFrame if the file doesn't exist
    try:
        return pd.read_csv(CSV_FILE)
    except EmptyDataError:
        print("The file is empty or contains no data.")
    except FileNotFoundError:
        print(f"The file '{CSV_FILE}' does not exist.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

    # Code continues to execute after handling the error
    print("Continuing with the rest of the program...")


# Function to fetch open trades
def get_open_positions():
    positions = mt5.positions_get()
    if positions is None:
        print(f"Error fetching positions: {mt5.last_error()}")
        return []
    return [
        {
            "ticket": pos.ticket,
            "symbol": pos.symbol,
            "type": "Buy" if pos.type == mt5.ORDER_TYPE_BUY else "Sell", #pos.type,
            "volume": pos.volume,
            "price_open": pos.price_open,
            "magic": pos.magic,
        }
        for pos in positions
    ]

# Function to open a new trade
def open_trade(symbol, trade_type, volume, magic):
    trade_action = mt5.ORDER_TYPE_BUY if trade_type == "Buy" else mt5.ORDER_TYPE_SELL
    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": volume,
        "type": trade_action,
        "price": mt5.symbol_info_tick(symbol).ask if trade_type == "Buy" else mt5.symbol_info_tick(symbol).bid,
        "deviation": 10,
        "magic": magic,
        "comment": "Synchronized trade",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_IOC,
    }
    result = mt5.order_send(request)
    if result.retcode != mt5.TRADE_RETCODE_DONE:
        print(f"Failed to open trade for {symbol}: {result.retcode}")
    else:
        print(f"Opened trade: {symbol}, {volume} lots, {'Buy' if trade_type == mt5.ORDER_TYPE_BUY else 'Sell'}")

# Function to close a trade
def close_trade(ticket, symbol, trade_type, volume):
    
    position = mt5.positions_get(ticket=ticket)
    tick = mt5.symbol_info_tick(position[0].symbol)

    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "position": position[0].ticket,
        "symbol": position[0].symbol,
        "volume": position[0].volume,
        "type": mt5.ORDER_TYPE_BUY if position[0].type == mt5.ORDER_TYPE_SELL else mt5.ORDER_TYPE_SELL,
        "price": tick.ask if position[0].type == 1 else tick.bid,  
        "deviation": 20,
        "magic": 100,
        "comment": "python script close",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_IOC,
    }
    result = mt5.order_send(request)
    if result.retcode != mt5.TRADE_RETCODE_DONE:
        print(f"Failed to close trade for {symbol}: {result.retcode}")
    # else:
        # print(f"Closed trade: {symbol}, {volume} lots, {'Buy' if trade_action == mt5.ORDER_TYPE_SELL else 'Sell'}")

# Synchronize master and slave tables
def synchronize_trades(master_trades, slave_trades):
    # Convert trades to sets for comparison
    master_set = {(trade["symbol"], trade["type"], trade["volume"],  trade["ticket"]) for trade in master_trades}
    slave_set = {(trade["symbol"], trade["type"], trade["volume"], trade["magic"]) for trade in slave_trades}

    # Identify missing trades to open in slave
    trades_to_open = master_set - slave_set
    for trade in trades_to_open:
        symbol, trade_type, volume, magic = trade
        # volume = 0.01
        open_trade(symbol, trade_type, volume, magic)

    # Identify extra trades to close in slave
    trades_to_close = slave_set - master_set
    for trade in trades_to_close:
        for slave_trade in slave_trades:
            if (slave_trade["symbol"], slave_trade["type"], slave_trade["volume"], slave_trade["magic"]) == trade:
                close_trade(slave_trade["ticket"], slave_trade["symbol"], slave_trade["type"], slave_trade["volume"])


def main():
    last_data = None  # Store the previous state of the CSV
    if not initialize_mt5():
        return
    try:
        while True:
            # Read the current state of the CSV
            current_data = read_csv_file()
            slave_trades = get_open_positions()
            if current_data is not None:
                master_trades = current_data.to_dict('records')
                
                
            else:
                print("Warning: current_data is None. Skipping conversion to dictionary.")
                master_trades = []  # Fallback: Use an empty list or handle accordingly
            
            # Synchronize trades
            synchronize_trades(master_trades, slave_trades)            

            # Check if the file has been updated
            if current_data is not None and last_data is not None:
                if not current_data.equals(last_data):
                    print("Detected an update in the CSV file!")
                    print(current_data)
                    last_data = current_data

            time.sleep(5)  # Check for updates every 5 seconds
    except KeyboardInterrupt:
        print("Slave script stopped.")
        


if __name__ == "__main__":
    main()