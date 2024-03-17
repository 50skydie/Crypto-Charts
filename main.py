import requests
import pandas as pd 
import matplotlib.pyplot as plt 
from datetime import datetime

def fetch_btc_price_for_x_days(x):    
    url = f'https://min-api.cryptocompare.com/data/v2/histoday?fsym=BTC&tsym=USD&limit={x}'
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()['Data']['Data']
        return data
    else:
        print("Failed to fetch BTC price history!")
        return None

def show_candle_info(btc_price_array):
    for entry in btc_price_array:
        print(f"open: {entry['open']} low: {entry['low']} high: {entry['high']}, close: {entry['close']} "
              f"date: {datetime.utcfromtimestamp(entry['time']).strftime('%Y-%m-%d')}")

def convert_to_dict(btc_price_array):
    data = []
    for entry in btc_price_array:
        data.append({"date": datetime.utcfromtimestamp(entry['time']).strftime('%Y-%m-%d'), "open": entry['open'],
                     "close": entry['close'], "low": entry['low'], "high": entry['high']})
    return data

def convert_to_pandas(btc_price_array):
    pandas_df = pd.DataFrame(convert_to_dict(btc_price_array))
    pd.set_option('display.max_rows', None)
    return pandas_df

def return_start_end_date(btc_price_array):
    return [datetime.utcfromtimestamp(btc_price_array[0]['time']).strftime('%Y-%m-%d'),
            datetime.utcfromtimestamp(btc_price_array[-1]['time']).strftime('%Y-%m-%d')]


btc_price_history = fetch_btc_price_for_x_days(7)
stock_prices = convert_to_pandas(btc_price_history)
print(return_start_end_date(btc_price_history))

plt.figure()
up_prices = stock_prices[stock_prices.close >= stock_prices.open] 
down_prices = stock_prices[stock_prices.close < stock_prices.open] 
up_color = 'green'
down_color = 'red'

# Plotting up prices of the stock 
plt.bar(up_prices.index, up_prices.close - up_prices.open, width=0.3, bottom=up_prices.open, color=up_color, label='Up Prices') 
plt.bar(up_prices.index, up_prices.high - up_prices.close, width=0.03, bottom=up_prices.close, color=up_color) 
plt.bar(up_prices.index, up_prices.low - up_prices.open, width=0.03, bottom=up_prices.open, color=up_color) 
  
# Plotting down prices of the stock 
plt.bar(down_prices.index, down_prices.close - down_prices.open, width=0.3, bottom=down_prices.open, color=down_color, label='Down Prices') 
plt.bar(down_prices.index, down_prices.high - down_prices.open, width=0.03, bottom=down_prices.open, color=down_color) 
plt.bar(down_prices.index, down_prices.low - down_prices.close, width=0.03, bottom=down_prices.close, color=down_color) 

# Set x-axis tick labels with dates
plt.xticks(stock_prices.index, stock_prices['date'], rotation=30, ha='right')
plt.ylabel("USD", fontsize=16)
plt.xlabel("Date", fontsize=16)
plt.title(f"USD/BTC daily chart from {return_start_end_date(btc_price_history)[0]} to {return_start_end_date(btc_price_history)[1]}")


plt.show() 