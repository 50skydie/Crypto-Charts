#!/usr/bin/python3

import requests
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
from prophet import Prophet


# Fetch BTC price for the last x days
def fetch_btc_price_for_x_days(x):    
    url = f'https://min-api.cryptocompare.com/data/v2/histoday?fsym=BTC&tsym=USD&limit={x}'
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()['Data']['Data']
        return data
    else:
        print("Failed to fetch BTC price history!")
        return None


# Convert fetched BTC data to a Pandas DataFrame
def convert_to_pandas(btc_price_array):
    data = []
    for entry in btc_price_array:
        data.append({
            "date": datetime.utcfromtimestamp(entry['time']).strftime('%Y-%m-%d'),
            "open": entry['open'], "close": entry['close'], "low": entry['low'], "high": entry['high']
        })
    return pd.DataFrame(data)


# Make forecast using Prophet
def make_forecast(stock_prices, predict_days_val):
    prophet_train_model = stock_prices[['date', 'close']].rename(columns={'date': 'ds', 'close': 'y'})
    model = Prophet()
    model.fit(prophet_train_model)
    future_df = model.make_future_dataframe(periods=predict_days_val)
    forecast = model.predict(future_df)
    forecast = forecast.drop(list(range(0, len(stock_prices))))
    forecast = forecast[['ds', 'yhat']].rename(columns={'ds': 'date', 'yhat': 'close'})
    forecast['date'] = forecast['date'].dt.strftime('%Y/%m/%d')
    forecast = forecast.set_index('date')
    return stock_prices, forecast


# Plot BTC price with forecast
def plot_with_forecast(stock_prices, predict_days_val):
    stock_prices_df = convert_to_pandas(stock_prices)
    stock_prices, forecast = make_forecast(stock_prices_df, predict_days_val)
    
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(stock_prices['date'], stock_prices['close'], color="green", label="BTC price")
    ax.plot(forecast.index, forecast['close'], color="blue", label="BTC predicted price")
    ax.set_title(f"BTC Price Forecasting ({datetime.today().strftime('%Y-%m-%d')})")
    ax.set_xlabel('Date')
    ax.set_ylabel('BTC/USD')
    ax.legend()

    #x-ticks tweak
    total_points = len(stock_prices['date']) + len(forecast.index)
    combined_dates = list(stock_prices['date']) + list(forecast.index)
    if total_points > 1:
        step = max(1, total_points // 10)
        ax.set_xticks(range(0, total_points, step))
        ax.set_xticklabels([combined_dates[i] for i in range(0, total_points, step)], rotation=60, ha='right')

    fig.tight_layout()
    return fig