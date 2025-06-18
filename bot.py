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
        
        
        
    