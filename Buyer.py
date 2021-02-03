from Buda import BudaHMACAuth
from Functions import *
import requests.auth
import sqlite3

write_log('log.txt','Starting Buyer.py')

auth = BudaHMACAuth('API KEY HERE', 'API SECRET HERE')
balances_json = requests.get('https://www.buda.com/api/v2/balances', auth=auth).json()['balances']
ticker_json = requests.get('https://www.buda.com/api/v2/markets/btc-clp/ticker', auth=auth).json()

conn = sqlite3.connect('trades.db')

try:
    balances = {}
    for bal in balances_json:
        balances[bal['available_amount'][1]] = float(bal['available_amount'][0])

    last_price = float(ticker_json['ticker']['last_price'][0])
    print(balances,last_price)

    # Try limit buy
    ## BID = PAY CLP AND GET BTC

    # Use only 5% of money available
    amnt = (balances['CLP']*0.25)/last_price

    bid = requests.post('https://www.buda.com/api/v2/markets/btc-clp/orders', auth=auth, json={
        'type': 'Bid',
        'price_type': 'limit',
        'limit': last_price,
        'amount': amnt,
    })
    ord_resp = bid.json()["order"]
    write_log('log.txt',str(ord_resp))

    ord_id = int(ord_resp['id'])
    limit_clp = float(ord_resp['limit'][0])
    amount_btc = float(ord_resp['amount'][0])

    c = conn.cursor()
    c.execute(f"INSERT INTO Positions values ({ord_id}, null, {limit_clp}, {amount_btc}, {limit_clp*0.98}, {limit_clp*1.05}, {limit_clp}, 1)")
except Exception as e:
    write_log('log.txt','Error: ' + str(e))
    print("Error: " + str(e))

conn.commit()
conn.close()

write_log('log.txt','Finished script execution Buyer.py')
## ASK = Sell BTC and get CLP
