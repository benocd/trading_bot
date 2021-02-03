# trading_bot

Only sell is automated. Run Seller.py for testing.
For auto exec. create a new cron job like this:
    * * * * * cd /home/pi/trading_bot && python3 Seller.py

Before using you must buy BTC and insert the data manually into trades.db (table Positions, ignore table Tweets).

Example:
    INSERT INTO Positions (CURRENT_TIMESTAMP, null, 24363306.7, 0.0025, 23886861.04, 25593065.4, 24363306.7, 1)
