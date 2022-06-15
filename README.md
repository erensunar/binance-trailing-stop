# Binance Trailing Stop Bot

Install the libraries in the 'Requirements.txt' file.
Create a database via Firebase.
Database files 'signal' > 'channel1' > {
"apiKey" (string): "",
"apiSecret" (string): "",
"botRun" (boolean): "",
"money" (number): 1,
"stopLoss" (number): 1,
"symbol" (string): "",
"targetProfit" (number): 1}

should be in the form

botRun: Set True to receive. It won't do anything with a false value.

money: Specifies the balance to be used for trading

stopLoss: The stop loss rate. % aspect. Example 1.2, 1.2% down from current price

targetProfit: Target profit rate. % aspect. Example 1.5 is 1.5% above the current price.

The bot reads from the database approximately once a second and checks the signal. We have 50000 reads per day in Firebase free version. If you want to run 24/7, you need to upgrade the package.

https://cloud.google.com/firestore/pricing?authuser=0

After creating the server, upload the server information as 'credentials.json' to the location of the bot.

After botRun is True, it will buy the specified coin.
It sells all the coins he has at the buy stage.
