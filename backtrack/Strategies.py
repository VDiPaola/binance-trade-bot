import math

import backtrader as bt
import backtrader.indicators
from random import uniform, randint
buyAmount = 0.072 #~£100 for BTC
highThreshold=0#4.5
lowThreshold=0#3

class StrategyExtension:

    def __init__(self, strategySettings):
        self.boughtAt = 0
        self.returnsPercent = 0
        self.lowestLow = 0
        self.highestHigh = 0
        self.numberOfHighs = 0
        self.numberOfLows = 0
        self.tradeCount = 0
        self.position = False
        self.strategySettings = strategySettings

    def sell(self, value):
        change = value - self.boughtAt
        percent = (change / self.boughtAt) * 100
        if percent > 0 and percent > self.highestHigh:
            self.highestHigh = percent
        elif percent < 0 and percent < self.lowestLow:
            self.lowestLow = percent
        if percent > highThreshold:
            self.numberOfHighs += 1
        elif percent < -lowThreshold:
            self.numberOfLows += 1
        self.returnsPercent += percent
        self.tradeCount += 1
        self.position = False

    def buy(self,value):
        self.position = True
        self.boughtAt = value

def generateTHREEMA():
    #vars
    fastPeriodMin = 50
    fastPeriodMax = 75
    slowPeriodMin = 70
    slowPeriodMax = 100
    trendPeriodMin = 150
    trendPeriodMax = 300
    gradientMin = 0
    gradientMax = 0.002
    maxDistanceFromTrendMin = 0.005
    maxDistanceFromTrendMax = 0.03
    maxLastExitMin = 0
    maxLastExitMax = 20

    #generate random variables
    fastTimeperiod = randint(fastPeriodMin, fastPeriodMax)
    slowTimePeriod = randint(slowPeriodMin, slowPeriodMax)
    trendTimePeriod = randint(trendPeriodMin, trendPeriodMax)
    gradient = uniform(gradientMin, gradientMax)
    maxDistanceFromTrend = uniform(maxDistanceFromTrendMin, maxDistanceFromTrendMax)
    maxLastExit = randint(maxLastExitMin, maxLastExitMax)

    #return object
    return{
        "name": "THREEMA",
        "fastTimeperiod": fastTimeperiod,
        "slowTimeperiod": slowTimePeriod,
        "trendTimeperiod": trendTimePeriod,
        "gradient": gradient, #min slope steepness to enter
        "maxDistanceFromTrend": maxDistanceFromTrend,
        "maxLastExit" : maxLastExit #number of bars that need to go by after an exit before it can enter again(can prevent multiple bad trades)
    }

class THREEMA(bt.Strategy):

    params = (('strategySettings', None),)

    def __init__(self):
        self.fast = bt.talib.MA(self.data, timeperiod=math.ceil(self.params.strategySettings["fastTimeperiod"]))
        self.slow = bt.talib.MA(self.data, timeperiod=math.ceil(self.params.strategySettings["slowTimeperiod"]))
        self.trend = bt.talib.MA(self.data, timeperiod=math.ceil(self.params.strategySettings["trendTimeperiod"]))
        self.lastExit = 0
        self.prevFast = False
        self.prevSlow = False
        self.prevTrend = False
        self.stoploss = -9999
        self.strategyExtension = StrategyExtension(self.params.strategySettings)


    def next(self):
        if self.prevFast != False and self.prevSlow != False and self.prevTrend != False:
            self.lastExit += 1
            distanceFromTrend = self.data.close - self.trend
            fastDifference = self.fast - self.prevFast
            slowDifference = self.slow - self.prevSlow
            trendDifference = self.trend - self.prevTrend
            gradient = self.params.strategySettings["gradient"]
            allUpwardsTrending = (fastDifference > gradient and slowDifference > gradient and trendDifference > gradient)

            #sell
            if (distanceFromTrend < 1 or self.fast < self.slow or self.data.close < self.stoploss) and self.strategyExtension.position:
                self.strategyExtension.sell(self.data.close + 0)
                self.lastExit = 0
                self.close()

            #buy
            if allUpwardsTrending and self.lastExit > self.params.strategySettings["maxLastExit"] and self.fast > self.slow and distanceFromTrend < (self.trend + self.trend*self.params.strategySettings["maxDistanceFromTrend"]) and self.data.close > self.trend and not self.strategyExtension.position:
                self.strategyExtension.buy(self.data.close + 0)
                self.stoploss = self.trend
                self.buy(size=buyAmount)

        self.prevFast = self.fast + 0
        self.prevSlow = self.slow + 0
        self.prevTrend = self.trend + 0

def generateTHREEMA_STOPLOSS():
    #vars
    fastPeriodMin = 50
    fastPeriodMax = 75
    slowPeriodMin = 70
    slowPeriodMax = 100
    trendPeriodMin = 150
    trendPeriodMax = 300
    gradientMin = 0
    gradientMax = 0.01
    maxDistanceFromTrendMin = 0.005
    maxDistanceFromTrendMax = 0.03
    maxLastExitMin = 0
    maxLastExitMax = 20
    stoplossMin = 0.1
    stoplossMax = 8

    #generate random variables
    fastTimeperiod = randint(fastPeriodMin, fastPeriodMax)
    slowTimePeriod = randint(slowPeriodMin, slowPeriodMax)
    trendTimePeriod = randint(trendPeriodMin, trendPeriodMax)
    gradient = uniform(gradientMin, gradientMax)
    maxDistanceFromTrend = uniform(maxDistanceFromTrendMin, maxDistanceFromTrendMax)
    maxLastExit = randint(maxLastExitMin, maxLastExitMax)
    stoploss = uniform(stoplossMin, stoplossMax)

    #return object
    return{
        "name": "THREEMA_STOPLOSS",
        "fastTimeperiod": fastTimeperiod,
        "slowTimeperiod": slowTimePeriod,
        "trendTimeperiod": trendTimePeriod,
        "gradient": gradient, #min slope steepness to enter
        "maxDistanceFromTrend": maxDistanceFromTrend,
        "stoploss": stoploss,
        "maxLastExit" : maxLastExit #number of bars that need to go by after an exit before it can enter again(can prevent multiple bad trades)
    }
class THREEMA_STOPLOSS(bt.Strategy):

    params = (('strategySettings', None),)

    def __init__(self):
        self.fast = bt.talib.MA(self.data, timeperiod=math.ceil(self.params.strategySettings["fastTimeperiod"]))
        self.slow = bt.talib.MA(self.data, timeperiod=math.ceil(self.params.strategySettings["slowTimeperiod"]))
        self.trend = bt.talib.MA(self.data, timeperiod=math.ceil(self.params.strategySettings["trendTimeperiod"]))
        self.lastExit = 0
        self.prevFast = False
        self.prevSlow = False
        self.prevTrend = False
        self.stoploss = -9999
        self.negativeBank = False
        self.strategyExtension = StrategyExtension(self.params.strategySettings)


    def next(self):
        if self.prevFast != False and self.prevSlow != False and self.prevTrend != False:
            self.lastExit += 1
            distanceFromTrend = self.data.close - self.trend
            fastDifference = self.fast - self.prevFast
            slowDifference = self.slow - self.prevSlow
            trendDifference = self.trend - self.prevTrend
            gradient = self.params.strategySettings["gradient"]
            allUpwardsTrending = (fastDifference > gradient and slowDifference > gradient and trendDifference > gradient)

            if self.strategyExtension.position and (self.data.close + 0 - (self.data.close*(self.params.strategySettings["stoploss"]/100))) > self.stoploss:
                self.stoploss = self.data.close + 0 - (self.data.close*(self.params.strategySettings["stoploss"]/100))

            if self.negativeBank or self.strategyExtension.returnsPercent < -10:
                self.strategyExtension.returnsPercent = -999999
                self.negativeBank = True

            #sell
            if (distanceFromTrend < 1 or self.fast < self.slow or self.data.close < self.stoploss) and self.strategyExtension.position:
                self.strategyExtension.sell(self.data.close + 0)
                self.lastExit = 0
                self.close()

            #buy
            if allUpwardsTrending and self.lastExit > self.params.strategySettings["maxLastExit"] and self.fast > self.slow and distanceFromTrend < (self.trend + self.trend*self.params.strategySettings["maxDistanceFromTrend"]) and self.data.close > self.trend and not self.strategyExtension.position:
                self.strategyExtension.buy(self.data.close + 0)
                self.stoploss = self.data.close + 0 - (self.data.close*(self.params.strategySettings["stoploss"]/100))
                self.buy(size=buyAmount)

        self.prevFast = self.fast + 0
        self.prevSlow = self.slow + 0
        self.prevTrend = self.trend + 0


class SAR(bt.Strategy):
#gets ~555 profit
    def __init__(self):
        self.sar = bt.talib.SAR(self.data.high, self.data.low)
        self.lastExit = 0
        self.dotCount = 0
        self.prevSar = 0
        self.upTrend = False

    def next(self):
        if self.prevSar != 0:
            self.lastExit += 1
            if self.upTrend and self.prevSar - self.sar > 0:
                self.upTrend = False
                self.dotCount = 0
            elif not self.upTrend and self.prevSar - self.sar < 0:
                self.upTrend = True
                self.dotCount = 0
            self.dotCount += 1
            #sell
            if not self.upTrend and self.dotCount >= 3 and self.position:
                self.close()
                self.lastExit = 0

            #buy
            if self.upTrend and self.dotCount >= 3 and not self.position:
                self.buy(size=buyAmount)
        self.prevSar = self.sar + 0

def generateMEAN_REVERSION():
    #vars
    periodMin = 10
    periodMax = 50
    devFactorMin = 1
    devFactorMax = 5
    trendPeriodMin = 150
    trendPeriodMax = 300
    gradientMin = 0
    gradientMax = 0.1
    maxLastExitMin = 0
    maxLastExitMax = 20
    stoplossMin = 0.3
    stoplossMax = 4

    #generate random variables
    period = randint(periodMin, periodMax)
    devFactor = randint(devFactorMin, devFactorMax)
    trendTimePeriod = randint(trendPeriodMin, trendPeriodMax)
    gradient = uniform(gradientMin, gradientMax)
    maxLastExit = randint(maxLastExitMin, maxLastExitMax)
    stoploss = uniform(stoplossMin, stoplossMax)

    #return object
    return{
        "name": "MEAN_REVERSION",
        "period": period,
        "devFactor": devFactor,
        "trendTimeperiod": trendTimePeriod,
        "gradient": gradient,
        "stoploss": stoploss,
        "maxLastExit" : maxLastExit
    }
class MEAN_REVERSION(bt.Strategy):
    '''
    This is a simple mean reversion bollinger band strategy.

    Entry Critria:
        - Long:
            - Price closes below the lower band
            - Stop Order entry when price crosses back above the lower band
        - Short:
            - Price closes above the upper band
            - Stop order entry when price crosses back below the upper band
    Exit Critria
        - Long/Short: Price touching the median line
    '''

    params = (
        ("period", 20),
        ("devfactor", 2),
        ("size", buyAmount),
        ("debug", False),
        ('strategySettings', None)
    )

    def __init__(self):
        self.boll = bt.indicators.BollingerBands(period=math.ceil(self.params.strategySettings["period"]), devfactor=math.ceil(self.params.strategySettings["devFactor"]))
        self.ma = bt.talib.MA(self.data, timeperiod=math.ceil(self.params.strategySettings["trendTimeperiod"]))
        self.prevMa = False
        self.stoploss = -999
        self.lastExit = 0
        self.short = False
        self.strategyExtension = StrategyExtension(self.params.strategySettings)
        # self.sx = bt.indicators.CrossDown(self.data.close, self.boll.lines.top)
        # self.lx = bt.indicators.CrossUp(self.data.close, self.boll.lines.bot)

    def next(self):
        if self.prevMa != False:
            self.lastExit += 1
            if not self.strategyExtension.position:
                gradientTrend = ((self.ma - self.prevMa) / self.prevMa) * 100
                minGradient = self.params.strategySettings["gradient"]
                if self.lastExit > self.params.strategySettings["maxLastExit"] and self.data.close > self.boll.lines.top and gradientTrend < -minGradient and self.data.close < self.ma:
                    self.strategyExtension.buy(self.data.close + 0)
                    self.stoploss = self.data.close + (self.data.close * self.params.strategySettings["stoploss"])
                    self.short = True

                if self.lastExit > self.params.strategySettings["maxLastExit"] and self.data.close < self.boll.lines.bot and gradientTrend > minGradient and self.data.close > self.ma:
                    self.strategyExtension.buy(self.data.close + 0)
                    self.stoploss = self.data.close - (self.data.close*self.params.strategySettings["stoploss"])
                    self.short = False


            else:

                if not self.short and (self.data.close < self.stoploss or self.data.close > self.boll.lines.mid):
                    self.strategyExtension.sell(self.data.close + 0)
                    self.lastExit = 0

                elif self.data.close > self.stoploss or self.data.close < self.boll.lines.mid:
                    diff = self.data.close - self.strategyExtension.boughtAt
                    self.strategyExtension.sell(self.strategyExtension.boughtAt + diff)
                    self.lastExit = 0
        self.prevMa = self.ma + 0

class RSI(bt.Strategy):

    def __init__(self):
        self.rsi = bt.talib.RSI(self.data, timeperiod=14)
        self.boughtAt = 0

    def next(self):
        if self.rsi < 15 and not self.position:
            self.buy(size=buyAmount) #100
            self.boughtAt = self.data.close + 0
        if self.rsi > 30 or self.data.close <= (self.boughtAt - (self.boughtAt*0.01)) and self.position:
            self.close()

class MA_UPTREND(bt.Strategy):

    def __init__(self):
        self.ma = bt.talib.WMA(self.data, timeperiod=50, matype=0)
        self.prevMa = "a"
        self.lastExit = 0

    def next(self):
        if self.prevMa != "a":
            distanceFromMA = self.data.close - self.ma
            difference = self.ma - self.prevMa
            distanceMax = 200
            self.lastExit += 1
            if self.lastExit > 25 and difference > 1.1 and distanceFromMA > 50 and distanceFromMA < distanceMax and not self.position:
                self.buy(size=buyAmount)
            if (distanceFromMA < 1 or distanceFromMA > distanceMax) and self.position:
                self.close()
                self.lastExit = 0
        self.prevMa = self.ma + 0

class MA_DOWNTREND(bt.Strategy):

    def __init__(self):
        self.ma = bt.talib.MA(self.data, timeperiod=85, matype=0)
        self.prevMa = "a"
        self.lastExit = 0

    def next(self):
        if self.prevMa != "a":
            distanceFromMA = self.ma - self.data.close
            difference = self.prevMa - self.ma
            self.lastExit += 1
            if difference > 2 and not self.position:
                self.buy(size=buyAmount)
            if (distanceFromMA < 1) and self.position:
                self.close()
                self.lastExit = 0
        self.prevMa = self.ma + 0