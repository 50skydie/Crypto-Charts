import requests

def get_btc_for_x_days(x):    
    url = f'https://min-api.cryptocompare.com/data/v2/histoday?fsym=BTC&tsym=USD&limit={x}'
    response = requests.get(url)
    print(response)
    
    if response.status_code == 200:
        data = response.json()['Data']
        return data
    else:
        print("Failed to fetch BTC price history!")
        return None

btc_price_history = get_btc_for_x_days(90)
print(btc_price_history)