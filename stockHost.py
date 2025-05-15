import streamlit as st

header = st.container()

with header:
    st.title('Welcome to Thea compound interest calculator')


def main():
    st.sidebar.header("Enter your stock symbol")
    ticker = st.sidebar.text_input("Stock Symbol", "AAPL")
    start_date = st.sidebar.text_input("Start Date", "2012-01-01")
    end_date = st.sidebar.text_input("End Date", "2025-05-13")


main()
