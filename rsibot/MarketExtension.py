def get_market(symbol):
    symbol = symbol.upper()
    if symbol == "BTCUSDT":
        return {
            "symbol": symbol,
            "THREEMA": threema(60, 85, 180, 0.016, 0),
            "THREEMA_STOPLOSS": threema_stoploss(0.005,60, 85, 180, 0.016, 0),
            "MEAN_REVERSION": mean_reversion(200, 20, 0.001, 0.016, 3.2)
        }
    elif symbol == "ETHUSDT":
        return {
            "symbol": symbol,
            "THREEMA": threema(60, 85, 180, 0.01, 0),
            "THREEMA_STOPLOSS": threema_stoploss(0.005,60, 85, 180, 0.01, 0),
            "MEAN_REVERSION": mean_reversion(200, 20, 0.002, 0.01, 1.2)
        }
    elif symbol == "LTCUSDT":
        return {
            "symbol": symbol,
            "THREEMA": threema(60, 85, 180, 0.013, 0),
            "THREEMA_STOPLOSS": threema_stoploss(0.005, 60, 85, 180, 0.013, 0),
            "MEAN_REVERSION": mean_reversion(200, 20, 0.0035, 0.013, 0.35)
        }
    elif symbol == "LINKUSDT":
        return {
            "symbol": symbol,
            "THREEMA": threema(65, 120, 200, 0.011, 0),
            "THREEMA_STOPLOSS": threema_stoploss(0.005, 65, 120, 200, 0.011, 0),
            "MEAN_REVERSION": mean_reversion(210, 20, 0.0016, 0.021, 0.04)
        }
    elif symbol == "BTTUSDT":
        return {
            "symbol": symbol,
            "THREEMA": threema(60, 85, 180, 0.021, 0),
            "THREEMA_STOPLOSS": threema_stoploss(0.005, 60, 85, 180, 0.021, 0),
            "MEAN_REVERSION": mean_reversion(200, 20, 0.0025, 0.021, 0.0000002)
        }
    return False

def threema(fastInterval, slowInterval, trendInterval, maxDistanceFromTrend, upwardsGradient=0):
    return {
        "fast_interval": fastInterval, #timeperiod for fast line
        "slow_interval": slowInterval, #timeperiod for slow line
        "trend_interval": trendInterval, #timeperiod for trend line
        "max_distance_from_trend": maxDistanceFromTrend, #max distance from trend line which it can enter trade/stoploss
        "gradient": upwardsGradient, #how much the trend line can be up to enter a trade
    }
def threema_stoploss(stoploss, fastInterval, slowInterval, trendInterval, maxDistanceFromTrend, upwardsGradient=0):
    return {
        "stoploss": stoploss,  # trailing stoploss
        "fast_interval": fastInterval, #timeperiod for fast line
        "slow_interval": slowInterval, #timeperiod for slow line
        "trend_interval": trendInterval, #timeperiod for trend line
        "max_distance_from_trend": maxDistanceFromTrend, #max distance from trend line which it can enter trade/stoploss
        "gradient": upwardsGradient, #how much the trend line can be up to enter a trade
    }
def mean_reversion(trendInterval, BBandsInterval, midRangeSize, maxDistanceFromMa, gradient):
    return {
        "trend_interval": trendInterval, #timeperiod for trend line
        "bbands_interval": BBandsInterval, #timeperiod for bbands
        "mid_range_size": midRangeSize, #area around the mid range point that triggers sell/reset stoploss
        "max_distance_from_ma": maxDistanceFromMa, #max distance from trend line which it can enter trade(basically a stoploss)
        "gradient": gradient,  # how much the trend line can be up/down to enter a trade
    }