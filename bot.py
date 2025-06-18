# tkinter allows tp build user interface
import tkinter as tk
from tkinter import ttk, messagebot
import json
import time
# Important for updating user interface
import threading
import random

# Store trading symbols and levels of trading (active positions and entry and exit prices)
DATA_FILE = "equities.json"

def fetch_mock_api(symbol):
    return {
        "price":100
    }
    

def mock_chatgpt_reponse(message):
    return f"Mock reponse to: {message}"

# Creating trading bot class
class TradingBotGUI:
    
    def __init__(self,root):
        self.root = root
        self.root.title("AI Trading Bot")
        self.equities = self.load_equities()
        # Flag for whether or not system is running
        # Actively trading equity in system? Toggle on or off
        self.system_running = False
        
        # Form to add equities to bot
        self.form_frame = tk.Frame(root)
        self.form_frame.pack(pady=10)
        
        # The symbol we are going to trade
        tk.Label(self.form_frame, text="Symbol:").grid(row=0,column=0)
        self.symbol_entry = tk.Entry(self.form_frame)
        self.symbol_entry.grid(row=0,column=1)
        # The levels to trade
        tk.Label(self.form_frame, text="Levels:").grid(row=0,column=2)
        self.levels_entry = tk.Entry(self.form_frame)
        self.levels_entry.grid(row=1,column=3)
        # Drawdown percentage
        tk.Label(self.form_frame, text="Drawdown %:").grid(row=0,column=4)
        self.drawdown_entry = tk.Entry(self.form_frame)
        self.drawdown_entry.grid(row=1,column=5)
        
        # Creating table to track traded equities
        self.tree = ttk.Treeview(root, columns=(
            "Symbols",
            "Positions",
            "Entry Price",
            "Levels",
            "Status"
        ), show='headings')
        # Setting the heading to these column headers and setting column widths
        for col in ["Symbols", "Positions", "Entry Price", "Levels", "Status"]:
            self.tree.heading(col,text=col)
            self.tree.column(col, width=120)
        self.tree.pack(pady=10)
        
        # Buttons that can control the bot
        self.toggle_system_button = tk.Button(root, text="Toggle Selected System", command=self.toggle_system)
        self.toggle_system_button.pack(pady=5)
        # Can remove selected equity from table
        self.remove_button = tk.Button(root, text="Remove Selected Equity", command=self.remove_selected_equity)
        self.remove_button.pack(pady=5)
        
    