# Import necessary libraries
import pandas as pd
from apscheduler.schedulers.blocking import BlockingScheduler
from oandapyV20 import API
import oandapyV20.endpoints.orders as orders
from oandapyV20.contrib.requests import MarketOrderRequest, TakeProfitDetails, StopLossDetails
from oanda_candles import Pair, Gran, CandleClient
from API_key import key, id

# Define a function to generate trading signals based on price patterns
def signal_generator(df):
    # Ensure the DataFrame has exactly two rows (two candles)
    if len(df) != 2:
        return 0

    # Extract Open and Close prices for current and previous candles
    open = df.Open.iloc[1]
    close = df.Close.iloc[1]
    previous_open = df.Open.iloc[0]
    previous_close = df.Close.iloc[0]

    # Define bearish and bullish patterns and return corresponding signals
    if(open > close and previous_open < previous_close and close < previous_open and open >= previous_close):
        return 1  # Bearish signal
    elif(open < close and previous_open > previous_close and close > previous_open and open <= previous_close):
        return 2  # Bullish signal
    else:
        return 0  # No clear pattern

# Function to retrieve the last 'n' candles for EUR/USD with 15-minute granularity
def get_candles(n):
    access_token = key
    client = CandleClient(access_token, real=False)
    collector = client.get_collector(Pair.EUR_USD, Gran.M15)
    candles = collector.grab(n)
    return candles

# Fetch the last 3 candles and check if their open price is greater than 1
candles = get_candles(3)
for candle in candles:
    print(float(str(candle.bid.o)) > 1)

# Define the main trading job function
def trading_job():
    candles = get_candles(3)
    dfstream = pd.DataFrame(columns=["Open", "Close", "High", "Low"])

    # Populate DataFrame with Open, Close, High, Low values from the candles
    i = 0
    for candle in candles:
        dfstream.loc[i, ["Open"]] = float(str(candle.bid.o))
        dfstream.loc[i, ["Close"]] = float(str(candle.bid.o))
        dfstream.loc[i, ["High"]] = float(str(candle.bid.h))
        dfstream.loc[i, ["Low"]] = float(str(candle.bid.l))
        i += 1

    # Convert the data types to float
    dfstream["Open"]  = dfstream["Open"].astype(float)
    dfstream["Close"] = dfstream["Close"].astype(float)
    dfstream["High"]  = dfstream["High"].astype(float)
    dfstream["Low"]   = dfstream["Low"].astype(float)

    # Generate a trading signal based on the latest two candles
    signal = signal_generator(dfstream.iloc[:-1, :])

    # Set up API client using OANDA's API
    accountID = id
    client = API(key)

    # Define risk management parameters
    SLTPRatio = 2  # Stop Loss to Take Profit ratio
    previous_candleR = abs(dfstream["High"].iloc[-2] - dfstream["Low"].iloc[-2])  # Range of the previous candle

    # Calculate Stop Loss and Take Profit values
    SLBuy = float(str(candle.bid.o)) - previous_candleR
    SLSell = float(str(candle.bid.o)) + previous_candleR
    TPBuy = float(str(candle.bid.o)) + previous_candleR * SLTPRatio
    TPSell = float(str(candle.bid.o)) - previous_candleR * SLTPRatio

    print(dfstream.iloc[:-1, :])
    print(TPBuy, " ", SLBuy, " ", TPSell, " ", SLBuy)

    # Execute sell or buy order based on the signal
    if signal == 1:  # Sell signal
        mo = MarketOrderRequest(instrument="EUR_USD", units=-1000, takeProfitOnFill=TakeProfitDetails(price=TPSell).data, stopLossOnFill=StopLossDetails(price=SLSell).data)
        r = orders.OrderCreate(accountID, data=mo.data)
        rv = client.request(r)
        print(rv)
    elif signal == 2:  # Buy signal
        mo = MarketOrderRequest(instrument="EUR_USD", units=1000, takeProfitOnFill=TakeProfitDetails(price=TPBuy).data, stopLossOnFill=StopLossDetails(price=SLBuy).data)
        r = orders.OrderCreate(accountID, data=mo.data)
        rv = client.request(r)
        print(rv)

# Execute the trading job function once to start
trading_job()

# Set up a scheduler to run the trading job at specific times
scheduler = BlockingScheduler()
scheduler.add_job(trading_job, "cron", day_of_week="mon-fri", hour="00-23", minute="1,16,31,46", start_date="2023-12-27 12:00:00", timezone="America/Toronto")
scheduler.start()  # Start the scheduler
