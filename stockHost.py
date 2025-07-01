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
# def determineShares(amount, startDate, selected_stock, end_date):
#     stockHistory = get_history(selected_stock, startDate, end_date)
#     # get the closing price closest to/on the starting date
#     closeDate, price = stockHistory[0]
#     st.write(f"Stock price on {closeDate}: ${price:.2f}")
#     shares = math.floor(float(amount)/ price)
#     st.write(f"Number of shares you purchased: {shares}")
#     return shares


def determineShares(amount, startDate, closePrice):
    currentDate = str(startDate)[0:10]
    #print(currentDate, "CURRENT DATE")

    priceOnStartDate = closePrice[currentDate]
    print("close price at current date --- ", priceOnStartDate)

    shares = math.floor((float(amount) / priceOnStartDate))
   # print(f"Number of shares you purchased: {shares}")
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

def write_report(selected_stock):
    company_name = selected_stock.info.get('longName', 'N/A')
    business_summary = selected_stock.info.get('longBusinessSummary', 'Summary not available.')
    sector = selected_stock.info.get('sector', 'Sector not available.')
    industry = selected_stock.info.get('industry', 'Industry not available.')

    st.markdown("## 🏢 Company Overview")

    # Use columns to make it more compact and clean
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"**📛 Company Name:** {company_name}")
        st.markdown(f"**🏭 Industry:** {industry}")
    with col2:
        st.markdown(f"**🏷️ Sector:** {sector}")

    # Add a separator and formatted business summary
    st.markdown("---")
    st.markdown("### 📘 Business Summary")
    st.markdown(f"<div style='text-align: justify;'>{business_summary}</div>", unsafe_allow_html=True)
    return

# As of rn, the investment total value chart depends on stock dividend payouts
# for stock that don't pay dividends (amazon, or Netflix) the chart doesn't display at all.
# as a user i would like to see the chart even for non dividend paying stocks. In the case
# of Google per screenshot above, the chart only shows data starting from when it began paying dividends
# July 2024. I'd like it to extend back to my selected start date. can this be improved?

# def non_dividend_growth_data(selected_stock, shares, start_date, end_date):
#
#     history = selected_stock.history(start=start_date, end=end_date) #represent as a dataframe
#
#     history = history[["Close"]].copy() #keep only closing price for each date
#     # get the total dollar value of the investment on each day, store in a new column called total_value
#     history["total_value"] = history["Close"] * shares #calculate the total value of the investment
#     history.index = pd.to_datetime(history.index)
#     return history[["total_value"]]


def SplitHistoryAnalysis(stockSplits, shares):
    st.subheader("Stock Split History")
    if not stockSplits:
        st.write("This stock has not split during this period")
        return

    split_count = 0
    split_info = []

    for date, ratio in stockSplits.items():
        if ratio != 0:
            split_count += 1
            split_info.append((date, ratio))

    df_splits = {}

    for key, value in stockSplits.items():
        new_key = str(key)[0:10]
        df_splits[new_key] = value

    df = pd.DataFrame(df_splits.items(), columns = ["Date", "Split Ratio"])
    st.dataframe(df, use_container_width=True, hide_index=True)

    print(split_count, "here is the split_count")
    if split_count > 0:
        st.success(f"This company has had {split_count} stock splits.")

    current_shares = shares
    total_shares = current_shares
    print("CURRENT SHARES --> ", current_shares)
    for date, split_ratio in split_info:
        new_shares = (current_shares * split_ratio)
        print("New shares ", new_shares)

        total_shares += new_shares
        print("total_shares: ", total_shares)


    st.success(f"You now have {total_shares} number of shares")


   # by the end of the chart, display how many shares we have now
   # ex with apple stock : 1 share becomes 2 -> 2 x 7 x 4  = 56 shares
   #
 \


def main():
    '''
    Take data from yahoo finance, throw it into a dictionary of my own choice,
    the dictionary should only have the data we need from the dataframe
    throughout my entire program, use the data accordingly so we don't have to make multiple API calls

    :return:
    '''

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
        stock_df = selected_stock.history(start=start_date, end=end_date)
        split_series = stock_df["Stock Splits"]
        split_series = split_series[split_series != 0]  # Only actual splits
        split_series.index = split_series.index.astype(str)


        data_dictionary = {
            "name": selected_stock, #stored an a y-finance object
            "start_date": start_date,
            "end_date": end_date,
            "starting_amount": amount,
            "dates": stock_df.index,
            "closePrice": stock_df["Close"],
            "Dividends": stock_df["Dividends"],
            "StockSplits": split_series.to_dict()
        }
       # st.write(data_dictionary)

        # Company Overview
        write_report(selected_stock)

        # Split history
        shares = determineShares(amount, start_date, data_dictionary.get("closePrice"))

        SplitHistoryAnalysis(data_dictionary.get("StockSplits"), shares)

        # get shares

        #use drip
        #drip(Dividends, selected_stock, )
main()
