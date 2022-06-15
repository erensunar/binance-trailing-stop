import firebase_admin
import ccxt
import pandas as pd
from firebase_admin import credentials,firestore
import threading
credentialData = credentials.Certificate("credentials.json")
firebase_admin.initialize_app(credentialData)
firestoreDb = firestore.client()
inPosition = False
global botWork


callback_done = threading.Event()
snapshots = list(firestoreDb.collection(u'signal').get())
channel1 = snapshots[0]
data = channel1.to_dict()
botWork = data["botRun"]


def on_snapshot(col_snapshot, changes, read_time):
    global botWork, data
    for change in changes:
        if change.type.name == 'MODIFIED':
            print(f'Modified: {change.document.id}')
            snapshots = list(firestoreDb.collection(u'signal').get())
            channel1 = snapshots[0]
            data = channel1.to_dict()
            botWork = data["botRun"]


def strategy():
    while True:
        print("Waiting")
        if botWork:
            apiKey = data["apiKey"]
            apiSecret = data["apiSecret"]
            symbol = data["symbol"]
            money = data["money"]
            stopLoss = data["stopLoss"]
            targetProfit = data["targetProfit"]
            exchange = ccxt.binance({
                "apiKey": apiKey,
                "secret": apiSecret,

                'options': {
                'defaultType': 'spot'
                },
                'enableRateLimit': True
                })
            
            while botWork:
    
                try:
                    
                    
                    balance = exchange.fetch_balance()
                    
                    bars = exchange.fetch_ohlcv(symbol, timeframe="1m", since = None, limit = 1)
                    df = pd.DataFrame(bars, columns=["timestamp", "open", "high", "low", "close", "volume"])

                    currentPrice = float(df["close"][len(df.index) - 1])


                    def longEnter(amount):
                        global targetPrice,stopLossPrice,inPosition
                        order = exchange.create_market_buy_order(symbol, amount)
                        price = order["price"]
                        lastPrice = price
                        targetPrice = price + ((float(price) / 100) * targetProfit) 
                        stopLossPrice = price - ((float(price) / 100) * stopLoss) 
                        inPosition = True

                    def longExit():
                        global inPosition
                        order = exchange.create_market_sell_order(symbol, float(balance["total"][symbol.split("USDT")[0]]))
                        inPosition = False

                    if not inPosition:
                        print("Signal received, purchase is processing.")
                        amount = float( money / currentPrice)
                        longEnter(amount)
                    
                    if inPosition and currentPrice <= stopLossPrice:
                        print("Stop loss order executed.")
                        longExit()
                        firestoreDb.collection("signal").document("channel1").update({"botRun": False})

                    

                    
                    if  inPosition and currentPrice >= targetPrice:
                        print("The target has been reached. The stop loss  increased by "+ str(stopLoss)+  ".Target price increased by " +str(targetProfit) + ".")
                        stopLossPrice = stopLossPrice + (float(stopLossPrice / 100) * stopLoss)
                        targetPrice = targetPrice + ((float(targetPrice) / 100) * targetProfit) 
                    
                    if inPosition:
                        print("Price: "+ str(currentPrice))
                        print("Stop Loss Price: " + str(stopLossPrice))
                        print("Target Price: " + str(targetPrice))
                        print("=======================================================================================================================================")
                except ccxt.BaseError as Error:
                    print ("[ERROR] ", Error )
                    continue

col_query = doc_ref = firestoreDb.collection(u'signal').document(u'channel1')
query_watch = col_query.on_snapshot(on_snapshot)
def control():
    import time
    global query_watch
    while True:
        time.sleep(0.02)
        query_watch
thread = threading.Thread(target=control)
thread.start()
thread2 = threading.Thread(target=strategy)
thread2.start()