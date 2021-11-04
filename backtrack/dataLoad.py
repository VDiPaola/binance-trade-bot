import datetime
from io import open
import csv
from binance.client import Client
MARKET = "XRPUSDT"

client = Client("test", "test", tld='us')

csvFile = open(MARKET+"_alltime15Mins.csv", "w",  newline="")
candle = csv.writer(csvFile, delimiter=",")

candlesticks = client.get_historical_klines(MARKET, client.KLINE_INTERVAL_15MINUTE, "1 jan 2010", datetime.datetime.today().strftime("%d %b %Y"))

for candlestick in candlesticks:
    candlestick[0] = candlestick[0] / 1000
    candle.writerow(candlestick)

csvFile.close()