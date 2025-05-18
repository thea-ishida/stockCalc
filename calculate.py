from decimal import Decimal #for decimal precision
import yfinance as fy
import pandas as pd

print("Hello world")

def get_stock_name():
    company = fy.Ticker(input("Enter a Stock Name: "))
    return company

def get_history(name): #need to change this later
    history = name.history(start='2023-02-01')
    pd.set_option("display.max_columns", None)
    return history

def get_closing_value(history):
    first_record = history.iloc[0]
    return first_record["Close"]

def get_first_div(name, start="2023-02-01"):
    #get all dividends
    dividends = name.dividends
    dividends = dividends[dividends.index >= start]
    if dividends.empty:
        return 0.0
    return Decimal(str(dividends.iloc[0]))

def share_amount():
    shares = (input("Enter the Number of Shares Purchased: "))
    return shares


def calculate_div_growth(shares, dividend_per_share):
    total_dividend = (float(shares) * float(dividend_per_share))
    print(f"Total Dividend: {total_dividend}")
    return total_dividend

def buy_more_shares(dividend_revenue, closing_value):
    updated_shares = float(dividend_revenue)/closing_value
    return updated_shares

def main():
    name = get_stock_name() #create a stock object
    shares = share_amount()
    print(shares)
    history = get_history(name)
    print("--------------------------------")
    closing_price = get_closing_value(history)
    #div_data = get_first_div(name)
    print("the closing price", closing_price)
    print("==============================")
    div_on_feb2 = get_first_div(name, "2023-02-01")
    print("Dividend on 2023-02-01:", div_on_feb2)

    result = calculate_div_growth(shares, div_on_feb2)
    print("dividend revenue", result)

    #next assume user wants to re-invest the dividend automatically, automate buying shares
    print(buy_more_shares(result, closing_price))

main()