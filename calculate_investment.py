import yfinance as fy
import pandas as pd

print("hello world ")

def get_dividends(stock):
    return fy.Ticker(stock).dividends

def get_info(stock):
    return fy.Ticker(stock).info

def get_starting_investment(starting_amount):
    initial= input(f"Enter{starting_amount}")
    return initial


def simulated_investment(stock, start_date, end_date,starting_amount, data):
    print(f"Simulated investment for {stock}")
    print(start_date, end_date, starting_amount)

    close_price = data["Close"]
    print("closing price ", close_price.head())




    return

def get_date_input(label):
    year = input(f"Enter {label} year (YYYY): ")
    month = input(f"Enter {label} month (M or MM): ").zfill(2)
    day = input(f"Enter {label} day (D or DD): ").zfill(2)
    return f"{year}-{month}-{day}"

def main():
    ticker = 'AAPL'
    start_date = get_date_input("start")
    end_date = get_date_input("end")
    starting_amount = get_starting_investment(" initial investment")

    data = fy.download(tickers=ticker, start=start_date, end=end_date)
    pd.set_option("display.max_rows", None)

    dividends = get_dividends(ticker)
    print(f"{ticker} dividend history: \n", dividends.head())
    #find a way to let user pick start date and end date

    simulated_investment(ticker, start_date, end_date, starting_amount, data)

main()