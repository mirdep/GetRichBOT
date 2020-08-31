import signalGetRich
from datetime import datetime
import datetime as TIME

def getLines(message):
    lines = message.splitlines()
    for i in range(len(lines)):
        lines[i] = lines[i].strip()

    return lines


def getAsset(assetInfo):
    asset = None
    return asset


def getAction(optionInfo):
    optionInfo = optionInfo.lower()
    if optionInfo == 'call' or optionInfo == 'put':
        option = optionInfo
    else:
        option = None
    return option


def getTime(timeInfo):
    time = None
    now = datetime.now()
    length = len(timeInfo)
    minute = timeInfo[length - 2:length]
    hour = timeInfo[length - 5:length - 3]
    if minute.isdigit():
        if hour.isdigit():
            minute = int(minute)
            hour = int(hour)
            time = datetime(year=(now.year), month=(now.month), day=(now.day), hour=hour, minute=minute)
            if now > time:
                time += TIME.timedelta(days=1)
            time = datetime.timestamp(time)
    return time


def getDuration(durationInfo):
    duration = None
    if durationInfo.find('M15') != -1:
        duration = 15
    elif durationInfo.find('M5') != -1:
        duration = 5
    elif durationInfo.find('M1') != -1:
        duration = 1
    return duration


def decodeSignalMessage(signalMessage):
    infos = getLines(signalMessage)
    signal = None
    if len(infos) == 6:
        stake = 0
        #print(stake)
        asset = getAsset(infos[0])
        #print('Mercado:', asset)
        action = getAction(infos[1])
        #print('Ação:', action)
        time = getTime(infos[2])
        #print('Tempo:', time)
        duration = getDuration(infos[3])
        #print('Duração:', duration)
        if stake != None and asset != None and action != None and time != None and duration != None:
            signal = signalGetRich.Signal(time, stake, asset, action, duration)
    return signal