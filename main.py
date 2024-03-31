import requests
import pandas as pd 
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
from prophet import Prophet


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


def plot_btc_candle(stock_prices):
    fig = plt.figure()
    up_prices = stock_prices[stock_prices.close >= stock_prices.open] 
    down_prices = stock_prices[stock_prices.close < stock_prices.open] 
    plt.bar(up_prices.index, up_prices.close - up_prices.open, width=0.3, bottom=up_prices.open, color='green', label='Up Prices') 
    plt.bar(up_prices.index, up_prices.high - up_prices.close, width=0.03, bottom=up_prices.close, color='green') 
    plt.bar(up_prices.index, up_prices.low - up_prices.open, width=0.03, bottom=up_prices.open, color='green') 
    plt.bar(down_prices.index, down_prices.close - down_prices.open, width=0.3, bottom=down_prices.open, color='red', label='Down Prices') 
    plt.bar(down_prices.index, down_prices.high - down_prices.open, width=0.03, bottom=down_prices.open, color='red') 
    plt.bar(down_prices.index, down_prices.low - down_prices.close, width=0.03, bottom=down_prices.close, color='red') 
    plt.xticks(stock_prices.index, stock_prices['date'], rotation=30, ha='right')
    plt.ylabel("USD", fontsize=16)
    plt.xlabel("Date", fontsize=16)
    plt.title(f"USD/BTC daily chart from {return_start_end_date(btc_price_history)[0]} to {return_start_end_date(btc_price_history)[1]}")
    plt.show()


#settings
btc_hist_val = 1500
predict_days_val = 300
btc_price_history = fetch_btc_price_for_x_days(btc_hist_val)
stock_prices = convert_to_pandas(btc_price_history)

#prophet forecast prep
prophet_train_model = stock_prices[['date', 'close']].rename(columns={'date' : 'ds', 'close' : 'y'})
stock_prices = stock_prices[['date', 'close']].set_index('date')
model = Prophet()
model.fit(prophet_train_model)
future_df = model.make_future_dataframe(periods=predict_days_val)
forecast = model.predict(future_df)
forecast = forecast.drop(list(range(0, btc_hist_val+1)))
forecast = forecast[['ds', 'yhat']].rename(columns={'ds' : 'date', 'yhat' : 'close'})
forecast['date'] = forecast['date'].dt.strftime('%Y/%m/%d')
forecast = forecast.set_index('date')

#ploting
x_spacing = int((btc_hist_val+predict_days_val)/10)
print(stock_prices)
print(forecast)
plt.figure(figsize=(10, 5))
plt.plot(stock_prices, color="green", label="BTC price")
plt.plot(forecast, color="blue", label="BTC predicted price")
plt.title("BTC price forecasting")
plt.xlabel('Date')
plt.ylabel('BTC/USD')
plt.xticks(range(0, (len(stock_prices.index) + len(forecast.index) + 1), x_spacing))
plt.legend()
plt.show()