import requests
import pandas as pd
from scripts.utility import read_constituents as get_tickers
from typing import List
from dotenv import load_dotenv
import os


load_dotenv()


api_key = os.getenv("VANTAGE_KEY")


# Create a function to fetch cash flow data for a given symbol
def fetch_cash_flow(symbol):
    url = f"https://www.alphavantage.co/query?function=CASH_FLOW&symbol={symbol}&apikey={api_key}"
    response = requests.get(url)
    data = response.json()
    return data


# Fetch cash flow data for the top 100 symbols.
tickers = get_tickers()

all_cleaned_data = []
annual_rep_headers = []

# Fetch cash flow annual reports for top stocks
for i, symbol in enumerate(tickers):
    if i >= 110:
        break
    data = fetch_cash_flow(symbol)
    if i == 0:
        annual_rep_headers = list(data["annualReports"][0].keys())
        annual_rep_headers.insert(0, "ticker")
    cleaned_data = [symbol]
    for k in annual_rep_headers[1:]:
        cleaned_data.append(data["annualReports"][0][k])
    all_cleaned_data.append(cleaned_data)


# Convert to pandas DataFrame
df = pd.DataFrame(all_cleaned_data)
# Setting headers
df.columns = annual_rep_headers

# csv file name
csv_file = "../notebooks/data/cash_flow_data.csv"
# Save DataFrame to CSV
df.to_csv(csv_file, index=False)
