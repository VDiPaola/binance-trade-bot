import datetime


class Strategy:
    def __init__(self, strategyName, market):
        self.in_position = False
        self.latestBoughtPrice = False
        self.latestSellPrice = 0
        self.stoploss = False
        self.canTrade = True
        self.strategyName = strategyName
        self.short = False
        self.market = market

    def buy(self, size):
        with open("logs/" + self.market + "_Log.txt", "a") as myfile:
            if self.short:
                print((str(datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")) + ":[" + self.strategyName + "][BUY SHORT] " + str(size) + " BTC for $" + str(self.latestBoughtPrice) + "\n"))
                myfile.write(str(datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")) + ":[" + self.strategyName + "][BUY SHORT] " + str(size) + " BTC for $" + str(self.latestBoughtPrice) + "\n")
            else:
                print((str(datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")) + ":[" + self.strategyName + "][BUY] " + str(size) + " BTC for $" + str(self.latestBoughtPrice) + "\n"))
                myfile.write(str(datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")) + ":[" + self.strategyName + "][BUY] " + str(size) + " BTC for $" + str(self.latestBoughtPrice) + "\n")

    def sell(self, size, price):
        with open("logs/" + self.market + "_Log.txt", "a") as myfile:
            if self.short:
                print((str(datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")) + ":[" + self.strategyName + "][SELL SHORT]" + str(size) + " BTC for $" + str(price) + "\n"))
                myfile.write(str(datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")) + ":[" + self.strategyName + "][SELL SHORT]" + str(size) + " BTC for $" + str(price) + "\n")
            else:
                print((str(datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")) + ":[" + self.strategyName + "][SELL] " + str(size) + " BTC for $" + str(price) + "\n"))
                myfile.write(str(datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")) + ":[" + self.strategyName + "][SELL] " + str(size) + " BTC for $" + str(price) + "\n")
