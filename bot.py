# tkinter allows tp build user interface
import tkinter as tk
from tkinter import ttk, messagebox
import json
import time
# Important for updating user interface
import threading
import random
import alpaca_trade_api as tradeapi

import dotenv
import os

load_dotenv()
api = tradeapi.REST(os.getenv('ALPACA_KEY'), os.getenv('ALPACA_SECRET_KEY'), os.getenv('BASE_URL'), api_version='v2')

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
        self.levels_entry.grid(row=0,column=3)
        # Drawdown percentage
        tk.Label(self.form_frame, text="Drawdown %:").grid(row=0,column=4)
        self.drawdown_entry = tk.Entry(self.form_frame)
        self.drawdown_entry.grid(row=0,column=5)
        
        # Creating add button, form_frame is root for widget
        self.add_button = tk.Button(self.form_frame, text="Add Equity", command=self.add_equities)
        self.add_button.grid(row=0,column=6)
        
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
        
        # Buttons that can control the bot, root is different part of interface
        self.toggle_system_button = tk.Button(root, text="Toggle Selected System", command=self.toggle_selected_system)
        self.toggle_system_button.pack(pady=5)
        # Can remove selected equity from table
        self.remove_button = tk.Button(root, text="Remove Selected Equity", command=self.remove_selected_equity)
        self.remove_button.pack(pady=5)
        
        # Make interface for AI component
        self.chat_frame = tk.Frame(root)
        self.chat_frame.pack(pady=10)
        
        # Input entry
        self.chat_input = tk.Entry(self.chat_frame, width=50)
        self.chat_input.grid(row=0,column=0, padx=5)
        
        # Button to send message
        self.send_button = tk.Button(self.chat_frame, text="Send", command=self.send_message)
        self.send_button.grid(row=0,column=1)
        
        # Bot output, cannot be edited (DISABLED)
        self.chat_output = tk.Text(root, width=50, height=5, state=tk.DISABLED)
        self.chat_output.pack()
        
        # Load saved data, loading from json
        self.refresh_table()
        
        # For auto-refreshing
        # Thread creation can query updates in continuoues fashion
        self.running = True
        self.auto_update_thread = threading.Thread(target=self.auto_update, daemon=True)
        self.auto_update_thread.start()
        
        
    # Adding equities functions
    def add_equities(self):
        # Getting the symbol, levels, and drawdown from the entry fields
        symbol = self.symbol_entry.get().upper()
        levels = self.levels_entry.get()
        drawdown = self.drawdown_entry.get()
        
        # Check some invalid entries, first line of defense
        if not symbol or not levels.isdigit() or not drawdown.replace('.','',1).isdigit():
            messagebox.showerror("Error", "Please enter valid symbol, levels and drawdown")
            return
        
        levels = int(levels)
        drawdown = float(drawdown) / 100
        entry_price = fetch_mock_api(symbol)["price"]
        
        # Taking drawdown threshold and trade at each level at drawdown from entry price
        level_prices = {i+1: round(entry_price * (1 - drawdown * (i+1)), 2) for i in range(levels)}
        
        self.equities[symbol] = {
            "position": 0,
            "entry_price": entry_price,
            "levels": level_prices,
            "status": "Off"
        }
        # Save data and update table when adding equity
        self.save_equities()
        self.refresh_table()
        
        
    # Function to toggle selected system
    def toggle_selected_system(self):
        # Get what is selected in the table
        selected_items = self.tree.selection() 
        if not selected_items:
            messagebox.showwarning("Warning", "No equity is selected")
            
        for item in selected_items:
            # Going through data and seeing what is selected in the tree and find correct symbol
            symbol = self.tree.item(item)["values"][0]
            # If off turn it on, otherwise turn it off, checks whether actively trading symbol
            self.equities[symbol]["status"] = "On" if self.equities[symbol]["status"] == "Off" else "Off"
    
        self.save_equities()
        self.refresh_table()
        
    
    # Remove an equity
    def remove_selected_equity(self):
        selected_items = self.tree.selection()
        if not selected_items:
            messagebox.showwarning("Warning", "No equity is selected")
            return
        
        for item in selected_items:
            symbol = self.tree.item(item)["values"][0]
            if symbol in self.equities:
                del self.equities[symbol]
                
        self.save_equities()
        self.refresh_table()
            
            
    # Function to send message to chat
    def send_message(self):
        message = self.chat_input.get()
        if not message:
            return
        
        # Message input
        response = mock_chatgpt_reponse(message)
        
        # Display message in chat output
        self.chat_output.config(state=tk.NORMAL)
        self.chat_output.insett(tk.END, f"You: {message}\n{response}\n\n")
        # Display response in chat output
        self.chat_output.config(state=tk.DISABLED)
        # Delete input field
        self.chat_input.delete(0, tk.END)
        
       
    # Get current pricing to execute trades
    def fetch_alpaca_data(self, symbol):
        try:
            barset = api.get_latest_trade(symbol)
            return {"price": barset.price}
        except Exception as e:
            return {"price": -1} 
        
    # Check if any existing orders
    def check_existing_orders(self, symbol, price):
        try: 
            orders = api.list_orders(status='open', symbols = symbol)
            for order in orders:
                # If order already exists for this level
                if float(order.limit_price) == price:
                    return True
        except Exception as e:
            print("API Error", f"Error checking existing orders: {e}")
        
        # Need to place an order
        return False 
        
    
        
    
    # Updating table function
    def refresh_table(self):
        # Need to delete everything and repopulate with new data
        for row in self.tree.get_children():
            self.tree.delete(row)
            
        # Iterate through saved data and insert into table
        for symbol, data in self.equities.items():
            self.tree.insert("", tk.END, values=(
                symbol,
                data["position"],
                data["entry_price"],
                str(data["levels"]),
                data["status"]
            ))
            
    # Auto update user interface
    def auto_update(self):
        while self.running:
            time.sleep(5)
            self.trade_systems()
            
    # Save equities to json file
    def save_equities(self):
        with open(DATA_FILE, "w") as f:
            json.dump(self.equities, f)
            
    # Load equities from json file
    def load_equities(self):
        try:
            with open(DATA_FILE, "r") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}
        
    # Save on close
    def on_close(self):
        self.running = False
        self.save_equities()
        self.root.destroy()
        
if __name__ == '__main__':
    root = tk.Tk()
    app = TradingBotGUI(root)
    root.protocol("WM_DELETE_WINDOW", app.on_close)
    root.mainloop()

            
        
        
        
    