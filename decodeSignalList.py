import signalGetRich
from datetime import datetime
import datetime as TIME

assetsList = ['EUR', 'USD', 'JPY', 'GBP', 'CAD', 'AUD', 'NZD', 'CHF']

def getTime(info):
    time = None
    if len(info) >= 5:
        sepIndex = info.find(':')
        if sepIndex != -1:
            now = datetime.now()
            minute = info[sepIndex + 1:sepIndex + 3]
            hour = info[sepIndex - 2:sepIndex]
            if minute.isdigit() and hour.isdigit():
                minute = int(minute)
                hour = int(hour)
                time = datetime(year=(now.year), month=(now.month), day=(now.day), hour=hour, minute=minute)
                if now > time:
                    time += TIME.timedelta(days=1)
                time = datetime.timestamp(time)
    return time


def getDuration(info):
    duration = None
    if info.find('M15') != -1:
        duration = 15
    elif info.find('M5') != -1:
        duration = 5
    elif info.find('M1') != -1:
        duration = 1
    return duration


def getAction(info):
    action = None
    info = info.lower()
    if info.find('put') != -1:
        action = 'put'
    elif info.find('call') != -1:
        action = 'call'
    return action


def getAsset(info):
    asset = None
    asset1 = None
    asset2 = None
    for i in range(len(assetsList)):
        if info.find(assetsList[i]) != -1:
            asset1 = i
            break
    for i in range(len(assetsList)):
        if i != asset1 and info.find(assetsList[i]) != -1:
            asset2 = i
            break

    if asset1 != None and asset2 != None:
        if info.index(assetsList[asset1]) < info.index(assetsList[asset2]):
            asset = assetsList[asset1] + assetsList[asset2]
        else:
            asset = assetsList[asset2] + assetsList[asset1]
        if info.find('OTC') != -1:
            asset += '-OTC'
    return asset


def getSignal(info):
    time = getTime(info)
    #print(time)
    duration = getDuration(info)
    #print(duration)
    action = getAction(info)
    #print(action)
    asset = getAsset(info)
    #print(asset)
    signal = signalGetRich.Signal(time, 0, asset, action, duration)
    return signal


def removeBlankLines(signalList):
    for signal in signalList:
        if signal.strip() == '':
            signalList.remove(signal)
    return signalList


def decodeSingleList(signalList):
    signals = []
    for signal in signalList:
        signals.append(getSignal(signal))

    isValid = False
    for signal in signals:
        if not signal.isValid():
            signals.remove(signal)
        else:
            isValid = True

    return isValid, signals


def decodeGroupList(signalList):
    signalList = removeBlankLines(signalList)
    if len(signalList) > 1:
        duration = getDuration(signalList[0])
        signalList.pop(0)
        if duration != None:
            for i in range(len(signalList)):
                signalList[i] += ' M' + str(duration)
            return decodeSingleList(signalList)

    return False, None