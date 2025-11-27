#!/usr/bin/env python3
"""
Credit Card Spending Analyzer - Launcher
Just double-click this file to start the analyzer!
"""

import sys
from pathlib import Path

# Check for required packages
try:
    import pandas
    import matplotlib
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    import tkinter
except ImportError as e:
    print("=" * 70)
    print("❌ Missing Required Package!")
    print("=" * 70)
    print(f"\nError: {e}")
    print("\nPlease install the required packages:")
    print("\n  pip install pandas matplotlib openpyxl")
    print("\nOr on Linux, you may also need:")
    print("\n  sudo apt-get install python3-tk")
    print("\n" + "=" * 70)
    input("\nPress Enter to exit...")
    sys.exit(1)

# Import and run the analyzer
from spending_analyzer import main

if __name__ == "__main__":
    print("Starting Credit Card Spending Analyzer...")
    print("\nTip: Place your CSV files in the './data' folder for automatic loading!")
    print("=" * 70 + "\n")
    main()