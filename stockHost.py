import streamlit as st
import pandas as pd
from decimal import Decimal #for decimal precision
import math
import yfinance as fy


header = st.container()

with header:
    st.title('Welcome to Thea compound interest calculator')


def calculate_div_growth(shares, dividend_per_share, current_sum):
    total_dividend = Decimal(str(shares)) * dividend_per_share
    cash_total = current_sum + total_dividend
    return total_dividend, cash_total

def main():

    st.sidebar.header("Enter your stock symbol")
    ticker = st.sidebar.text_input("Stock Symbol", "AAPL")
    start_date = st.sidebar.text_input("Start Date", "2024-05-05")
    end_date = st.sidebar.text_input("End Date", "2025-05-13")
    currentValue = 500
    st.write("Started with 500 shares today", currentValue)
    selected_stock = fy.Ticker(ticker)
    print("the selected stock", selected_stock)

    # look up dividends the company paid since
    dividends = selected_stock.dividends
    starting_day = pd.to_datetime(start_date)

    # calculate the number of times you receive the dividend and add up the total sum
    timezone = dividends.index.tz
    if timezone is not None:
        starting_day = starting_day.tz_localize(timezone)
    else:
        starting_day = starting_day.localize(None)

    # keep dividend payments that happened after the starting date
    new_dividends = dividends[dividends.index >= starting_day]
    print(f"new dividends since {starting_day}", new_dividends)

    current_total = Decimal("0.0")  # holds running total
    total_dividends = Decimal("0.0")  # track the payout

    # loop through each day of dividend payment
    for date, dividends_per_share in new_dividends.items():
        div_as_decimal = Decimal(str(dividends_per_share))
        #calculate_div_growth(currentValue, div_as_decimal, current_total)
        div_total, current_total = calculate_div_growth(currentValue, div_as_decimal, current_total)
        #print(div_total, current_total)
        total_dividends += div_total  # add up dividend payouts from each payment

    st.write("Total dividends: ", str(total_dividends))

main()
