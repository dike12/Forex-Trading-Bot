import yfinance as yf
import pandas as pd

dataF = yf.download("EURUSD=X", start="2023-11-25", end="2023-12-24", interval="15m")
dataF.iloc[-1:, :]
dataF.Open.iloc

def signal_generator(df):
    if len(df) != 2:
        return 0

    open = df.Open.iloc[1]
    close = df.Close.iloc[1]
    previous_open = df.Open.iloc[0]
    previous_close = df.Close.iloc[0]

    #bearish pattern 
    if(open > close and previous_open < previous_close and close < previous_open and open >= previous_close):
        return 1
    
    #bullish pattern
    elif(open < close and previous_open > previous_close and close > previous_open and open <= previous_close):
        return 2
    
    #No clear pattern
    else:
        return 0
    

signal = []
signal.append(0)
for i in range(1, len(dataF)):
    df = dataF[i-1: i+1]
    signal.append(signal_generator(df))

if len(signal) < len(dataF):
    signal.append(0) 

#signal generator(data)
dataF["signal"] = signal

from apscheduler.schedulers.blocking import BlockingScheduler
from oandapyV20 import API
import oandapyV20.endpoints.orders as orders
from oandapyV20.contrib.requests import MarketOrderRequest
from oanda_candles import Pair, Gran, CandleClient
from oandapyV20.contrib.requests import TakeProfitDetails, StopLossDetails
from API_key import key, id


def get_candles(n):
    access_token = key
    client = CandleClient(access_token, real=False)
    collector = client.get_collector(Pair.EUR_USD, Gran.M15)
    candles = collector.grab(n)
    return candles

candles = get_candles(3)

for candle in candles:
    print(float(str(candle.bid.o)) > 1)

def trading_job():
    candles = get_candles(3)
    dfstream = pd.DataFrame(columns=["Open", "Close", "High", "Low"])

    i = 0
    for candle in candles:
        dfstream.loc[i, ["Open"]] = float(str(candle.bid.o))
        dfstream.loc[i, ["Close"]] = float(str(candle.bid.o))
        dfstream.loc[i, ["High"]] = float(str(candle.bid.h))
        dfstream.loc[i, ["Low"]] = float(str(candle.bid.l))
        i = i+1

    dfstream["Open"]  = dfstream["Open"].astype(float)
    dfstream["Close"]  = dfstream["Close"].astype(float)
    dfstream["High"]  = dfstream["High"].astype(float)
    dfstream["Low"]  = dfstream["Low"].astype(float)

    signal = signal_generator(dfstream.iloc[:-1, :])

    #Executing Orders
    accountID = id
    client = API(key)

    SLTPRatio = 2
    previous_candleR = abs(dfstream["High"].iloc[-2] - dfstream["Low"].iloc[-2])

    SLBuy = float(str(candle.bid.o)) - previous_candleR
    SLSell = float(str(candle.bid.o)) + previous_candleR

    TPBuy = float(str(candle.bid.o)) + previous_candleR * SLTPRatio
    TPSell = float(str(candle.bid.o)) - previous_candleR * SLTPRatio

    print(dfstream.iloc[:-1, :])
    print(TPBuy, " ", SLBuy, " ", TPSell, " ", SLBuy)

    signal = 1

    #sell
    if signal == 1: 
        mo = MarketOrderRequest(instrument="EUR_USD", units=-1000, takeProfitOnFill=TakeProfitDetails(price=TPSell).data, stopLossOnFill=StopLossDetails(price=SLSell).data)
        r = orders.OrderCreate(accountID, data=mo.data)
        rv = client.request(r)
        print(rv)

    #Buy
    elif signal == 2:
        mo = MarketOrderRequest(instrument="EUR_USD", units=1000, takeProfitOnFill=TakeProfitDetails(price=TPBuy).data, stopLossOnFill=StopLossDetails(price=SLBuy).data)
        r = orders.OrderCreate(accountID, data=mo.data)
        rv = client.request(r)
        print(rv)

trading_job()

scheduler = BlockingScheduler()
scheduler.add_job(trading_job, "cron", day_of_week="mon-fri", hour="00-23", minute="1,16,31,46", start_date="2023-12-27 12:00:00", timezone="Eastern standard time")
scheduler.start()