from Buda import BudaHMACAuth
from Mindicador import Mindicador
from Twitter import *
from Functions import *
import requests.auth
import sqlite3

# Precio del Dolar
usd_clp = Mindicador("dolar").InfoApi()
val_usd_clp = float(usd_clp["serie"][0]["valor"])
print(usd_clp["serie"][0], val_usd_clp)

# BUDA Ticker
market_id = 'btc-clp'
url = f'https://www.buda.com/api/v2/markets/{market_id}/ticker'
auth = BudaHMACAuth('API KEY HERE', 'API SECRET HERE')
response = requests.get(url, auth=auth)
buda_data = response.json()["ticker"]
last_price = buda_data["last_price"][0]
print(response.json())

# https://docs.python.org/3/library/sqlite3.html
conn = sqlite3.connect('trades.db')
c = conn.cursor()

# Update max values in trades
c.execute(f"UPDATE Positions SET Max_price = {last_price} WHERE Max_price < {last_price} AND Active = 1")

# Check if there's any position to sell
c.execute(f"SELECT * FROM Positions WHERE Min_sell < {last_price} AND (Max_price*0.95) > {last_price} AND Active = 1 OR Stop_loss >= {last_price} AND Active = 1")
rows = c.fetchall()
for row in rows:
    print("SELL",row)
    # TODO Place Sell order
    # ...

    # Set position inactive
    c.execute(f"UPDATE Positions SET Active = 0 WHERE TweetID = {row[0]}")

# Retrieve tweets
tweets = get_all_tweets("ThePsychoBot")
for tweet in tweets:
    if (tweet[2].find('PSYCHO BOT ALERT') != -1):
        # Remove emojis from tweet
        tweetTxt = deEmojify(tweet[2])
        # Remove dollar sign
        tweetTxt = re.sub('[!@#$]', '', tweetTxt)
        # Remove line breaks
        splitText = tweetTxt.split("\n\n")
        # Split signal text
        signal = splitText[2].split(" ")
        print(tweet, splitText, signal)

        # changes in bd
        new_signal = False
        try:
            # Insert a row of data
            values = [tweet[0], tweet[1], tweet[2], splitText[1], signal[0], signal[2]]
            c.execute("INSERT INTO Tweet VALUES (?,?,?,?,?,?)", values)
            new_signal = True
        except Exception as e:
            print("Error: " + str(e))
        
        if new_signal:
            tweet_value_in_clp = val_usd_clp*float(signal[2])
            
            med = median(float(buda_data["min_ask"][0]),float(buda_data["max_bid"][0]))
            
            # For comparison
            print("tweet_value_in_clp",tweet_value_in_clp,"med",med,"last_price",last_price)
            # TODO Create new order
            # ...
            
            # Set to 5% profit
            stop_loss = tweet_value_in_clp*0.95
            min_sell = tweet_value_in_clp*1.05
            print("New BUY signal: ", new_signal)
            # write into positions table
            try:
                values = [tweet[0],None,tweet_value_in_clp,0,stop_loss,min_sell,last_price,1]
                c.execute("INSERT INTO Positions VALUES (?,?,?,?,?,?,?,?)", values)
            except Exception as e:
                print("Error: " + str(e))


# Save (commit) the changes
conn.commit()

# We can also close the connection if we are done with it.
# Just be sure any changes have been committed or they will be lost.
conn.close()