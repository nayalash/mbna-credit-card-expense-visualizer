"""
Simple Credit Card Spending Analyzer
"""

import pandas as pd
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path
from datetime import datetime

class SpendingAnalyzer:
    def __init__(self):
        self.data = None
        self.folder_path = None
        
        self.category_patterns = {
            'Groceries': ['WAL-MART', 'THIARA', 'SOBEYS', 'IQBAL FOODS', 'VOILA', 'FRILLS'],
            'Utilities': ['HYDRO', 'RELIANCE', 'COGECO', 'ROGERS', 'PAYMENTUS', 'ENBRIDGE', 'KUBRA'],
            'Subscriptions': ['NETFLIX', 'PRIME', 'LA FITNESS', 'GOOGLE'],
            'Charity': ['HUMAN APPEAL'],
            'Transporation': ["UBER", "PRESTO"],
            "Food": ["TST", "SQ", "POPEYES", "MARY", "TEXAS", "CHICKEN", "COFFEE", "TEA", "TIM HORTONS", "CHA", "PIZZA"],
            "Gas": ["Petro", "Esso"]
        }
    
    def load_csvs_from_folder(self, folder_path):
        """Load all CSV files"""
        self.folder_path = Path(folder_path)
        csv_files = list(self.folder_path.glob('*.csv'))
        
        if not csv_files:
            raise ValueError("No CSV files found")
        
        all_data = []
        for csv_file in csv_files:
            df = pd.read_csv(csv_file)
            all_data.append(df)
        
        self.data = pd.concat(all_data, ignore_index=True)
        self.process_data()
        return len(csv_files)
    
    def process_data(self):
        """Process data - expenses only"""
        self.data['Posted Date'] = pd.to_datetime(self.data['Posted Date'], format='%m/%d/%Y')
        self.data['Type'] = self.data['Amount'].apply(lambda x: 'Payment' if x > 0 else 'Expense')
        self.data['Abs_Amount'] = abs(self.data['Amount'])
        self.data['Category'] = self.data['Payee'].apply(self.categorize_transaction)
        self.data['Month'] = self.data['Posted Date'].dt.strftime('%Y-%m')
        self.data = self.data.sort_values('Posted Date')
        
        # Expenses only
        self.data = self.data[self.data['Type'] == 'Expense'].copy()
    
    def categorize_transaction(self, payee):
        """Categorize transaction"""
        payee_upper = payee.upper()
        
        for category, patterns in self.category_patterns.items():
            if any(pattern in payee_upper for pattern in patterns):
                return category
        
        return 'Other'
    
    def get_monthly_spending(self):
        """Total spending by month"""
        return self.data.groupby('Month')['Abs_Amount'].sum().round(2)
    
    def get_monthly_average(self):
        """Average spending per month"""
        monthly_totals = self.get_monthly_spending()
        return monthly_totals.mean().round(2)
    
    def get_category_by_month(self):
        """Category breakdown by month"""
        pivot = self.data.pivot_table(
            values='Abs_Amount',
            index='Month',
            columns='Category',
            aggfunc='sum',
            fill_value=0
        ).round(2)
        
        pivot['TOTAL'] = pivot.sum(axis=1)
        return pivot
    
    def get_summary_stats(self):
        """Summary stats"""
        return {
            'total_expenses': self.data['Abs_Amount'].sum(),
            'num_transactions': len(self.data),
            'avg_transaction': self.data['Abs_Amount'].mean(),
            'monthly_average': self.get_monthly_average(),
            'num_months': self.data['Month'].nunique(),
            'date_range': f"{self.data['Posted Date'].min().strftime('%Y-%m-%d')} to {self.data['Posted Date'].max().strftime('%Y-%m-%d')}"
        }
    
    def get_top_merchants(self, n=10):
        """Top merchants"""
        return self.data.groupby('Payee')['Abs_Amount'].sum().sort_values(ascending=False).head(n).round(2)


class SpendingAnalyzerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Spending Analyzer")
        self.root.geometry("1200x800")
        
        self.analyzer = SpendingAnalyzer()
        self.folder_path = None
        
        self.setup_ui()
    
    def setup_ui(self):
        """Setup UI"""
        top_frame = ttk.Frame(self.root, padding="10")
        top_frame.pack(fill=tk.X)
        
        ttk.Label(top_frame, text="CSV Folder:").pack(side=tk.LEFT)
        self.folder_label = ttk.Label(top_frame, text="No folder selected", foreground="gray")
        self.folder_label.pack(side=tk.LEFT, padx=10)
        
        ttk.Button(top_frame, text="Select Folder", command=self.select_folder).pack(side=tk.LEFT)
        ttk.Button(top_frame, text="Load Data", command=self.load_data).pack(side=tk.LEFT, padx=5)
        
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.create_summary_tab()
        self.create_monthly_tab()
        self.create_merchants_tab()
        self.create_transactions_tab()
        
        self.auto_load_data()
    
    def create_summary_tab(self):
        """Summary tab"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Summary")
        
        self.summary_text = tk.Text(frame, wrap=tk.WORD, font=("Courier", 16))
        self.summary_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        scrollbar = ttk.Scrollbar(frame, command=self.summary_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.summary_text.config(yscrollcommand=scrollbar.set)
    
    def create_monthly_tab(self):
        """Monthly tab"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Monthly")
        
        self.monthly_text = tk.Text(frame, wrap=tk.WORD, font=("Courier", 14))
        self.monthly_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        scrollbar = ttk.Scrollbar(frame, command=self.monthly_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.monthly_text.config(yscrollcommand=scrollbar.set)
    
    def create_merchants_tab(self):
        """Merchants tab"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Top Merchants")
        
        columns = ('Merchant', 'Total')
        self.merchant_tree = ttk.Treeview(frame, columns=columns, show='headings', height=20)
        
        self.merchant_tree.heading('Merchant', text='Merchant')
        self.merchant_tree.heading('Total', text='Total Spent')
        
        self.merchant_tree.column('Merchant', width=600)
        self.merchant_tree.column('Total', width=150)
        
        self.merchant_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=self.merchant_tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.merchant_tree.config(yscrollcommand=scrollbar.set)
    
    def create_transactions_tab(self):
        """Transactions tab"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="All Transactions")
        
        columns = ('Date', 'Payee', 'Category', 'Amount')
        self.tree = ttk.Treeview(frame, columns=columns, show='headings', height=20)
        
        for col in columns:
            self.tree.heading(col, text=col)
        
        self.tree.column('Date', width=100)
        self.tree.column('Payee', width=500)
        self.tree.column('Category', width=150)
        self.tree.column('Amount', width=100)
        
        self.tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=self.tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.config(yscrollcommand=scrollbar.set)
    
    def select_folder(self):
        """Select folder"""
        folder = filedialog.askdirectory(title="Select Folder with CSV Files")
        if folder:
            self.folder_path = folder
            self.folder_label.config(text=folder, foreground="black")
    
    def auto_load_data(self):
        """Auto-load from ./data"""
        data_folder = Path('./data')
        if data_folder.exists():
            csv_files = list(data_folder.glob('*.csv'))
            if csv_files:
                self.folder_path = str(data_folder.absolute())
                self.folder_label.config(text=self.folder_path, foreground="black")
                self.root.after(100, self.load_data)
    
    def load_data(self):
        """Load data"""
        if not self.folder_path:
            messagebox.showwarning("No Folder", "Select a folder first!")
            return
        
        try:
            num_files = self.analyzer.load_csvs_from_folder(self.folder_path)
            messagebox.showinfo("Success", f"Loaded {num_files} CSV(s)!")
            
            self.update_summary()
            self.update_monthly()
            self.update_merchants()
            self.update_transactions()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error: {str(e)}")
    
    def update_summary(self):
        """Update summary"""
        stats = self.analyzer.get_summary_stats()
        
        text = f"""
SPENDING SUMMARY (Expenses Only)
{'='*60}

Date Range: {stats['date_range']}

Total Spent:        ${stats['total_expenses']:,.2f}
Transactions:       {stats['num_transactions']}
Average per Trans:  ${stats['avg_transaction']:,.2f}

Monthly Average:    ${stats['monthly_average']:,.2f}  ({stats['num_months']} months)

"""
        
        self.summary_text.delete(1.0, tk.END)
        self.summary_text.insert(1.0, text)
    
    def update_monthly(self):
        """Update monthly - just numbers"""
        monthly_total = self.analyzer.get_monthly_spending()
        category_by_month = self.analyzer.get_category_by_month()
        monthly_avg = self.analyzer.get_monthly_average()
        
        text = f"""MONTHLY SPENDING {'='*60}

"""
        
        for month, total in monthly_total.items():
            text += f"{month}:  ${total:,.2f}\n"
        
        text += f"\n{'-'*40}\n"
        text += f"Monthly Average:  ${monthly_avg:,.2f}\n"
        
        text += f"\n{'='*60}\n\n"
        text += f"CATEGORY BREAKDOWN BY MONTH\n"
        text += f"{'='*60}\n\n"
        
        # Header
        categories = [col for col in category_by_month.columns if col != 'TOTAL']
        header = f"{'Month':<12}"
        for cat in categories:
            header += f"{cat:<15}"
        header += f"{'TOTAL':<15}\n"
        text += header
        text += "-"*100 + "\n"
        
        # Rows
        for month in category_by_month.index:
            row = f"{month:<12}"
            for cat in categories:
                val = category_by_month.loc[month, cat]
                row += f"${val:>12,.2f} "
            total_val = category_by_month.loc[month, 'TOTAL']
            row += f"${total_val:>12,.2f}\n"
            text += row
        
        self.monthly_text.delete(1.0, tk.END)
        self.monthly_text.insert(1.0, text)
    
    def update_merchants(self):
        """Update merchants"""
        for item in self.merchant_tree.get_children():
            self.merchant_tree.delete(item)
        
        top = self.analyzer.get_top_merchants(20)
        for merchant, amount in top.items():
            self.merchant_tree.insert('', tk.END, values=(merchant, f"${amount:,.2f}"))
    
    def update_transactions(self):
        """Update transactions"""
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        for _, row in self.analyzer.data.iterrows():
            self.tree.insert('', tk.END, values=(
                row['Posted Date'].strftime('%Y-%m-%d'),
                row['Payee'][:50],
                row['Category'],
                f"${row['Abs_Amount']:.2f}"
            ))


def main():
    root = tk.Tk()
    app = SpendingAnalyzerGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()