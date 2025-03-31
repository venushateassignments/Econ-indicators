# -*- coding: utf-8 -*-
"""
Economic Analysis using FredAPI data
A teaching tool for students to learn about economic data analysis using FRED API
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from fredapi import Fred
from datetime import datetime
import os

class FredDataAnalyzer:
    def __init__(self, api_key='512a320ffbbb4f42bb4c2fccff785243'):
        """Initialize the FRED API connection"""
        self.fred = Fred(api_key=api_key)
        self.output_dir = "output"
        self._create_output_directory()

    def _create_output_directory(self):
        """Create output directory if it doesn't exist"""
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    def search_ticker(self, description):
        """Search for a ticker based on description"""
        ticker_info = self.fred.search(description)
        if ticker_info is None:
            print(f"Did not find ticker by searching '{description}'. Please revise your search.")
            return None
        return ticker_info

    def get_ticker_data(self, ticker_id, start_date=None, end_date=None):
        """Fetch data for a specific ticker"""
        try:
            data = self.fred.get_series(ticker_id, observation_start=start_date, observation_end=end_date)
            return data
        except Exception as e:
            print(f"Error fetching data for '{ticker_id}': {str(e)}")
            return None

    def save_data(self, data, ticker_id):
        """Save data to CSV files"""
        try:
            # Save daily data
            data.to_csv(f"{self.output_dir}/{ticker_id}.csv")
            # Save quarterly data
            pd.Series(data, pd.date_range('2013-01-05', datetime.now(), freq='QS')).to_csv(
                f"{self.output_dir}/{ticker_id}_quarterly.csv"
            )
            print(f"Data saved successfully for {ticker_id}")
        except Exception as e:
            print(f"Error saving data: {str(e)}")

    def plot_single_series(self, data, title, ylabel='Value'):
        """Plot a single time series"""
        plt.figure(figsize=(12, 6))
        plt.plot(data, label=title)
        plt.title(f'{title} Over Time')
        plt.xlabel('Time')
        plt.ylabel(ylabel)
        plt.grid(True)
        plt.legend()
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()

    def plot_multiple_series(self, series_dict, title, ylabel='Value'):
        """Plot multiple time series for comparison"""
        plt.figure(figsize=(12, 6))
        for label, data in series_dict.items():
            plt.plot(data, label=label)
        plt.title(title)
        plt.xlabel('Time')
        plt.ylabel(ylabel)
        plt.grid(True)
        plt.legend()
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()

def main():
    # Initialize the analyzer
    analyzer = FredDataAnalyzer()
    
    while True:
        print("\n=== FRED Economic Data Analysis Tool ===")
        print("1. Search for a ticker")
        print("2. Plot single economic indicator")
        print("3. Compare multiple countries' indicators")
        print("4. Exit")
        
        choice = input("\nEnter your choice (1-4): ")
        
        if choice == '1':
            description = input("Enter search description (e.g., 'unemployment rate USA'): ")
            ticker_info = analyzer.search_ticker(description)
            if ticker_info is not None:
                print("\nSearch Results:")
                print(ticker_info[['id', 'title', 'observation_start', 'observation_end']])
        
        elif choice == '2':
            ticker_id = input("Enter ticker ID: ")
            data = analyzer.get_ticker_data(ticker_id)
            if data is not None:
                title = input("Enter plot title: ")
                ylabel = input("Enter y-axis label: ")
                analyzer.plot_single_series(data, title, ylabel)
                save = input("Save data to CSV? (y/n): ")
                if save.lower() == 'y':
                    analyzer.save_data(data, ticker_id)
        
        elif choice == '3':
            print("\nEnter ticker IDs for comparison (comma-separated):")
            ticker_ids = input().split(',')
            ticker_ids = [t.strip() for t in ticker_ids]
            
            series_dict = {}
            for ticker_id in ticker_ids:
                data = analyzer.get_ticker_data(ticker_id)
                if data is not None:
                    series_dict[ticker_id] = data
            
            if series_dict:
                title = input("Enter plot title: ")
                ylabel = input("Enter y-axis label: ")
                analyzer.plot_multiple_series(series_dict, title, ylabel)
        
        elif choice == '4':
            print("Thank you for using the FRED Economic Data Analysis Tool!")
            break
        
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()