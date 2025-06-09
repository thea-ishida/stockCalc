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

    #if not dividend_collection:
    #    st.info("The stock you selected did not pay any dividends during the selected period.")
     #   return []

    tot_shares = shares# c
    left_over_cash = 0 #(D)
    drip_data = []
    #print("Starting amount of shares: ", tot_shares)

    price_history = dict(get_history(selected_stock, starting_day, end_date)) # store in a dictionary to get key, value

    for starting_day, dividend_per_share in dividend_collection.items():
        date_str = starting_day.strftime("%Y-%m-%d")
        tot_div = Decimal(str(dividend_per_share)) * tot_shares #total dividends received
        available_cash = tot_div + left_over_cash

        if date_str not in price_history:
            print(f"No stock price found for {date_str}")
            continue

        price = Decimal(str(price_history[date_str])) # closing price

        if available_cash >=  price:
            new_shares = available_cash // price       # (C) to get as many shares as we can if we can afford with our current available cash
            left_over_cash = available_cash % price    # (D)   a % b = a - (a // b) * b
            tot_shares += new_shares                   # Update (A)
        else:
            left_over_cash = available_cash

        total_value = (tot_shares * price) + left_over_cash

        drip_data.append({
            'date': date_str,
            'shares': float(tot_shares),
            'price': float(price),
            'cash': float(left_over_cash),
            'total_value': float(total_value)
        })

    st.write("Current Cash Value: ", total_value)

    return drip_data

        # if the amt (B) is large enough to purchase a share or more on this date (per close price)
        # you would make this buy, let's call the number of shares bough (C) and leftover cash (D)
        # at this point, you need to track the current number of shares (A) = (A) + (C) and
        # leftover cash (D)

        # if the amt (B) is not enough to purchase a new share, put it into the leftover cash (D)
        # Track the current leftover cash with (B) = (B) + (D)
        # Do this until the (B) is large enough to purchase a new share of the stock then do so


def main():
    #sidebar inputs
    st.sidebar.header("Enter your stock information")
    ticker= st.sidebar.text_input("Enter stock ticker (e.g. AAPL):","AAPL")
    amount = st.sidebar.number_input("Initial Investment", min_value=0.0, value=0.0)
    start_date = st.sidebar.date_input("Start Date").strftime("%Y-%m-%d")
    end_date = st.sidebar.date_input("End Date").strftime("%Y-%m-%d")

    calculate_button = st.sidebar.button("Calculate")

    if calculate_button:
        # handling invalid inputs
        errors = check_valid_inputs(ticker, amount, start_date, end_date)
        if errors:
            for error in errors:
                st.error(error)
                return

        selected_stock = fy.Ticker(ticker)

        st.write(f"Started with an initial investment of: $", amount)

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
        new_dividends = selected_stock.dividends.loc[start_date:end_date]
        # print("new dividends: ----> ", new_dividends)
        if new_dividends.empty:
            #print("This stock does not produce any dividends.")
            st.info("This stock does not produce any dividends.")
            return


        current_total = Decimal("0.0")  # holds running total
        total_dividends = Decimal("0.0")  # track the payout

        data = []
        shares_from_initial = determineShares(amount, starting_day.strftime("%Y-%m-%d"), selected_stock, end_date)
        # print(shares_from_initial, "SHARES FROM INITIAL")

        for date, dividends_per_share in new_dividends.items():
            div_as_decimal = Decimal(str(dividends_per_share))
            div_total, current_total = calculate_div_growth(shares_from_initial, div_as_decimal, current_total)
            total_dividends += div_total  # add up dividend payouts from each payment



        st.write("Total dividends: ", str(total_dividends))

        #for DRIP
        drip_results = drip(new_dividends, selected_stock, shares_from_initial, start_date, end_date)
        df = pd.DataFrame(drip_results)
        df['date'] = pd.to_datetime(df['date'])
        df.set_index('date', inplace=True)

        st.subheader("Investment Growth Until End Date")
        st.line_chart(df['total_value'])


main()
