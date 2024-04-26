import requests
import pandas as pd 
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
from prophet import Prophet
import mysql.connector
from mysql.connector import errorcode


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


#prophet forecast
def make_forecast(stock_prices):
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
def plot_with_forecast(stock_prices):
    stock_prices, forecast = make_forecast(stock_prices)
    #print(stock_prices)
    #print(forecast)
    plt.figure(figsize=(10, 5))
    plt.plot(stock_prices, color="green", label="BTC price")
    plt.plot(forecast, color="blue", label="BTC predicted price")
    plt.title(f"BTC price forecasting {datetime.today().strftime('%Y-%m-%d')}")
    plt.xlabel('Date')
    plt.ylabel('BTC/USD')
    plt.xticks(range(0, (len(stock_prices.index) + len(forecast.index) + 1), x_spacing))
    plt.legend()
    plt.show()


def create_database(cursor):
    try:
        cursor.execute(
            "CREATE DATABASE {} DEFAULT CHARACTER SET 'utf8'".format(DB_NAME))
    except mysql.connector.Error as err:
        print("Failed creating database: {}".format(err))
        exit(1)

    try:
        cursor.execute("USE {}".format(DB_NAME))
    except mysql.connector.Error as err:
        print("Database {} does not exists.".format(DB_NAME))
        if err.errno == errorcode.ER_BAD_DB_ERROR:
            create_database(cursor)
            print("Database {} created successfully.".format(DB_NAME))
            cnx.database = DB_NAME
        else:
            print(err)
            exit(1)


def check_table_data(_user='root', _password='', _host='127.0.0.1', _database='test', table='snapshot'):
    try:
        cnx = mysql.connector.connect(user=_user, password=_password,
                              host=_host,
                              database=_database)
        cursor = cnx.cursor()
        query = f"SELECT EXISTS(SELECT 1 FROM {table} LIMIT 1)"
        cursor.execute(query)
        result = cursor.fetchone()
        return not bool(result[0])
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return False
    finally:
        if cnx.is_connected():
            cursor.close()
            cnx.close()


def upload_database(_user='root', _password='', _host='127.0.0.1', _database='test'):
    cnx = mysql.connector.connect(user=_user, password=_password,
                              host=_host,
                              database=_database)
    cursor = cnx.cursor()

    DB_NAME = "XD_Test"
    TABLES = {}
    TABLES['hist_data'] = (
        f"CREATE TABLE `snapshot{datetime.today().strftime('%Y%m%d')}` ("
        "  `id_no` int(11) NOT NULL AUTO_INCREMENT,"
        "  `date` date NOT NULL,"
        "  `open` FLOAT(11, 2) NOT NULL,"
        "  `close` FLOAT(11, 2) NOT NULL,"
        "  `low` FLOAT(11, 2) NOT NULL,"
        "  `high` FLOAT(11, 2) NOT NULL,"
        "  PRIMARY KEY (`id_no`)"
        ") ENGINE=InnoDB")
    TABLES['pred_data'] = (
        f"CREATE TABLE `snapshot{datetime.today().strftime('%Y%m%d')}_prediction` ("
        "  `id_no` int(11) NOT NULL AUTO_INCREMENT,"
        "  `date` date NOT NULL,"
        "  `prediction` FLOAT(11, 2) NOT NULL,"
        "  PRIMARY KEY (`id_no`)"
        ") ENGINE=InnoDB")

    #run make DB
    for table_name in TABLES:
        table_description = TABLES[table_name]
        try:
            print("Creating table {}: ".format(table_name), end='')
            cursor.execute(table_description)  
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_TABLE_EXISTS_ERROR:
                print("Table already exists.")
            else:
                print(err.msg)
        else:
            print("OK")
    cursor.close()
    cnx.close()

def upload_data_to_db(data, _user='root', _password='', _host='127.0.0.1', _database='test'):
    cnx = mysql.connector.connect(user=_user, password=_password,
                              host=_host,
                              database=_database)
    cursor = cnx.cursor()

    add_hist_data = (f"INSERT INTO snapshot{datetime.today().strftime('%Y%m%d')}"
                "(date, open, close, low, high) "
                "VALUES (%s, %s, %s, %s, %s)")

    add_pred = (f"INSERT INTO snapshot{datetime.today().strftime('%Y%m%d')}_prediction"
                "(date, prediction) "
                "VALUES (%s, %s)")

    #commit hist data
    if check_table_data(table = f"snapshot{datetime.today().strftime('%Y%m%d')}"):
        for entry in convert_to_dict(data):
            cursor.execute(add_hist_data, (entry['date'], entry['open'], entry['close'], entry['low'], entry['high']))
        cnx.commit()
        print(f"snapshot{datetime.today().strftime('%Y%m%d')} collected!")
    else:
        print(f"snapshot{datetime.today().strftime('%Y%m%d')} already exists!")

    #commit pred data
    if check_table_data(table = f"snapshot{datetime.today().strftime('%Y%m%d')}_prediction"):
        stock, pred = make_forecast(convert_to_pandas(data))
        pred = pred.to_dict()['close']
        for entry_key in pred.keys():
            cursor.execute(add_pred, (entry_key, pred[entry_key]))
        cnx.commit()
        print(f"snapshot{datetime.today().strftime('%Y%m%d')}_prediction collected!")
    else:
        print(f"snapshot{datetime.today().strftime('%Y%m%d')}_prediction already exists!")

    #close connection
    cursor.close()
    cnx.close()
    

#wrapper for snapshot
def collect_snapshot(btc_price_history):
    upload_database()
    upload_data_to_db(btc_price_history)


#settings
btc_hist_val = 1500
predict_days_val = 300
btc_price_history = fetch_btc_price_for_x_days(btc_hist_val)
x_spacing = int((btc_hist_val+predict_days_val)/10)
menu = True

while(menu):
    print("""
    ### Menu ###
    1) Get data for today from API
    2) Save snapshot to DB
    3) Load and plot snapshot
    """)
    usr_in = input()
    match int(usr_in):
        case 1:
            plot_with_forecast(convert_to_pandas(btc_price_history))
        case 2:
            collect_snapshot(btc_price_history)
        case 3:
            pass
        case _:
            menu = False
