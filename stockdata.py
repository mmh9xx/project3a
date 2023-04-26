import requests
import json
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
from datetime import datetime
import re

# Input validation functions
def validate_symbol(symbol):
    return bool(re.match(r'^[A-Z]{1,7}$', symbol))

def validate_chart_type(chart_type):
    return chart_type in ('1', '2')

def validate_time_series(time_series):
    return time_series in ('1', '2', '3', '4')

def validate_date(date_str):
    try:
        datetime.strptime(date_str, '%Y-%m-%d')
        return True
    except ValueError:
        return False

def get_stock_data(symbol, time_series, start_date, end_date, api_key):
    base_url = "https://www.alphavantage.co/query"
    payload = {
        "function": time_series,
        "symbol": symbol,
        "outputsize": "full",
        "apikey": api_key
    }
    if time_series == 'TIME_SERIES_INTRADAY':
        payload['interval'] = '5min'

    response = requests.get(base_url, params=payload)
    response.raise_for_status()

    data = json.loads(response.text)

    if time_series == 'TIME_SERIES_INTRADAY':
        time_series = 'Time Series (5min)'
    elif time_series == 'TIME_SERIES_DAILY_ADJUSTED':
        time_series = 'Time Series (Daily)'
    elif time_series == 'TIME_SERIES_WEEKLY':
        time_series = 'Weekly Time Series'
    elif time_series == 'TIME_SERIES_MONTHLY':
        time_series = 'Monthly Time Series'
    else:
        raise ValueError("Invalid time series")

    open_key = '1. open'
    high_key = '2. high'
    low_key = '3. low'
    close_key = '4. close'

    dates = []
    open_prices = []
    high_prices = []
    low_prices = []
    close_prices = []

    for date_str in data[time_series]:
        if time_series == 'Time Series (5min)':
            date_format = '%Y-%m-%d %H:%M:%S'
        else:
            date_format = '%Y-%m-%d'

        date = datetime.strptime(date_str, date_format)
        if date >= start_date and date <= end_date:
            dates.append(date)
            open_str = data[time_series][date_str][open_key]
            high_str = data[time_series][date_str][high_key]
            low_str = data[time_series][date_str][low_key]
            close_str = data[time_series][date_str][close_key]
            open_prices.append(float(open_str))
            high_prices.append(float(high_str))
            low_prices.append(float(low_str))
            close_prices.append(float(close_str))

    return dates, open_prices, high_prices, low_prices, close_prices
