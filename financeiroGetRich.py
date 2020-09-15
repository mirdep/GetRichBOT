from datetime import datetime
import configReader, time


HISTORICO_BANCA = 'banca.stats'
with open(HISTORICO_BANCA, 'a') as (writer):
    pass
HISTORICO_ENTRADA = 'entradas.stats'
with open(HISTORICO_ENTRADA, 'a') as (writer):
    pass

LOG_LABEL = '[Financeiro]'
SEPARATOR = ' | '

MINIMUM_STAKE = 2

def LOG(message):
    print('\n'+LOG_LABEL + ' ' + message)


def formatTime(timestamp):
    time = datetime.fromtimestamp(timestamp)
    return '{:02d}'.format(time.day) + '/' + '{:02d}'.format(time.month) + '/' + '{:02d}'.format(time.year % 100) + ' ' + '{:02d}'.format(time.hour) + ':' + '{:02d}'.format(time.minute)


def calculateGale(stake):
    if type(stake) == float or type(stake) == int:
        return stake * 2
    return 0

def getBanca():
    return float(configReader.get('banca'))

def getSaldoHoje(balance):
    banca = None
    with open(HISTORICO_BANCA) as (reader):
        bancas = reader.read().splitlines()
        if len(bancas) > 0:
            bancaRecente = bancas[(len(bancas) - 1)].split(SEPARATOR)
            tempo = datetime.fromtimestamp(float(bancaRecente[2]))
            now = datetime.now()
            if tempo.month == now.month and tempo.day == now.day:
                banca = float(bancaRecente[1])
    if banca == None:
        atualizarBanca(balance)
        banca = balance
    return banca

def atualizarBanca(balance):
    try:
        with open(HISTORICO_BANCA, 'a') as (writer):
            now = datetime.timestamp(datetime.now())
            writer.write(formatTime(now) + SEPARATOR + '{:.2f}'.format(balance) + SEPARATOR + str(now) + '\n')
    except:
        LOG('Não foi possível salvar os dados da banca! Contate o administrador.')


def getStake():
    stakePorcentagem = float(configReader.get('stake'))
    banca = getBanca()
    return banca*(stakePorcentagem/100)

def getSaldoStopWin(saldoAtual):
    return getSaldoHoje(saldoAtual) + getBanca() * (float(configReader.get('stop_win')) / 100)

def getSaldoStopLoss(saldoAtual):
    return getSaldoHoje(saldoAtual) - getBanca() * (float(configReader.get('stop_loss')) / 100)    


def podeExecutar(saldoAtual, signal):
    podeExecutar = False

    saldoStopWin = getSaldoStopWin(saldoAtual)
    saldoStopLoss = getSaldoStopLoss(saldoAtual)

    if saldoAtual >= saldoStopWin and saldoAtual < saldoStopWin+MINIMUM_STAKE:
        LOG('Você já atingiu seu Stop Win de hoje. Parabéns, já pode descansar!')
    elif saldoAtual >= saldoStopWin+MINIMUM_STAKE:
        if signal.qtdMG == 0:
            LOG('Você já atingiu seu Stop Win de hoje. Operando com a gordura!')
            podeExecutar = True
            signal.stake = (saldoAtual - saldoStopWin)/3
            if signal.stake > getStake():
                signal.stake = getStake()
        else:
            if signal.stake*2 >= saldoAtual - saldoStopWin:
                LOG('Realizando Gale na gordura!')
                podeExecutar = True
                signal.stake = calculateGale(signal.stake)
            else:
                LOG('Gordura insuficiente para realizar Gale!')
    elif saldoAtual <= saldoStopLoss:
        LOG('Você já atingiu seu Stop Loss de hoje. Não desanime, amanhã você vai recuperar!')
    else:
        podeExecutar = True
        if signal.qtdMG > 0:
            signal.stake = calculateGale(signal.stake)
        else:
            signal.stake = getStake()
    return podeExecutar, signal


def addEntradaExecutada(signal, id, profit):
    with open(HISTORICO_ENTRADA, 'a') as (writer):
        now = datetime.timestamp(datetime.now())
        writer.write(formatTime(now) + SEPARATOR + 'ID = ' + str(id) + SEPARATOR + signal.toString() + SEPARATOR + 'R$' + '{:.2f}'.format(profit) + SEPARATOR + str(now) + '\n')


def getEntradasExecutadasHoje():
    entradasExecutadas = []
    with open(HISTORICO_ENTRADA) as (reader):
        entradas = reader.read().splitlines()
        now = datetime.now()
        for entrada in entradas:
            info = entrada.split(SEPARATOR)
            data = info[0].split('/')
            if int(data[0]) == now.day and int(data[1]) == now.month and int(data[2][0:2]) == now.year%100:
                message = info[0].split(' ')[1] + SEPARATOR + info[3]
                if info[3].find('-') != -1:
                    message += ' ❌'
                else:
                    message += ' ✅'
                entradasExecutadas.append(message)

    if len(entradasExecutadas) > 0:
        return entradasExecutadas
    else:
        return ['Nenhuma entrada realizada hoje!\nBora operar e ganhar dinheiro ✅🔥🚀']