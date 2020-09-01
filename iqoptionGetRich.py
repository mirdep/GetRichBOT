import time, configReader, logging
from iqoptionapi.stable_api import IQ_Option
import threading
import asyncio
from datetime import datetime
import signalGetRich, financeiroGetRich, decodeSignalList, decodeOverMilionarios

logging.basicConfig(format='[%(levelname) 5s/%(asctime)s] %(name)s: %(message)s', level=(logging.WARNING))

LOG_LABEL = '[IQOPTION API]'
print(LOG_LABEL+' Inicializando...')
iqoptionLabel = 'iqoption'
iqoptionClient = IQ_Option(configReader.get('iq_email'), configReader.get('iq_senha'))
connected, reason = iqoptionClient.connect()
if connected:
    print(LOG_LABEL+' Login feito com sucesso!')
else:
    print(LOG_LABEL+' Erro ao fazer login... Motivo: ' + reason)
iqoptionClient.change_balance(configReader.get('iq_conta'))

def checkConnection():
    connected = iqoptionClient.check_connect()
    if not connected:
        connected, reason = iqoptionClient.connect()
    return connected

def LOG(message):
    print('\n'+LOG_LABEL + ' ' + str(message))


def getBalance():
    return iqoptionClient.get_balance()


def calculateGale(stake):
    if type(stake) == float or (type(stake) == int):
        return stake * 2
    return 0


def getSaldo():
    bancaHoje = financeiroGetRich.getBanca(getBalance(), deHoje=True)
    saldo = getBalance()
    return 'Banca do dia = R$' + '{:.2f}'.format(bancaHoje) + '\nSaldo atual = R$' + '{:.2f}'.format(saldo) + '\nLucro = R$' + '{:.2f}'.format(saldo - bancaHoje)


financeiroGetRich.getBanca(getBalance(), deHoje=True)
signalExecLine = []

def printSignalLineInfo():
    global signalExecLine
    LOG('== FILA DE ESPERA DE ENTRADA =>> ' + str(len(signalExecLine)))


def getSignalsInLine():
    if len(signalExecLine) > 0:
        line = '> Sinais Cadastrados <\n\n'
        for i in range(len(signalExecLine)):
            line += str(i + 1) + 'ª - ' + signalExecLine[i].toString() + '\n'

    else:
        line = 'Nenhum sinal de entrada na fila. Você é um fracassado amigão!'
    return line


def clearSignalsLine():
    global signalExecLine
    if len(signalExecLine) > 0:
        signalExecLine = []
        return 'Fila zerada com sucesso!'
    signalExecLine = []
    return 'A fila já estava zerada!'


def getNextSignal():
    if len(signalExecLine) == 0:
        return False, 0
    return True, signalExecLine[0]


def getEntradasExecutadasHoje():
    return financeiroGetRich.getEntradasExecutadasHoje()


_DESLIGAR = False

def desligar():
    global _DESLIGAR
    _DESLIGAR = True


def getResult(id, tipo):
    waitTime = 0.1
    while True:
        if _DESLIGAR:
            break

        if tipo == 'binary':
            result, profit = iqoptionClient.check_win_v4(id)
            if profit != None:
                return profit
        elif tipo == 'digital':
            check, profit = iqoptionClient.check_win_digital_v2(id)
            if check == True:
                return profit
        time.sleep(waitTime)


def buy(signal):
    completed, id = iqoptionClient.buy(signal.stake, signal.asset, signal.action, signal.duration)
    if completed:
        return True, 'binary', id
    completed, id = iqoptionClient.buy_digital_spot(signal.asset, signal.stake, signal.action, signal.duration)
    if completed:
        return True, 'digital', id
    return None, None, None

def execSignal(signal):
    if checkConnection():
        for i in range(int(configReader.get('max_gale')) + 1):
            if i > 0:
                    signal.stake = calculateGale(signal.stake)
                    
            if financeiroGetRich.podeExecutar(getBalance()):
                completed, tipo, id = buy(signal)

                if completed:
                    message = '\n=====ENTRADA FEITA=====\n'
                    if i > 0:
                        message += str(i) + 'º MartinGale\n'
                    message += 'ID = ' + str(id) + '\n' + signal.toString() + '\n======================='
                    print(message)
                    time.sleep(30)
                    profit = getResult(id, tipo)
                    financeiroGetRich.addEntradaExecutada(signal, id, profit)
                    if profit != None:
                        if profit >= 0:
                            LOG('Você lucrou = R$' + str('{:.2f}'.format(profit)) + ' ✅✅✅\nNa entrada ' + signal.toString())
                            break
                        else:
                            LOG('Você lucrou = R$' + str('{:.2f}'.format(profit)) + ' ❌\nNa entrada ' + signal.toString())

                    else:
                        print('Não foi possível pegar o resultado da entrada ID = ' + str(id))
                        break
                else:
                    message = '\nErro ao executar entrada:\n' + signal.toString()
                    print(message)
                    break
            else:
                break

    else:
        message = '\nErro ao executar entrada:\n' + signal.toString()
        print(message)

def requestSignalExec(signal):
    threading.Thread(target=execSignal, args=(signal,)).start()


def signalLineExecution():
    while True:
        if _DESLIGAR:
            break

        fastCheck = False
        hasNextSignal, nextSignal = getNextSignal()
        if hasNextSignal:
            now = datetime.timestamp(datetime.now())
            execDelay = int(configReader.get('delay_exec'))
            if now + execDelay >= nextSignal.time:
                requestSignalExec(nextSignal)
                removeSignalFromLine(nextSignal)
                fastCheck = True
        if not fastCheck:
            time.sleep(0.5)


threading.Thread(target=signalLineExecution).start()

def sortTime(signal):
    return signal.time


def signalExists(signal):
    exists = False
    for i in signalExecLine:
        if i.isEqual(signal):
            exists = True
            break
    else:
        return exists


def addSignalToLine(signal):
    if signal.isValid() and not signalExists(signal):
        signalExecLine.append(signal)
        signalExecLine.sort(key=sortTime)


def removeSignalFromLine(signal):
    signalExecLine.remove(signal)


def addSignal_OverMilionarios(signalMessage):
    signal = decodeSignalList.getSignal(signalMessage)
    if type(signal) == signalGetRich.Signal:
        if signal.isValid():
            signal.stake = financeiroGetRich.getStake(getBalance())
            addSignalToLine(signal)
            return '[OverMilionariosOB] Sinal adicionado na lista.'
    return


def addList(message, listType):
    lines = message.splitlines()
    if listType == 'single':
        isValid, signalList = decodeSignalList.decodeSingleList(lines)
    elif listType == 'group':
        isValid, signalList = decodeSignalList.decodeGroupList(lines)
    else:
        isValid = False

    if isValid:
        stake = financeiroGetRich.getStake(getBalance())
        for signal in signalList:
            signal.stake = stake
            addSignalToLine(signal)
    return isValid, len(signalList)