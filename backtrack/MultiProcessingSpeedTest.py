from multiprocessing import Process
import Strategies
import datetime
import backtrader as bt

def run(market, strategy, strategySettings):
    cerebro = bt.Cerebro()
    cerebro.broker.setcash(1000)
    data = bt.feeds.GenericCSVData(dataname=market+"_alltime15Mins.csv", dtformat=2, compression=15,
                                   timeframe=bt.TimeFrame.Minutes)
    cerebro.adddata(data)

    cerebro.addstrategy(strategy, strategySettings=strategySettings)

    cerebro.run()


if __name__ == '__main__':
    testStrategy = {'fastTimeperiod': 53, 'slowTimeperiod': 98, 'trendTimeperiod': 268,
                    'gradient': 0.001276387404329823, 'maxDistanceFromTrend': 0.010557171648579887,
                    'stoploss': 0.006132991027880451, 'maxLastExit': 20}

    print("starting single processing test")
    time = datetime.datetime.now()
    run("BTCUSDT", Strategies.THREEMA, testStrategy)
    run("BTCUSDT", Strategies.THREEMA, testStrategy)
    run("ETHUSDT", Strategies.THREEMA, testStrategy)
    print("single processing took " + str((datetime.datetime.now() - time).total_seconds()) + " seconds")

    print("starting multi-processing test")
    time = datetime.datetime.now()
    t1 = Process(target=run, args=("BTCUSDT", Strategies.THREEMA, testStrategy))
    t2 = Process(target=run, args=("BTCUSDT", Strategies.THREEMA, testStrategy))
    t3 = Process(target=run, args=("ETHUSDT", Strategies.THREEMA, testStrategy))

    t1.start()
    t2.start()
    t3.start()

    t1.join()
    t2.join()
    t3.join()

    print("multi-processing took " + str((datetime.datetime.now()-time).total_seconds()) + " seconds")