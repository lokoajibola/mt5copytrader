# -*- coding: utf-8 -*-
"""
Created on Fri Jan 24 16:48:23 2025

COPY TRADE FROM A MASTER MT5 TO A SLAVE MT5 BY OPENING TWO MT5 TERMINALS

@author: LK
"""

import MetaTrader5 as mt5
import time

# Paths to MT5 terminals
MASTER_MT5_PATH = "C:/Program Files/FxPro - MetaTrader 5/terminal64.exe"  # Update with the correct path
SLAVE_MT5_PATH = "C:/Program Files/MetaTrader 5/terminal64.exe"  # Update with the correct path

# Master and Slave account credentials
MASTER_LOGIN = 51962256  # Master account login
MASTER_PASSWORD = "1nojf!W@MEUAz8" # Master account password
MASTER_SERVER = "mt5-demo.icmarkets.com"  # Master account server

SLAVE_LOGIN = 52140021  # Slave account login
SLAVE_PASSWORD = "tffq!48Wz6O1Pn"  # Slave account password
SLAVE_SERVER = "mt5-demo.icmarkets.com"   # Slave account server

# Initialize connection to a specific terminal
def initialize_terminal(path, account_login, account_password, account_server):
    if not mt5.initialize(path=path, login=account_login, password=account_password, server=account_server):
        print(f"Failed to connect to account {account_login} at {path}. Error: {mt5.last_error()}")
        return False
    print(f"Connected to account {account_login} at {path}.")
    return True

# Function to get open positions for an account
def get_open_positions():
    positions = mt5.positions_get()
    if positions is None:
        print(f"Error getting positions. Error: {mt5.last_error()}")
        return {}
    return {pos.symbol: pos for pos in positions}

# Function to close a trade
def close_trade(symbol, position_type, volume):
    close_type = mt5.ORDER_TYPE_SELL if position_type == mt5.POSITION_TYPE_BUY else mt5.ORDER_TYPE_BUY
    tick = mt5.symbol_info_tick(symbol)

    if tick is None:
        print(f"Failed to get tick data for {symbol}.")
        return

    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": volume,
        "type": close_type,
        "price": tick.bid if close_type == mt5.ORDER_SELL else tick.ask,
        "deviation": 10,
        "magic": 234000,
        "comment": "Closing copied trade",
    }

    result = mt5.order_send(request)
    if result.retcode != mt5.TRADE_RETCODE_DONE:
        print(f"Failed to close trade for {symbol}. Error: {result.retcode}")
    else:
        print(f"Successfully closed {symbol} position.")

# Function to synchronize trades between master and slave
def synchronize_trades():
    # Connect to the master terminal
    if not initialize_terminal(MASTER_MT5_PATH, MASTER_LOGIN, MASTER_PASSWORD, MASTER_SERVER):
        return
    master_positions = get_open_positions()
    # mt5.shutdown()  # Disconnect from the master terminal

    # Connect to the slave terminal
    if not initialize_terminal(SLAVE_MT5_PATH, SLAVE_LOGIN, SLAVE_PASSWORD, SLAVE_SERVER):
        return
    slave_positions = get_open_positions()

    # Copy trades from master to slave
    for symbol, master_pos in master_positions.items():
        if symbol not in slave_positions:
            print(f"Copying trade for {symbol} ({'BUY' if master_pos.type == mt5.POSITION_TYPE_BUY else 'SELL'})")
            request = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": symbol,
                "volume": master_pos.volume,
                "type": mt5.ORDER_TYPE_BUY if master_pos.type == mt5.POSITION_TYPE_BUY else mt5.ORDER_TYPE_SELL,
                "price": mt5.symbol_info_tick(symbol).ask if master_pos.type == mt5.POSITION_TYPE_BUY else mt5.symbol_info_tick(symbol).bid,
                "deviation": 10,
                "magic": 234000,
                "comment": "Copied trade",
            }
            result = mt5.order_send(request)
            if result.retcode != mt5.TRADE_RETCODE_DONE:
                print(f"Failed to copy trade for {symbol}. Error: {result.retcode}")
            else:
                print(f"Successfully copied trade for {symbol}.")
        else:
            print(f"{symbol} trade already exists in slave account. Skipping...")

    # Close trades on the slave account that no longer exist on the master
    for symbol, slave_pos in slave_positions.items():
        if symbol not in master_positions:
            print(f"Closing trade for {symbol} as it's no longer in the master account.")
            close_trade(symbol, slave_pos.type, slave_pos.volume)

    # mt5.shutdown()  # Disconnect from the slave terminal
    print("Trade synchronization completed.")

# Main loop to continuously synchronize trades
if __name__ == "__main__":
    while True:
        synchronize_trades()
        print("Waiting for 10 seconds before checking again...")
        time.sleep(10)
