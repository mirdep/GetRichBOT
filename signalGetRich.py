from datetime import datetime

def assetExists(market):
    exists = False
    assetsList = ['EUR', 'USD', 'JPY', 'GBP', 'CAD', 'AUD', 'NZD', 'CHF']
    for i in assetsList:
        if market == i:
            exists = True
            break
    return exists


def formatTime(timestamp):
    time = datetime.fromtimestamp(timestamp)
    return str(time.day) + '/' + str(time.month) + '/' + str(time.year % 100) + ' ' + '{:02d}'.format(time.hour) + ':' + '{:02d}'.format(time.minute)


class Signal:

    def __init__(self, time, stake, asset, action, duration):
        self.time = time
        self.stake = stake
        self.asset = asset
        self.action = action
        self.duration = duration

    def timeIsValid(self):
        return type(self.time) == float or type(self.time) == int

    def stakeIsValid(self):
        return type(self.stake) == float or type(self.stake) == int

    def assetIsValid(self):
        isValid = False
        if type(self.asset) == str:
            if len(self.asset) == 6:
                market1 = self.asset[0:3]
                market2 = self.asset[3:6]
                isValid = assetExists(market1) and assetExists(market2) and market1 != market2
            elif len(self.asset) == 10:
                market1 = self.asset[0:3]
                market2 = self.asset[3:6]
                isValid = assetExists(market1) and assetExists(market2) and market1 != market2 and self.asset[6:10] == '-OTC'
        return isValid

    def actionIsValid(self):
        isValid = False
        if type(self.action) == str:
            self.action = self.action.lower()
            isValid = self.action == 'put' or self.action == 'call'
        return isValid

    def durationIsValid(self):
        return type(self.duration) == int and (self.duration == 1 or self.duration == 5 or self.duration == 15)

    def isValid(self):
        return self.timeIsValid() and self.stakeIsValid() and self.assetIsValid() and self.actionIsValid() and self.durationIsValid()

    def toString(self):
        return formatTime(self.time) + ' M' + str(self.duration) + ' ' + self.asset + ' ' + self.action + ' R$' + '{:.2f}'.format(self.stake)

    def isEqual(self, signal):
        return self.time == signal.time and self.stake == signal.stake and self.asset == signal.asset and self.action == signal.action and self.duration == signal.duration