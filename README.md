# Economic Indicators Analysis Tool

This is a teaching tool for students to learn about economic data analysis using the Federal Reserve Economic Data (FRED) API.

## Setup Instructions

1. Make sure you have Python 3.7 or higher installed on your computer.

2. Install the required packages using pip:
   ```bash
   pip install -r requirements.txt
   ```

3. Get a FRED API key:
   - Go to https://research.stlouisfed.org/docs/api/api_key.html
   - Sign up for a free account
   - Request an API key
   - Replace the default API key in the code with your own

## Usage

### Interactive Web Dashboard

1. Run the Streamlit dashboard:
   ```bash
   streamlit run app.py
   ```

2. The dashboard will open in your default web browser with the following features:
   - Search for economic indicators
   - Select from popular indicators
   - Customize date range
   - View interactive visualizations
   - See data tables

### Command Line Tool

1. Run the command line version:
   ```bash
   python economy-fred-analysis.py
   ```

2. Choose from the following options:
   - Search for a ticker (e.g., "unemployment rate USA")
   - Plot single economic indicator
   - Compare multiple countries' indicators
   - Exit

3. Follow the prompts to:
   - Enter search terms
   - Select ticker IDs
   - Create visualizations
   - Save data to CSV files

## Features

- Interactive web dashboard
- Search functionality for economic indicators
- Date range selection
- Interactive visualizations
- Data tables
- Popular indicators quick access
- Data export to CSV format
- Error handling and user feedback
- Automatic output directory creation

## Example Ticker IDs

Here are some common economic indicators you can try:
- Unemployment Rate (USA): LNS14000000
- GDP Growth Rate (USA): GDPC1
- Inflation Rate (USA): CPIAUCSL
- Interest Rate (USA): FEDFUNDS
- Consumer Price Index: CPIAUCSL
- Industrial Production: INDPRO
- Retail Sales: RRSFS
- Housing Starts: HOUST

## Output

All downloaded data will be saved in the `output` directory:
- Daily data: `output/[ticker_id].csv`
- Quarterly data: `output/[ticker_id]_quarterly.csv` 