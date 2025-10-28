#!/usr/bin/python3
import requests
import pandas as pd 
import numpy as np
import matplotlib.pyplot as plt
import os
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


#prophet forecast
def make_forecast(stock_prices, predict_days_val):
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
    return stock_prices, forecast


#make forecast and plot
def plot_with_forecast(stock_prices, predict_days_val):
    stock_prices, forecast = make_forecast(convert_to_pandas(stock_prices), predict_days_val)
    fig_hist, ax = plt.subplots(figsize=(10, 5)) #fig_snap, ax = plt.subplots(figsize=(10, 5))
    ax.plot(stock_prices, color="green", label="BTC price")
    ax.plot(forecast, color="blue", label="BTC predicted price")
    ax.set_title(f"BTC price forecasting {datetime.today().strftime('%Y-%m-%d')}")
    ax.set_xlabel('Date')
    ax.set_ylabel('BTC/USD')
    plt.xticks(range(0, (len(stock_prices.index) + len(forecast.index) + 1), x_spacing))
    ax.legend()
    plt.show()

        
#wrapper for snapshot
def collect_snapshot(btc_price_history):
    upload_database()
    upload_data_to_db(btc_price_history)


#settings
btc_hist_val = 1500
predict_days_val = 300
x_spacing = int((btc_hist_val+predict_days_val)/11)
menu = True


while(menu):
    print("""
    ### Menu ###
    1) Get data for today from API
    """)
    usr_in = input()
    os.system('cls')
    match int(usr_in):
        case 1:
            plot_with_forecast(fetch_btc_price_for_x_days(btc_hist_val), predict_days_val)
        case _:
            menu = False
