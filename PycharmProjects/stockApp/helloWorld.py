import yfinance as fy
import pandas as pd

print("Hello World")

data = fy.download(tickers='VFV.TO', start='2000-01-01', end='2025-05-13')

pd.set_option("display.max_rows", None)

print(data)
print(type(data))

dividend_data = fy.Ticker('VFV.TO').dividends
print(dividend_data)

# 2012-12-27 00:00:00-05:00    0.149, stock price close at 20.767181 per share
# you have 486 shares, so you will get paid 0.149 x 486 = $72.414 in dividend
# if you chose to reinvest your dividend, automatically, they will buy more shares for you
# so you will have 72.414 / 20.767181 = 3 shares + some leftover cash
# Now, you have 489 shares and some leftover cash

# 2013-03-22 00:00:00-04:00    0.109
# this time, your dividend income is: 489 x 0.109 = 53.301
# closing price at that time is: 23.733500