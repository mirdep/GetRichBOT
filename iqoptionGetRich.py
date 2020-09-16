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

def formatMoneyBRL(money):
    return 'R$'+'{:.2f}'.format(money)


def getSaldo():
    saldoAtual = getBalance()
    banca = financeiroGetRich.getBanca()
    message = 'Banca = '+formatMoneyBRL(banca)+'\n'
    stake = financeiroGetRich.getStake()
    message += 'Stake = '+formatMoneyBRL(stake)+'\n'
    saldoHoje = financeiroGetRich.getSaldoHoje(saldoAtual)
    message += 'Saldo do dia = '+formatMoneyBRL(saldoHoje)+'\n'
    stopWin = financeiroGetRich.getSaldoStopWin(saldoAtual)
    message += 'StopWin = '+formatMoneyBRL(stopWin)+'\n'
    stopLoss = financeiroGetRich.getSaldoStopLoss(saldoAtual)
    message += 'StopLoss = '+formatMoneyBRL(stopLoss)+'\n'
    maxgale = configReader.get('max_gale')
    message += 'Operando com '+maxgale+'MG\n'
    message += '--------------------------------------\n'
    message += 'Saldo atual = '+formatMoneyBRL(saldoAtual)+'\n'
    lucro = saldoAtual - saldoHoje
    lucroPorcentagem = (lucro/banca)*100
    message += 'Lucro = '+formatMoneyBRL(lucro)+' ('+'{:.2f}'.format(lucroPorcentagem)+'%)'
    return message


financeiroGetRich.getSaldoHoje(getBalance())
signalExecLine = []

def printSignalLineInfo():
    global signalExecLine
    LOG('== FILA DE ESPERA DE ENTRADA =>> ' + str(len(signalExecLine)))

def atualizarStakeFila():
    global signalExecLine
    for i in range(len(signalExecLine)):
        signalExecLine[i].stake = financeiroGetRich.getStake()

def getSignalsInLine():
    atualizarStakeFila()
    return signalExecLine


def clearSignalsLine():
    global signalExecLine
    if len(signalExecLine) > 0:
        signalExecLine = []
        return 'Fila zerada com sucesso!'
    signalExecLine = []
    return 'A fila já estava zerada!'


def getNextSignal():
    global signalExecLine
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

def processarResultado(signal, id, tipo):
    realizarMG = False
    profit = getResult(id, tipo)
    financeiroGetRich.addEntradaExecutada(signal, id, profit)
    if profit == None:
        print('Não foi possível pegar o resultado da entrada ID = ' + str(id))

    elif profit >= 0:
        LOG('Você lucrou = R$' + str('{:.2f}'.format(profit)) + ' ✅✅✅\nNa entrada ' + signal.toString())

    else:
        LOG('Você lucrou = R$' + str('{:.2f}'.format(profit)) + ' ❌\nNa entrada ' + signal.toString())
        realizarMG = True
    return realizarMG

def realizarOperacao(signal):
    completed, tipo, id = buy(signal)
    realizarMG = False
    if completed:
        message = '\n=====ENTRADA FEITA=====\n'
        if signal.qtdMG > 0:
            message += str(signal.qtdMG) + 'º MartinGale\n'
        message += 'ID = ' + str(id) + '\n' + signal.toString() + '\n=======================\n'
        print(message)
        time.sleep(30)
        realizarMG = processarResultado(signal, id, tipo)

    else:
        print('\nNão foi possível executar a entrada:\n' + signal.toString())

    return realizarMG

def executarSinal(signal):
    for i in range(int(configReader.get('max_gale')) + 1):
        signal.qtdMG = i
        podeExecutar, signalTemp = financeiroGetRich.podeExecutar(getBalance(), signal)
        signal = signalTemp
            
        if podeExecutar:
            realizarMG = realizarOperacao(signal)
            if not realizarMG:
                break
        else:
            break


def requestSignalExec(signal):
    if checkConnection():
        threading.Thread(target=executarSinal, args=(signal,)).start()
    else:
        print('\nNão foi possível se conectar à IQOPtion:\n' + signal.toString())


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

def resetarBanca():
    financeiroGetRich.atualizarBanca(getBalance())


def addSignal_OverMilionarios(signalMessage):
    resultMessage = None
    if configReader.get('ativar_overm') == 'S':
        if signalMessage.find("Gale sempre no mesmo sentido") != -1:
            signal = decodeSignalList.getSignal(signalMessage)
            if signal.isValid():
                signal.stake = financeiroGetRich.getStake()
                addSignalToLine(signal)
            resultMessage = '[OverMilionariosOB] Sinal ao-vivo adicionado na lista.'
    return resultMessage


def addList(message, listType):
    lines = message.splitlines()
    if listType == 'single':
        isValid, signalList = decodeSignalList.decodeSingleList(lines)
    elif listType == 'group':
        isValid, signalList = decodeSignalList.decodeGroupList(lines)
    else:
        isValid = False

    if isValid:
        stake = financeiroGetRich.getStake()
        for signal in signalList:
            signal.stake = stake
            addSignalToLine(signal)
    return isValid, len(signalList)