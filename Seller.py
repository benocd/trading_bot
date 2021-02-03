from Buda import BudaHMACAuth
from Functions import *
import requests.auth
import sqlite3

# BUDA Ticker
market_id = 'btc-clp'
url = f'https://www.buda.com/api/v2/markets/{market_id}/ticker'
auth = BudaHMACAuth('API KEY HERE', 'API SECRET HERE')
response = requests.get(url, auth=auth)
buda_data = response.json()["ticker"]
buda_last_price = buda_data["last_price"][0]
buda_min_ask = buda_data["min_ask"][0]
buda_max_bid = buda_data["max_bid"][0]
print('Last Price: ' + '\033[33m' + buda_last_price + '\033[39m' + '\tMin Ask: ' + '\033[31m' + buda_min_ask + '\033[39m' + '\tMax Bid: ' + '\033[32m' + buda_max_bid + '\033[39m')

# https://docs.python.org/3/library/sqlite3.html
conn = sqlite3.connect('trades.db')
c = conn.cursor()

# Buda Order
def PlaceOrderBuda(order_type,limit,amount):
    ord_url = f'https://www.buda.com/api/v2/markets/{market_id}/orders'
    response = requests.post(ord_url, auth=auth, json={
        'type': order_type,
        'price_type': 'limit',
        'limit': limit,
        'amount': amount,
    })
    resp = response.json()
    write_log('log.txt',str(resp))

# Sell
def SellPos(id,amount,price):
    print("ID:",id, '\033[33m' + 'Sell order created.',str(amount)+' BTC @ $'+str(price)+' CLP' + '\033[39m')

    # Place Sell order
    PlaceOrderBuda('Ask',price,amount)

    # Set position inactive
    c.execute(f"UPDATE Positions SET Active = 0 WHERE TweetID = {id}")

# Check if there's any position to sell
c.execute("SELECT * FROM Positions WHERE Active = 1")
rows = c.fetchall()

# Analize each row
for row in rows:
    tID = row[0]
    entryPrice = row[2]
    amntBTC = row[3]
    stopLoss = row[4]
    minSell = row[5]
    maxPrice = row[6]

    print("ID:",tID,"Entry Price (CLP):",entryPrice,"amount (BTC):",amntBTC,"Stop Loss:",stopLoss,"Min Sell:",minSell,"Max Price:",maxPrice)

    # Check stop loss
    if (float(buda_last_price) <= stopLoss):
        print("ID:",tID, '\033[31m' + 'STOP LOSS ACTIVATED! - Place sell order at $' + buda_last_price + '\033[39m')
        write_log('log.txt','ID:'+tID+' STOP LOSS ACTIVATED!')
        SellPos(tID,amntBTC,buda_last_price)

    # Check take profit
    if (float(buda_last_price) > minSell and float(buda_last_price) <= (maxPrice * 0.995)):
        print("ID:",tID, '\033[32m' + 'TAKE PROFIT ACTIVATED! - Place sell order at $' + buda_last_price + '\033[39m')
        write_log('log.txt','ID:'+tID+' TAKE PROFIT ACTIVATED!')
        SellPos(tID,amntBTC,buda_last_price)
    
    # Check new high
    if (float(buda_last_price) > maxPrice):
        print("ID:",tID, '\033[35m' + 'NEW HIGH DETECTED! - Moved from $' + str(maxPrice) + ' ==> $' + str(buda_last_price) + '\033[39m')
        write_log('log.txt','ID:'+tID+'NEW HIGH DETECTED! - Moved from $' + str(maxPrice) + ' ==> $' + str(buda_last_price))
        c.execute(f"UPDATE Positions SET Max_price = {float(buda_last_price)} , Stop_loss = {float(buda_last_price) * 0.98} WHERE TweetID = {tID}")

# Save (commit) the changes and close the DB
conn.commit()
conn.close()