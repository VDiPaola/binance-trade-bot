import datetime
import backtrader as bt
import GeneticAlgorithm
import Strategies

fromdate = datetime.datetime.strptime("2010-08-01", '%Y-%m-%d')
todate = datetime.datetime.today()

def run(market, strategy, strategySettings):
    cerebro = bt.Cerebro()
    cerebro.broker.setcash(1000)
    data = bt.feeds.GenericCSVData(dataname=market+"_alltime15Mins.csv", dtformat=2, compression=15,
                                   timeframe=bt.TimeFrame.Minutes, fromdate=fromdate, todate=todate)
    cerebro.adddata(data)

    cerebro.addstrategy(strategy, strategySettings=strategySettings)

    cerebro.run()

    cerebro.plot()


market = "LTCUSDT"

ss = {'name': 'THREEMA', 'fastTimeperiod': 55, 'slowTimeperiod': 105.0, 'trendTimeperiod': 172, 'gradient': 0.0013169064759878456, 'maxDistanceFromTrend': 0.02332659235757221, 'maxLastExit': 6.3}
run(market, Strategies.THREEMA, ss)