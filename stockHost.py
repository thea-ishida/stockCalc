import streamlit as st
import pandas as pd
from decimal import Decimal #for decimal precision
import math
import yfinance as fy
from datetime import datetime
import time


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
    tot_shares = shares# c
    left_over_cash = 0 #(D)
    drip_data = []
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


def split_analysis(splits, selected_stock):
    st.subheader("Stock Split History")
    number_splits = len(splits)
    st.write(f"**Stock Splits**: {number_splits}")

    if number_splits > 0:
        recent_split_date = splits.index[-1].strftime('%Y-%m-%d')
        st.write(f"**Most Recent Split Date**: {recent_split_date}")
    else:
        st.write("This stock has no recorded splits.")


    st.subheader("Stock Split Evaluation")
    if number_splits == 0:
        st.info("This company has never split its stock")
    elif number_splits < 3:
        st.success("This company has had a few stock splits")
    elif number_splits >= 3:
        st.success("This company has had multiple stock splits. Investor confidence")
    return



def write_report(selected_stock):
    company_name = selected_stock.info['longName']
    business_summary = selected_stock.info.get('longBusinessSummary', 'Summary not available.')
    sector = selected_stock.info.get('sector', 'Sector not available.')
    industry = selected_stock.info.get('industry', 'Industry not available.')

    splits = selected_stock.splits #as a series
    split_analysis(splits, selected_stock)

    st.subheader("Company Overview")
    st.write(f"**Company Name**: {company_name}")
    st.write(f"**Sector**: {sector}")
    st.write(f"***Business Summary***: {business_summary}")
    st.write(f"*Industry*: {industry}")

    return
# As of rn, the investment total value chart depends on stock dividend payouts
# for stock that don't pay dividends (amazon, or Netflix) the chart doesn't display at all.
# as a user i would like to see the chart even for non dividend paying stocks. In the case
# of Google per screenshot above, the chart only shows data starting from when it began paying dividends
# July 2024. I'd like it to extend back to my selected start date. can this be improved?

def non_dividend_growth_data(selected_stock, shares, start_date, end_date):
    history = selected_stock.history(start=start_date, end=end_date) #represent as a dataframe

    history = history[["Close"]].copy() #keep only closing price for each date
    # get the total dollar value of the investment on each day, store in a new column called total_value
    history["total_value"] = history["Close"] * shares #calculate the total value of the investment
    history.index = pd.to_datetime(history.index)
    return history[["total_value"]]

def main():
    #sidebar inputs
    st.sidebar.header("Enter your stock information")
    ticker= st.sidebar.text_input("Enter stock ticker (e.g. AAPL):","AAPL")
    amount = st.sidebar.number_input("Initial Investment", min_value=0.0, value=0.0)
    start_date = st.sidebar.text_input("Start Date", "2012-02-01")
    end_date = st.sidebar.text_input("End Date", "2025-06-02")
    use_drip = st.sidebar.checkbox("Use DRIP (Reinvest Dividends)", value=True)
    calculate_button = st.sidebar.button("Calculate")

    if calculate_button:
        with st.spinner("Running full stock analysis.."):
            errors = check_valid_inputs(ticker, amount, start_date, end_date)
            if errors:
                for error in errors:
                    st.error(error)
                    return

        selected_stock = fy.Ticker(ticker)
        st.write(f"Started with an initial investment of: $", amount)
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

        if (new_dividends.empty or new_dividends.sum() == 0) and use_drip:
            st.warning("This stock does not pay dividends — DRIP (Dividend Reinvestment Plan) is not applicable.")

        purchased_shares = determineShares(amount, start_date, selected_stock, end_date)

        #price_growth_df = non_dividend_growth_data(selected_stock, 0, start_date, end_date)

        price_growth_df = non_dividend_growth_data(selected_stock, purchased_shares, start_date, end_date)

        if new_dividends.empty:
            st.info("This stock does not produce any dividends.")
            price_data = selected_stock.history(start=end_date, end=end_date)
            price_data = price_data[price_data.index <= pd.to_datetime(end_date)]


            if not price_data.empty:
                last_valid_row = price_data.iloc[-1]
                last_valid_date = price_data.index[-1].strftime('%Y-%m-%d')
                end_price = last_valid_row["Close"]

                st.warning(f"No trading data available on {end_date} (possibly a weekend or holiday).")
                st.write(f"Most recent price data available before {end_date} was on {last_valid_date}")
                st.write(f"Stock price on {last_valid_date}: ${end_price:.2f}")
            else:
                st.error("No historical price data available before the end date.")
                return

            current_value = (purchased_shares * end_price)
            st.write(f"Stock price on {end_date:}", end_price)
            st.write(f"Final investment value: ${current_value:.2f}")

            #df = non_dividend_growth_data(selected_stock, purchased_shares, start_date, end_date)

            if not price_growth_df.empty:
                st.subheader("Investment Growth Until End Date")
                st.line_chart(price_growth_df['total_value'])
            return

        #if stock pays dividends
        current_total = Decimal("0.0")  # holds running total
        total_dividends = Decimal("0.0")  # track the payout

        for date, dividends_per_share in new_dividends.items():
            div_as_decimal = Decimal(str(dividends_per_share))
            div_total, current_total = calculate_div_growth(purchased_shares, div_as_decimal, current_total)
            total_dividends += div_total  # add up dividend payouts from each payment

        st.write("Total dividends: ", str(total_dividends))
        write_report(selected_stock)

       # st.write("use_drip is:", use_drip)

        #for DRIP
        if use_drip:
            drip_results = drip(new_dividends, selected_stock, purchased_shares, start_date, end_date)

            # get price history of entire selected period, set index of df to align with drip result
            price_history_df = selected_stock.history(start=start_date, end=end_date)[["Close"]].copy()
            price_history_df.index = pd.to_datetime(price_history_df.index)

            # Get the first available price on or after the start date
            start_ts = pd.to_datetime(start_date)

        # Ensure the index is timezone-naive
            if price_history_df.index.tz is not None:
                price_history_df.index = price_history_df.index.tz_convert(None)

            if start_ts in price_history_df.index:
                adjusted_start_date = start_ts
            else:
                adjusted_start_date = price_history_df[price_history_df.index >= start_ts].index[0]

            adjusted_start_date_row = price_history_df.loc[adjusted_start_date]  # if df is time-indexed
            initial_price = adjusted_start_date_row['Close']

            initial_total_value = purchased_shares  * initial_price
            initial_row = pd.DataFrame({
                'shares': [purchased_shares ],
                'cash': [0.0],
                'total_value': [initial_total_value]
            }, index=[adjusted_start_date])

             # convert drip_result to a dataFrame, set date as the index
            df = pd.DataFrame(drip_results)
            df['date'] = pd.to_datetime(df['date'])
            df.set_index('date', inplace=True)


            df = pd.concat([initial_row, df])
            df = df.sort_index()
            df = df.reindex(price_history_df.index, method='ffill')
            merged = price_history_df.join(df[['shares', 'cash']], how='left')
            merged[['shares', 'cash']] = merged[['shares', 'cash']].ffill().fillna(method='bfill')
            merged['total_value'] = merged['shares'] * merged['Close'] + merged['cash']

            st.subheader("Investment Growth Until End Date")
            st.line_chart(merged['total_valsue'])

        # join daily price history with drip data on dates that match,
        # how= left: adds DRIP data on dividend dates
        # fill in missing shares and cash values by copying forward the last known value, get a continuous chart

        else: # if the user does not want DRIP growth
            st.subheader("Investment Growth Without DRIP")
            st.line_chart(price_growth_df['total_value'])

        st.download_button("Download Data", price_growth_df.to_csv(), file_name="investment_data.csv")

main()
