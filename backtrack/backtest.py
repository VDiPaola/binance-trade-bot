import datetime
import backtrader as bt
import GeneticAlgorithm
import Strategies

fromdate = datetime.datetime.strptime("2019-01-01", '%Y-%m-%d')
todate = datetime.datetime.today()

def run(market, strategy, strategySettings):
    cerebro = bt.Cerebro()
    cerebro.broker.setcash(1000)
    data = bt.feeds.GenericCSVData(dataname=market+"_alltime15Mins.csv", dtformat=2, compression=15,
                                   timeframe=bt.TimeFrame.Minutes, fromdate=fromdate, todate=todate)
    cerebro.adddata(data)

    cerebro.addstrategy(strategy, strategySettings=strategySettings)

    strat = cerebro.run()

    return strat[-1].strategyExtension

if __name__ == '__main__':
    markets = ["ETHUSDT"]
    optimiserSettings = GeneticAlgorithm.OptimiserSettings(crossoverRate=55, strategyMutationRate=1, attributeMutationRate=8, population=100,
                                                           markets=markets, multiProcessing=True)

    scoreSettings = GeneticAlgorithm.ScoreSettings(returnPercentage=90, highestHigh=8, goodBadTradeCountRatio=0.9,
                                                   goodBadTradeCountRatioNegative=0.5, lowestLow=3.5, lowestLowNegative=6, tradeCountNegative=320)

    GeneticAlgorithm.Optimiser(optimiserSettings, scoreSettings, strategyClass=Strategies.MEAN_REVERSION,
                               generateStrategy=Strategies.generateMEAN_REVERSION, runStrategy=run)