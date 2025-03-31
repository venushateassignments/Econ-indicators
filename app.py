import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from fredapi import Fred
from datetime import datetime, timedelta
import os
import numpy as np

# Set page config
st.set_page_config(
    page_title="Economic Indicators Dashboard",
    page_icon="📈",
    layout="wide"
)

# Initialize FRED API with API key input
def init_fred():
    # Store API key in session state
    if 'fred_api_key' not in st.session_state:
        st.session_state.fred_api_key = '512a320ffbbb4f42bb4c2fccff785243'
    
    # Create sidebar input for API key
    with st.sidebar:
        st.session_state.fred_api_key = st.text_input(
            "Enter FRED API Key",
            value=st.session_state.fred_api_key,
            type="password"
        )
        st.markdown("""
        [Get a FRED API Key](https://fred.stlouisfed.org/docs/api/api_key.html)
        """)
    
    return Fred(api_key=st.session_state.fred_api_key)

# Cache the search results
@st.cache_data
def search_indicators(_fred, query):
    try:
        # Get raw results from FRED
        raw_results = _fred.search(query)
        
        if raw_results is not None and not raw_results.empty:
            # Create a copy to avoid modifying the original DataFrame
            results = raw_results.copy()
            
            # Convert problematic date columns to string format
            date_columns = ['observation_start', 'observation_end']
            for col in date_columns:
                if col in results.columns:
                    try:
                        # First convert to string to avoid any datetime parsing
                        results[col] = pd.to_datetime(results[col].astype(str), errors='coerce')
                        # Replace any NaT (Not a Time) values with a default date
                        results[col] = results[col].fillna(pd.Timestamp('1900-01-01'))
                        # Convert to string for display
                        results[col] = results[col].dt.strftime('%Y-%m-%d')
                    except Exception:
                        # If date parsing fails, use a default date
                        results[col] = '1900-01-01'
            
            # Keep only the most relevant columns
            keep_columns = ['id', 'title', 'observation_start', 'observation_end', 'frequency', 'units']
            results = results[[col for col in keep_columns if col in results.columns]]
            
            # Limit to top 3 results
            return results.head(3)
    except Exception as e:
        # Only show error if it's not the timestamp error
        if "Out of bounds nanosecond timestamp" not in str(e):
            st.error(f"Error searching for indicators: {str(e)}")
        return None

# Cache the series data
@st.cache_data
def get_series_data(_fred, series_id, start_date=None, end_date=None):
    try:
        data = _fred.get_series(series_id, observation_start=start_date, observation_end=end_date)
        if data is None or len(data) == 0:
            st.error(f"No data found for series {series_id}")
            return None
        return data
    except Exception as e:
        st.error(f"Error fetching data for {series_id}: {str(e)}")
        return None

def calculate_correlation(data1, data2):
    try:
        if data1 is None or data2 is None:
            return None
            
        # Align the data on dates
        combined_data = pd.concat([data1, data2], axis=1)
        combined_data.columns = ['Indicator1', 'Indicator2']
        # Remove any missing values
        combined_data = combined_data.dropna()
        
        if len(combined_data) < 2:
            st.warning("Insufficient overlapping data points to calculate correlation")
            return None
            
        return combined_data['Indicator1'].corr(combined_data['Indicator2'])
    except Exception as e:
        st.error(f"Error calculating correlation: {str(e)}")
        return None

def main():
    st.title("📈 Economic Indicators Dashboard")
    st.markdown("""
    *The work is co-created by Dr. Wilson Yu and AI in 2025*
    """)
    st.markdown("""
    This dashboard allows you to explore and visualize economic indicators from the Federal Reserve Economic Data (FRED) database.
    Compare two indicators and see their correlation.
    """)

    # Initialize FRED
    fred = init_fred()

    # Initialize scale factor in session state
    if 'scale_factor' not in st.session_state:
        st.session_state.scale_factor = 1.0

    # Sidebar for controls
    st.sidebar.header("Search and Select Indicators")
    
    # First Indicator Search
    st.sidebar.subheader("Economic Indicator 1")
    search_query1 = st.sidebar.text_input("Search for first indicator", "unemployment rate")
    
    # Search results for first indicator
    if search_query1:
        search_results1 = search_indicators(fred, search_query1)
        if search_results1 is not None and not search_results1.empty:
            st.sidebar.markdown("### Top 3 Results for Indicator 1")
            for idx, row in search_results1.iterrows():
                if st.sidebar.button(f"{row['title']} ({row['id']})", key=f"btn1_{idx}"):
                    st.session_state.selected_series1 = row['id']
                    st.session_state.selected_title1 = row['title']
        else:
            st.sidebar.warning("No results found. Try a different search term.")

    # Second Indicator Search
    st.sidebar.subheader("Economic Indicator 2")
    search_query2 = st.sidebar.text_input("Search for second indicator", "inflation rate")
    
    # Search results for second indicator
    if search_query2:
        search_results2 = search_indicators(fred, search_query2)
        if search_results2 is not None and not search_results2.empty:
            st.sidebar.markdown("### Top 3 Results for Indicator 2")
            for idx, row in search_results2.iterrows():
                if st.sidebar.button(f"{row['title']} ({row['id']})", key=f"btn2_{idx}"):
                    st.session_state.selected_series2 = row['id']
                    st.session_state.selected_title2 = row['title']
        else:
            st.sidebar.warning("No results found. Try a different search term.")

    # Scale adjustment controls in sidebar
    if 'selected_series1' in st.session_state and 'selected_series2' in st.session_state:
        st.sidebar.subheader("Scale Adjustment")
        st.sidebar.markdown("Adjust the scale of the second indicator for better visualization")
        
        col1, col2, col3 = st.sidebar.columns([1, 2, 1])
        with col1:
            if st.button("➖", key="minus_scale"):
                st.session_state.scale_factor *= 0.5
        with col2:
            st.markdown(f"Scale: {st.session_state.scale_factor:.2f}x")
        with col3:
            if st.button("➕", key="plus_scale"):
                st.session_state.scale_factor *= 2.0
        
        if st.sidebar.button("Reset Scale", key="reset_scale"):
            st.session_state.scale_factor = 1.0

    # Main content area
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.header("Economic Indicators Visualization")
        
        # Date range selector
        col1a, col1b = st.columns(2)
        with col1a:
            start_date = st.date_input(
                "Start Date",
                datetime.now() - timedelta(days=365),
                max_value=datetime.now()
            )
        with col1b:
            end_date = st.date_input(
                "End Date",
                datetime.now(),
                max_value=datetime.now()
            )

        # Plot selected series
        if 'selected_series1' in st.session_state and 'selected_series2' in st.session_state:
            try:
                # Get data for both indicators
                data1 = get_series_data(fred, st.session_state.selected_series1, 
                                     start_date=start_date, end_date=end_date)
                data2 = get_series_data(fred, st.session_state.selected_series2, 
                                     start_date=start_date, end_date=end_date)
                
                if data1 is not None and data2 is not None and len(data1) > 0 and len(data2) > 0:
                    # Create the plot
                    fig, ax = plt.subplots(figsize=(12, 6))
                    ax.plot(data1.index, data1.values, 'b-', label=st.session_state.selected_title1)
                    ax.plot(data2.index, data2.values * st.session_state.scale_factor, 'r-', 
                           label=f"{st.session_state.selected_title2} (×{st.session_state.scale_factor:.2f})")
                    plt.title("Economic Indicators Comparison")
                    plt.xlabel("Date")
                    plt.ylabel("Value")
                    plt.grid(True)
                    plt.legend()
                    plt.xticks(rotation=45)
                    plt.tight_layout()
                    
                    st.pyplot(fig)
                    
                    # Calculate and display correlation (using scaled data)
                    correlation = calculate_correlation(data1, data2 * st.session_state.scale_factor)
                    if correlation is not None:
                        st.subheader("Correlation Analysis")
                        st.markdown(f"**Correlation Coefficient:** {correlation:.3f}")
                    
                    # Display data tables
                    st.subheader("Data Tables")
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown(f"**{st.session_state.selected_title1}**")
                        st.dataframe(data1.tail())
                    with col2:
                        st.markdown(f"**{st.session_state.selected_title2}**")
                        st.dataframe(data2.tail())
                else:
                    st.warning("No data available for one or both indicators in the selected date range.")
                
            except Exception as e:
                st.error(f"Error processing data: {str(e)}")
        else:
            st.info("Select two indicators from the search results to visualize.")

    with col2:
        st.header("Popular Indicators")
        popular_indicators = {
            "Unemployment Rate (USA)": "UNRATE",  # Changed from LNS14000000
            "GDP Growth Rate (USA)": "GDPC1",
            "Inflation Rate (USA)": "CPIAUCSL",
            "Interest Rate (USA)": "FEDFUNDS",
            "Industrial Production": "INDPRO",
            "Retail Sales": "RSXFS",  # Changed from RRSFS
            "Housing Starts": "HOUST",
            "Personal Savings Rate": "PSAVERT"
        }
        
        st.subheader("Select First Indicator")
        for idx, (title, series_id) in enumerate(popular_indicators.items()):
            if st.button(f"1: {title}", key=f"pop1_{idx}"):
                st.session_state.selected_series1 = series_id
                st.session_state.selected_title1 = title
        
        st.subheader("Select Second Indicator")
        for idx, (title, series_id) in enumerate(popular_indicators.items()):
            if st.button(f"2: {title}", key=f"pop2_{idx}"):
                st.session_state.selected_series2 = series_id
                st.session_state.selected_title2 = title

    # Footer
    st.markdown("---")
    st.markdown("""
    Data source: Federal Reserve Economic Data (FRED)
    """)

if __name__ == "__main__":
    main() 