from flask import Flask, render_template, request, redirect, url_for
from stockdata import get_stock_data, validate_symbol, validate_chart_type, validate_time_series, validate_date
import matplotlib.pyplot as plt
import io
import base64
import matplotlib.dates as mdates
from datetime import datetime
import csv

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        symbol = request.form["symbol"]
        time_series_input = request.form["time_series"]
        start_date_str = request.form["start_date"]
        end_date_str = request.form["end_date"]
        chart_type_input = request.form["chart_type"]

        # Validating inputs
        if not (validate_symbol(symbol) and validate_time_series(time_series_input) and validate_chart_type(chart_type_input) and validate_date(start_date_str) and validate_date(end_date_str)):
            error = "Invalid input. Please ensure all fields are filled out correctly."
            return render_template("index.html", error=error)

        # Get stock data
        time_series_dict = {
            "1": "TIME_SERIES_INTRADAY",
            "2": "TIME_SERIES_DAILY_ADJUSTED",
            "3": "TIME_SERIES_WEEKLY",
            "4": "TIME_SERIES_MONTHLY",
        }
        time_series = time_series_dict.get(time_series_input)
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
        api_key = '9UL3ZIO409JYQX26'
        dates, open_prices, high_prices, low_prices, close_prices = get_stock_data(symbol, time_series, start_date, end_date, api_key)

        # Generate chart
        img = io.BytesIO()
        fig, ax = plt.subplots(figsize=(10, 5))

        if chart_type_input == "1":
            ax.plot(dates, close_prices, label="Close")
            ax.plot(dates, open_prices, label="Open")
            ax.plot(dates, low_prices, label="Low")
            ax.plot(dates, high_prices, label="High")
        elif chart_type_input == "2":
            ax.bar(dates, close_prices, label="Close", alpha=0.3)
            ax.bar(dates, open_prices, label="Open", alpha=0.3)
            ax.bar(dates, low_prices, label="Low", alpha=0.3)
            ax.bar(dates, high_prices, label="High", alpha=0.3)

        if time_series == 'TIME_SERIES_INTRADAY':
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M'))
            plt.xticks(rotation=45)
        else:
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
            plt.xticks(rotation=45)

        ax.set_xlabel('Date')
        ax.set_ylabel('Price ($)')
        ax.set_title(f'{symbol} Stock Prices')
        ax.legend()
        plt.tight_layout()
        plt.savefig(img, format='png')
        img.seek(0)
        plot_url = base64.b64encode(img.getvalue()).decode()

        return render_template("stock.html", plot_url=plot_url)
    return render_template("stock.html")

def indexs():
    # read data from CSV file
    with open('stocks.csv', 'r') as file:
        reader = csv.reader(file)
        symbol = [row[0].strip() for row in reader]

    # render HTML template with dropdown menu
    return render_template('stock.html', symbol=symbol)

if __name__ == "__main__":
    app.run()
