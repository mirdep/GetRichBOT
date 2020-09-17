import signalGetRich
from datetime import datetime
import datetime as TIME

assetsList = ['EUR', 'USD', 'JPY', 'GBP', 'CAD', 'AUD', 'NZD', 'CHF']
paresExistentes = ['EURUSD','EURGBP','GBPJPY','EURJPY','GBPUSD','USDJPY','EURUSD-OTC','EURGBP-OTC','USDCHF-OTC','EURJPY-OTC','NZDUSD-OTC','GBPUSD-OTC','GBPJPY-OTC','USDJPY-OTC','AUDCAD-OTC','AUDUSD','USDCAD','AUDJPY','GBPCAD','GBPCHF','EURCAD','EURAUD']

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
    cleanList = []
    for signal in signalList:
        if signal.strip() != '':
            cleanList.append(signal)
    return cleanList


def decodeSingleList(signalList):
    signals = []
    for signal in signalList:
        signals.append(getSignal(signal))

    validos = []
    for signal in signals:
        if signal.isValid():
            validos.append(signal)

    isValid = len(validos) > 0
    return isValid, validos


def decodeGroupList(signalList):
    signalList = removeBlankLines(signalList)
    duration = 0
    for i, signal in enumerate(signalList):
        temp = getDuration(signal)
        if temp == None:
            signalList[i] += ' M'+str(duration)
        else:
            duration = temp
    return decodeSingleList(signalList)