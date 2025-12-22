from logic import fetch_btc_price_for_x_days, make_forecast, convert_to_pandas
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt


def test_data_prep(number_of_days, tested_days):
    test_data = fetch_btc_price_for_x_days(number_of_days + tested_days - 1)
    input_data = test_data[:-tested_days]
    check_data= test_data[-tested_days:]
    return (input_data, check_data)


historical_days = 1000
prediction_days = 365
input_data, check_data = test_data_prep(historical_days, prediction_days)
check_data_df = convert_to_pandas(check_data)
input_data_df = convert_to_pandas(input_data)
data, prediction = make_forecast(input_data_df, prediction_days)
fig, ax = plt.subplots(figsize=(10, 5))
ax.plot(
    data['date'],
    data['close'],
    color="green",
    label="BTC price"
)
ax.plot(
    prediction.index,
    check_data_df['close'],
    color="red",
    label="real BTC price"
)
ax.plot(
    prediction.index,
    prediction['close'],
    color="blue",
    label="BTC predicted price"
)
ax.plot(
    prediction.index,
    prediction['lower'],
    color="cyan",
    linestyle="--",
    label="BTC predicted price lower error"
)
ax.plot(
    prediction.index,
    prediction['upper'],
    color="cyan",
    linestyle="--",
    label="BTC predicted price upper error"
)
ax.fill_between(
    prediction.index,
    prediction['lower'],
    prediction['upper'],
    color='cyan',
    alpha=0.3,
    label='Prediction error area'
)
ax.set_title(f"BTC TEST Forecasting ({datetime.today().strftime('%Y-%m-%d')})")
ax.set_xlabel('Date')
ax.set_ylabel('BTC/USD')
ax.legend()
total_points = len(data['date']) + len(prediction.index)
combined_dates = list(data['date']) + list(prediction.index)
if total_points > 1:    #xticks tweak
    step = max(1, total_points // 10)
    ax.set_xticks(range(0, total_points, step))
    ax.set_xticklabels([combined_dates[i] for i in range(0, total_points, step)], rotation=60, ha='right')

fig.tight_layout()
plt.show()
