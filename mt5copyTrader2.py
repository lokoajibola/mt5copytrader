# -*- coding: utf-8 -*-
"""
Created on Fri Jan 24 19:47:24 2025

COPY TRADES FROM A MASTER MT5 TERMINAL TO A SLAVE MT5 TERMINAL USING TELEGRAM AS INTERMEDIARY


@author: LK
"""

import MetaTrader5 as mt5
import time
from telegram import Bot

# Telegram bot credentials
TELEGRAM_TOKEN = "7539276831:AAE_YQ0RraeMpW2zr3HLBGBw6nZWEul72MM"  # Replace with your bot's token
TELEGRAM_CHAT_ID = "1894679406"  # Replace with your Telegram chat ID

# Initialize Telegram bot
bot = Bot(token=TELEGRAM_TOKEN)

# # Replace these with your actual values
# api_id = 16047550  # Replace with your API ID
# api_hash = '5907aca3fc4b623071d21cb973a0462a'  # Replace with your API Hash
# phone_number = '+2348132380110'  # Replace with your phone number
# # channel_username = '-1427964477'  # Replace with the target channel's user

# # Initialize the Telethon client
# client = TelegramClient('real2b', api_id, api_hash)

# Paths to MT5 terminals
MASTER_MT5_PATH = "C:/Program Files/FxPro - MetaTrader 5/terminal64.exe"  # Update with the correct path
# SLAVE_MT5_PATH = "C:/Program Files/MetaTrader 5/terminal64.exe"  # Update with the correct path

# Master and Slave account credentials
MASTER_LOGIN = 51962256  # Master account login
MASTER_PASSWORD = "1nojf!W@MEUAz8" # Master account password
MASTER_SERVER = "mt5-demo.icmarkets.com"  # Master account server

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


if __name__ == "__main__":
    # Connect to the master terminal
    initialize_terminal(MASTER_MT5_PATH, MASTER_LOGIN, MASTER_PASSWORD, MASTER_SERVER)
        
    while True:
        master_positions = get_open_positions()
        time.sleep(10)
    