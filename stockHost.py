import streamlit as st
import pandas as pd
from decimal import Decimal #for decimal precision
import math
import yfinance as fy
from datetime import datetime


header = st.container()

with header:
    st.title('Welcome to Thea compound interest calculator')


def check_valid_inputs(ticker, amount, start_date, end_date):
    errors = []
    try:
        float(amount)
    except ValueError:
        errors.append("The initial investment must be a number")

    try:
        datetime.strptime(start_date, "%Y-%m-%d")
    except ValueError:
        errors.append("Start date must be in YYYY-MM-DD format.")

    try:
        datetime.strptime(end_date, "%Y-%m-%d")
    except ValueError:
        errors.append("End date must be in YYYY-MM-DD format")

    if not ticker.isalpha():
        errors.append("Ticker symbol must only contain letters")
    return errors


# change this to take in the initial investment
def get_history(name, start_date, end_date):
    stock_history = name.history(start=start_date, end=end_date)
    stock_close_history = []

    for key, value in stock_history["Close"].items():
        date_str = key.strftime('%Y-%m-%d')
        record = (date_str, value)
        stock_close_history.append(record)
        last_valid_price = (date_str, value)
           # print("The last valid price: ", last_valid_price)

    return stock_close_history



def calculate_div_growth(shares, dividend_per_share, current_sum):
    total_dividend = Decimal(str(shares)) * dividend_per_share
    cash_total = current_sum + total_dividend
    return total_dividend, cash_total

#function to determine how many shares were bought on the starting date
def determineShares(amount, startDate, selected_stock, end_date):
    stockHistory = get_history(selected_stock, startDate, end_date)
    # get the closing price closest to/on the starting date
    closeDate, price = stockHistory[0]
    st.write(f"Stock price on {closeDate}: ${price:.2f}")
    shares = math.floor(float(amount)/ price)
    st.write(f"Number of shares you purchased: {shares}")
    return shares


def drip(dividend_collection, selected_stock, shares, starting_day, end_date):
   # print("got here")
    tot_shares = shares# c
    left_over_cash = 0 #(D)
    drip_data = []

    price_history = dict(get_history(selected_stock, starting_day, end_date)) # store in a dictionary to get key, value

    for starting_day, dividend_per_share in dividend_collection.items():
        date_str = starting_day.strftime("%Y-%m-%d")
        #print("here:", date_str, "you will calculate the amount of dividend received (B) on this date", dividend_per_share)
        tot_div = Decimal(str(dividend_per_share)) * tot_shares #total dividends received
        available_cash = tot_div + left_over_cash

       # print("date_str", date_str)
        if date_str not in price_history:
           # print(f"No stock price found for {date_str}")
            continue

        price = Decimal(str(price_history[date_str])) # closing price
   #     print(price, "<--------", end_date)

      #  print(price)
        #if more shares can be bought
        if available_cash >=  price:
            new_shares = available_cash // price       # (C) to get as many shares as we can if we can afford with our current available cash
            left_over_cash = available_cash % price    # (D)   a % b = a - (a // b) * b
            tot_shares += new_shares                   # Update (A)
        else:
            left_over_cash = available_cash
        drip_data.append((date_str, float(tot_shares)))  # For plotting or display
       # print(drip_data, " <------------- drip data")

     #   print(left_over_cash)

    return left_over_cash

        # if the amt (B) is large enough to purchase a share or more on this date (per close price)
        # you would make this buy, let's call the number of shares bough (C) and leftover cash (D)
        # at this point, you need to track the current number of shares (A) = (A) + (C) and
        # leftover cash (D)

        # if the amt (B) is not enough to purchase a new share, put it into the leftover cash (D)
        # Track the current leftover cash with (B) = (B) + (D)
        # Do this until the (B) is large enough to purchase a new share of the stock then do so




def main():
    #sidebar inputs
    st.sidebar.header("Enter your stock symbol")
    ticker= st.sidebar.text_input("Stock Symbol", "AAPL")
    amount = st.sidebar.number_input("Initial Investment", min_value=0.0, value=0.0)
    start_date = st.sidebar.text_input("Start Date", "2022-02-01")
    end_date = st.sidebar.text_input("End Date", "2024-12-12")
    st.write(f"Started with an initial investment of: $", amount)

    errors = check_valid_inputs(ticker, amount, start_date, end_date)
    if errors:
        for error in errors:
            st.error(error)
        #print(errors)
        return

    selected_stock = fy.Ticker(ticker)
   # print("the selected stock", selected_stock)

    # look up dividends the company paid since
    dividends = selected_stock.dividends
    starting_day = pd.to_datetime(start_date)

    # calculate the number of times you receive the dividend and add up the total sum
    timezone = dividends.index.tz
    if timezone is not None:
        starting_day = starting_day.tz_localize(timezone)
    else:
        starting_day = starting_day.localize(None)

    #find the number of shares:

    # keep dividend payments that happened after the starting date
    new_dividends = dividends[dividends.index >= starting_day]
   # print(f"new dividends since {starting_day}", new_dividends)

    current_total = Decimal("0.0")  # holds running total
    total_dividends = Decimal("0.0")  # track the payout

    data = []
    shares_from_initial = determineShares(amount, starting_day.strftime("%Y-%m-%d"), selected_stock, end_date)
    #print(shares_from_initial, "SHARES FROM INITIAL")

    for date, dividends_per_share in new_dividends.items():
        div_as_decimal = Decimal(str(dividends_per_share))
        div_total, current_total = calculate_div_growth(shares_from_initial, div_as_decimal, current_total)
        total_dividends += div_total  # add up dividend payouts from each payment

        data.append((date.date(), float(current_total)))

    st.write("Total dividends: ", str(total_dividends))

    #for DRIP
    drip_result = drip(new_dividends, selected_stock, shares_from_initial, starting_day, end_date)
    st.write("Current Cash Value: ", drip_result)





    # plot the growth of the investment
    # 1. create pandas dataframe from the data which has the date and current total
    # 2. put date as dataframe index
    df = pd.DataFrame(data, columns= ["Date", "Total Dividends Collected"])
    df.set_index("Date", inplace=True)
    st.line_chart(df)

main()
