import datetime
import numpy as np
from multiprocessing import Pool
import random


class OptimiserSettings:
    def __init__(self,  crossoverRate, strategyMutationRate, attributeMutationRate, population,markets,multiProcessing=True):
        self.crossoverRate = crossoverRate
        self.strategyMutationRate = strategyMutationRate
        self.attributeMutationRate = attributeMutationRate
        self.markets = markets
        self.population = population
        self.multiProcessing = multiProcessing

class ScoreSettings:
    def __init__(self, returnPercentage, highestHigh, goodBadTradeCountRatio, lowestLow, goodBadTradeCountRatioNegative, lowestLowNegative, tradeCountNegative):
        self.returnPercentage = returnPercentage
        self.highestHigh = highestHigh
        self.lowestLow = lowestLow
        self.goodBadTradeCountRatio = goodBadTradeCountRatio
        self.goodBadTradeCountRatioNegative = goodBadTradeCountRatioNegative
        self.lowestLowNegative = lowestLowNegative
        self.tradeCountNegative = tradeCountNegative

class Optimiser:

    def __init__(self, optimiserSettings, scoreSettings, strategyClass, generateStrategy, runStrategy):
        self.settings = optimiserSettings
        self.scoreSettings = scoreSettings
        self.strategyClass = strategyClass
        self.runStrategy = runStrategy
        self.generateStrategy = generateStrategy
        self.generation = 1
        self.Run(self.generateStrategies(generateStrategy,optimiserSettings.population))
    def Run(self, strategies):
        strategyList = []
        print("starting generation " + str(self.generation))
        print("running backtrader")
        for strategy in strategies:
            strategyPerMarketList = []
            if not self.settings.multiProcessing:
                for market in self.settings.markets:
                    strategyPerMarketList.append(self.runStrategy(market, self.strategyClass, strategy))
            else:
                with Pool(processes=len(self.settings.markets)) as pool:
                    processes = []
                    for market in self.settings.markets:
                        processes.append(pool.apply_async(self.runStrategy, (market, self.strategyClass, strategy)))
                    for process in processes:
                        strategyPerMarketList.append(process.get())
            strategyList.append(self.sumStrategies(strategyPerMarketList))
        print("finished backtrader")
        print("starting tournament")
        children = np.array([])
        while len(children) < self.settings.population:
            children = np.append(children, self.startTournament(strategyList))
        print("finished tournament")
        nextGenerationStrategies = []
        for child in children:
            nextGenerationStrategies.append(child["strategySettings"])
        print("finished generation" + str(self.generation))
        self.generation += 1
        self.Run(nextGenerationStrategies)


    def sumStrategies(self, strategies):
        strategyResponse = {}
        #populate with default attributes
        for attribute, value in strategies[-1].__dict__.items():
            if attribute == "strategySettings":
                strategyResponse[attribute] = value
            else:
                strategyResponse[attribute] = 0
        #add everything apart from lowest low and highest high
        for strategy in strategies:
            for attribute, value in strategy.__dict__.items():
                if attribute.lower() != "boughtat" and attribute != "position" and attribute != "strategySettings":
                    if attribute.lower() == "lowestlow" or attribute.lower() == "highesthigh":
                        if (attribute.lower() == "lowestlow" and strategyResponse[attribute] > value) or (attribute.lower() == "highesthigh" and strategyResponse[attribute] < value):
                            strategyResponse[attribute] = value

                    else:
                        strategyResponse[attribute] += value
        #divide all by number of strategies to get average (apart from high and low)
        for key in strategyResponse.keys():
            if key.lower() != "lowestlow" and key.lower() != "highesthigh" and key != "strategySettings":
                strategyResponse[key] = strategyResponse[key] / len(strategies)
        return strategyResponse

    def generateStrategies(self, method, population):
        #gets the initial strategy list
        strategies = []
        for i in range(population):
            strategies.append(method())
        return strategies


    def crossover(self,strategy1, strategy2):
        print("crossing over")
        child1 = {}
        child2 = {}
        attributes = strategy1["strategySettings"].keys()
        i = 0
        for attribute in attributes:
            if i % 2 == 0:
                child1[attribute] = strategy1["strategySettings"][attribute]
                child2[attribute] = strategy2["strategySettings"][attribute]
            else:
                child1[attribute] = strategy2["strategySettings"][attribute]
                child2[attribute] = strategy1["strategySettings"][attribute]
            i += 1
        strategy1["strategySettings"] = child1
        strategy2["strategySettings"] = child2

        return [strategy1, strategy2]


    def mutate(self,strategy):
        print("mutating")
        for attribute in strategy["strategySettings"].keys():
            if type(strategy["strategySettings"][attribute]) == int or type(strategy["strategySettings"][attribute]) == float and random.uniform(0.0, 100.0) < self.settings.attributeMutationRate:
                if random.uniform(0.0, 100.0) < 50:
                    strategy["strategySettings"][attribute] = float(strategy["strategySettings"][attribute]) + float(strategy["strategySettings"][attribute])*0.05
                else:
                    strategy["strategySettings"][attribute] = float(strategy["strategySettings"][attribute]) - float(strategy["strategySettings"][attribute]) * 0.05
        return strategy

    def log(self, strategies):
        print("logging generation")
        name = strategies[-1]["strategySettings"]["name"] + "_" + "-".join(self.settings.markets)
        with open("logs/" + name + ".txt", "a") as myfile:
            myfile.write("Generation "+ str(self.generation) + "\n")
            for strategy in strategies:
                string = str(datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S") + str(strategy["strategySettings"]))
                # for attribute in strategy["strategySettings"].keys():
                #     string += "_" + attribute + "-" + str(strategy["strategySettings"][attribute])
                myfile.write(string + "\n")

            for strategy in strategies:
                string = ""
                for attribute in strategy.keys():
                    if attribute != "strategySettings" and attribute != "boughtAt" and attribute != "position":
                        string += "_" + attribute + "-" + str(strategy[attribute])
                myfile.write(string + "\n")

            myfile.write("\n\n\n")


    def score(self, strategy):
        score = 0
        goodBadTradeRatio = 0
        if strategy["numberOfLows"] != 0:
            goodBadTradeRatio = strategy["numberOfHighs"] / strategy["numberOfLows"]

        else:
            goodBadTradeRatio = strategy["numberOfHighs"]

        if strategy["lowestLow"] > self.scoreSettings.lowestLow:
            score += 1
        elif strategy["lowestLow"] < self.scoreSettings.lowestLowNegative:
            score -= 1

        if goodBadTradeRatio > self.scoreSettings.goodBadTradeCountRatio:
            score += 1
        elif goodBadTradeRatio < self.scoreSettings.goodBadTradeCountRatioNegative:
            score -= 1

        if strategy["tradeCount"] < self.scoreSettings.tradeCountNegative:
            score -= 1

        if strategy["returnsPercent"] > self.scoreSettings.returnPercentage:
            score += 1
        if strategy["highestHigh"] > self.scoreSettings.highestHigh:
            score += 1

        return score

    def fight(self,strat1,strat2):
        strat1Score = self.score(strat1)
        strat2Score = self.score(strat2)
        if strat1Score > strat2Score:
            return strat1
        elif strat2Score > strat1Score:
            return strat2

        drawPriority = ["lowestLow", "returnsPercent", "numberOfLows", "tradeCount", "numberOfHighs", "highestHigh" ]
        for priority in drawPriority:
            if priority == "numberOfLows":
                if strat1[priority] < strat2[priority]:
                    return strat1
                elif strat2[priority] < strat1[priority]:
                    return strat2
            else:
                if strat1[priority] > strat2[priority]:
                    return strat1
                elif strat2[priority] > strat1[priority]:
                    return strat2

        return strat1

    def startTournament(self, strategies):
        random.shuffle(strategies)
        winners = []
        for i in range(0, len(strategies)-1, 2):
            strat1 = strategies[i]
            strat2 = strategies[i+1]
            winner = self.fight(strat1, strat2)
            winners.append(winner)

        self.log(winners)

        random.shuffle(winners)
        children = []
        for i in range(len(winners)):
            #crossover
            if i+1 < len(winners) and random.randint(0,100) < self.settings.crossoverRate:
                crossover = self.crossover(winners[i], winners[i+1])
                children.append(crossover[0])
                children.append(crossover[1])
            else:
                children.append(winners[i])
        for child in children:
            #mutation
            if random.uniform(0.0, 100.0) < self.settings.strategyMutationRate:
                child = self.mutate(child)

        return children