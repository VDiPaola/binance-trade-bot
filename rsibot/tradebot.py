from builtins import len, Exception, float

import websocket, json, talib, numpy, datetime, config, StrategyExtension, sys, MarketExtension
from binance.client import Client
from binance.enums import *

#exit if no market was entered as command line argument
if len(sys.argv) < 2 or (len(sys.argv) >= 2 and MarketExtension.get_market(sys.argv[1])) == False:
    sys.exit(0)
MARKET = MarketExtension.get_market(sys.argv[1])
print("running on market: " + MARKET["symbol"])

SOCKET = "wss://stream.binance.com:9443/ws/"+ MARKET["symbol"].lower() +"@kline_15m"

#trade vars
TRADE_SYMBOL = MARKET["symbol"].upper()
TRADE_BUY_PRICE = 10 # in USDT

closes = []

STRATEGIES = {}
STRATEGIES["THREEMA"] = StrategyExtension.Strategy("THREEMA", TRADE_SYMBOL)
STRATEGIES["THREEMA_STOPLOSS"] = StrategyExtension.Strategy("THREEMA_STOPLOSS", TRADE_SYMBOL)
STRATEGIES["MEAN_REVERSION"] = StrategyExtension.Strategy("MEAN_REVERSION", TRADE_SYMBOL)

client = Client(api_key=config.API_KEY, api_secret=config.API_SECRET)

def order(side, usd, price, symbol,order_type=ORDER_TYPE_MARKET):
    try:
        print("sending order")
        quantity = usd / price
        order = client.create_order(symbol=symbol, side=side, type=order_type, quantity=quantity)
        print(order)
    except Exception as e:
        print("an exception occured - {}".format(e))
        return False

    return True

def on_open(ws):
    print('opened connection')

def on_close(ws):
    print('closed connection')
    #send alert email etc saying that the connection has closed

def on_message(ws, message):
    global closes, in_position,latestBoughtPrice

    obj = json.loads(message)
    candle = obj['k']
    latestPrice = float(candle['c'])
    isCandleClosed = candle['x']
    npArray = []

    if isCandleClosed:
        #add latest close
        closes.append(latestPrice)
        closes.pop()
        npArray = numpy.array(closes)
    else:
        npArray = numpy.append(closes, [latestPrice])

    # --------------------------------------------------------------------------------------------------------
    currentStrategy = "THREEMA"
    if hasattr(MARKET, currentStrategy):
        THREEMA = MARKET[currentStrategy]
        #Get MA's
        maFast = talib.MA(npArray, timeperiod=THREEMA["ma_fast_interval"])
        maSlow = talib.MA(npArray, timeperiod=THREEMA["ma_slow_interval"])
        maTrend = talib.MA(npArray, timeperiod=THREEMA["ma_trend_interval"])

        currentFast = maFast[-1]
        currentSlow = maSlow[-1]
        currentTrend = maTrend[-1]

        distanceFromTrend = latestPrice - currentTrend

        fastDifference = currentFast - maFast[-2]
        slowDifference = currentSlow - maSlow[-2]
        trendDifference = currentTrend - maTrend[-2]

        allUpwardsTrending = (fastDifference > THREEMA["gradient"] and slowDifference > THREEMA["gradient"] and trendDifference > THREEMA["gradient"])

        if STRATEGIES[currentStrategy].canTrade:
            if (distanceFromTrend < 1 or currentFast < currentSlow) and STRATEGIES[currentStrategy].in_position:
                #sell
                print("TRYING TO SELL " + currentStrategy)

                order_succeeded = order(SIDE_SELL, TRADE_BUY_PRICE, STRATEGIES[currentStrategy].latestBoughtPrice, TRADE_SYMBOL)

                if order_succeeded:
                    STRATEGIES[currentStrategy].in_position = False
                    STRATEGIES[currentStrategy].sell(TRADE_BUY_PRICE, latestPrice)


            if isCandleClosed and allUpwardsTrending and currentFast > currentSlow and distanceFromTrend < (currentTrend + (currentTrend*THREEMA["max_distance_from_trend"])) and latestPrice > currentTrend and not STRATEGIES[currentStrategy].in_position:
                #buy
                order_succeeded = order(SIDE_BUY, TRADE_BUY_PRICE, latestPrice, TRADE_SYMBOL)
                if order_succeeded:
                    STRATEGIES[currentStrategy].in_position = True
                    STRATEGIES[currentStrategy].latestBoughtPrice = latestPrice
                    STRATEGIES[currentStrategy].buy(TRADE_BUY_PRICE)

# --------------------------------------------------------------------------------------------------------
        currentStrategy = "THREEMA_STOPLOSS"
        if hasattr(MARKET, currentStrategy):
            THREEMA = MARKET[currentStrategy]
            # Get MA's
            maFast = talib.MA(npArray, timeperiod=THREEMA["ma_fast_interval"])
            maSlow = talib.MA(npArray, timeperiod=THREEMA["ma_slow_interval"])
            maTrend = talib.MA(npArray, timeperiod=THREEMA["ma_trend_interval"])

            currentFast = maFast[-1]
            currentSlow = maSlow[-1]
            currentTrend = maTrend[-1]

            distanceFromTrend = latestPrice - currentTrend

            fastDifference = currentFast - maFast[-2]
            slowDifference = currentSlow - maSlow[-2]
            trendDifference = currentTrend - maTrend[-2]

            allUpwardsTrending = (fastDifference > THREEMA["gradient"] and slowDifference > THREEMA[
                "gradient"] and trendDifference > THREEMA["gradient"])

            stoplossCondition1 = STRATEGIES[currentStrategy].stoploss != False and STRATEGIES[currentStrategy].stoploss < latestPrice-(latestPrice*THREEMA["stoploss"])
            stoplossCondition2 = STRATEGIES[currentStrategy].stoploss == False and STRATEGIES[currentStrategy].latestBoughtPrice != False and ((latestPrice - STRATEGIES[currentStrategy].latestBoughtPrice) / STRATEGIES[currentStrategy].latestBoughtPrice) *100 >= 5 + THREEMA["stoploss"]
            if STRATEGIES[currentStrategy].in_position and (stoplossCondition1 or stoplossCondition2):
                STRATEGIES[currentStrategy].stoploss = latestPrice-(latestPrice*THREEMA["stoploss"])

            if STRATEGIES[currentStrategy].canTrade:
                if (distanceFromTrend < 1 or (STRATEGIES[currentStrategy].stoploss == False and currentFast < currentSlow) or (STRATEGIES[currentStrategy].stoploss != False and latestPrice < STRATEGIES[currentStrategy].stoploss)) and STRATEGIES[currentStrategy].in_position:
                    # sell
                    print("TRYING TO SELL " + currentStrategy)
                    order_succeeded = order(SIDE_SELL, TRADE_BUY_PRICE, STRATEGIES[currentStrategy].latestBoughtPrice, TRADE_SYMBOL)
                    if order_succeeded:
                        STRATEGIES[currentStrategy].in_position = False
                        STRATEGIES[currentStrategy].stoploss = False
                        STRATEGIES[currentStrategy].sell(TRADE_BUY_PRICE, latestPrice)

                if isCandleClosed and allUpwardsTrending and currentFast > currentSlow and distanceFromTrend < (currentTrend + (currentTrend * THREEMA["max_distance_from_trend"])) and latestPrice > currentTrend and not STRATEGIES[currentStrategy].in_position:
                    # buy
                    order_succeeded = order(SIDE_BUY, TRADE_BUY_PRICE, latestPrice, TRADE_SYMBOL)
                    if order_succeeded:
                        STRATEGIES[currentStrategy].in_position = True
                        STRATEGIES[currentStrategy].latestBoughtPrice = latestPrice
                        STRATEGIES[currentStrategy].buy(TRADE_BUY_PRICE)
    #--------------------------------------------------------------------------------------------------------
    currentStrategy = "MEAN_REVERSION"
    if hasattr(MARKET, currentStrategy):
        MEAN_REVERSION = MARKET[currentStrategy]
        try:
            top, middle, bottom = talib.BBANDS(
                npArray,
                timeperiod=MEAN_REVERSION["bbands_interval"],
                # number of non-biased standard deviations from the mean
                nbdevup=2,
                nbdevdn=2,
                # Moving average type: simple moving average here
                matype=0)
        except Exception as ex:
            print("exception getting BBANDS " + str(ex))

        midRangeSize = MEAN_REVERSION["mid_range_size"]
        #enable trading if back at mean
        if not STRATEGIES[currentStrategy].canTrade:
            reachedMid = latestPrice >= (middle[-1] - middle[-1]*midRangeSize) and latestPrice <= (middle[-1] + middle[-1]*midRangeSize)
            if reachedMid:
                print("REACHED MID. CAN TRADE.")
                STRATEGIES[currentStrategy].canTrade = True

        ma = talib.MA(npArray, timeperiod=MEAN_REVERSION["trend_interval"])
        #sell conditions
        if STRATEGIES[currentStrategy].in_position:
            stoploss = latestPrice < ma[-1]
            stoplossShort = latestPrice > ma[-1]
            if not STRATEGIES[currentStrategy].short and (latestPrice >= middle[-1] - middle[-1]*midRangeSize or stoploss):
                # sell
                STRATEGIES[currentStrategy].sell(TRADE_BUY_PRICE, latestPrice)
                STRATEGIES[currentStrategy].in_position = False
                if stoploss:
                    print("STOPLOSS")
                    STRATEGIES[currentStrategy].canTrade = False

            elif STRATEGIES[currentStrategy].short and (latestPrice <= middle[-1] + middle[-1]*midRangeSize or stoplossShort):
                # sell short
                STRATEGIES[currentStrategy].sell(TRADE_BUY_PRICE, latestPrice)
                STRATEGIES[currentStrategy].in_position = False
                if stoplossShort:
                    print("STOPLOSS SHORT")
                    STRATEGIES[currentStrategy].canTrade = False
        elif isCandleClosed and STRATEGIES[currentStrategy].canTrade:
            #buy conditions
            maDifference = ma[-1] - maTrend[-2]
            maxGradient = MEAN_REVERSION["gradient"]

            maxDistanceLong = ma[-1] + ma[-1]*MEAN_REVERSION["max_distance_from_ma"]
            maxDistanceShort = ma[-1] - ma[-1]*MEAN_REVERSION["max_distance_from_ma"]
            if latestPrice > top[-1] and latestPrice < ma[-1] and maDifference < -maxGradient and latestPrice > maxDistanceShort:
                #buy short
                STRATEGIES[currentStrategy].short = True
                STRATEGIES[currentStrategy].latestBoughtPrice = latestPrice
                STRATEGIES[currentStrategy].buy(TRADE_BUY_PRICE)
                STRATEGIES[currentStrategy].in_position = True

            elif latestPrice < bottom[-1] and latestPrice > ma[-1] and maDifference > maxGradient and latestPrice < maxDistanceLong:
                #buy
                STRATEGIES[currentStrategy].short = False
                STRATEGIES[currentStrategy].latestBoughtPrice = latestPrice
                STRATEGIES[currentStrategy].buy(TRADE_BUY_PRICE)
                STRATEGIES[currentStrategy].in_position = True

    print(str(datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")) + " onMessage End")



#preload closes with last 2 days of data
startDate = datetime.date.today() - datetime.timedelta(days=3)
candlesticks = numpy.array(client.get_historical_klines(TRADE_SYMBOL, client.KLINE_INTERVAL_15MINUTE, str(startDate)))
newData = []
for candle in candlesticks:
    newData.append(float(candle[4]))
closes = newData

#websocket
ws = websocket.WebSocketApp(SOCKET, on_open=on_open, on_close=on_close, on_message=on_message)
ws.run_forever()