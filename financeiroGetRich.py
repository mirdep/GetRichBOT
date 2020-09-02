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

def LOG(message):
    print('\n'+LOG_LABEL + ' ' + message)


def formatTime(timestamp):
    time = datetime.fromtimestamp(timestamp)
    return '{:02d}'.format(time.day) + '/' + '{:02d}'.format(time.month) + '/' + '{:02d}'.format(time.year % 100) + ' ' + '{:02d}'.format(time.hour) + ':' + '{:02d}'.format(time.minute)


def getBanca(balance, deHoje=False):
    banca = None
    if deHoje:
        juros = 'composto'
    else:
        juros = configReader.get('juros')

    if juros == 'simples':
        banca = float(configReader.get('banca'))
    
    elif juros == 'composto':
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


def getStake(balance):
    stakePorcentagem = float(configReader.get('stake'))
    banca = getBanca(balance)
    return banca*(stakePorcentagem/100)


def podeExecutar(balance):
    podeExecutar = False
    stake = 0
    banca = getBanca(balance, deHoje=True)
    lucro = balance-banca

    stopWin = banca * (float(configReader.get('stop_win')) / 100)
    stopLoss = 0 - banca * (float(configReader.get('stop_loss')) / 100)

    if lucro > stopWin and lucro < stopWin*1.05:
        LOG('Você já atingiu seu Stop Win de hoje. Parabéns, já pode descansar!')
    elif lucro >= stopWin*1.05:
        LOG('Você já atingiu seu Stop Win de hoje. Operando com a gordura!')
        podeExecutar = True
        stake = lucro - stopWin
        if stake > getStake(balance):
            stake = getStake(balance)
    elif lucro <= stopLoss:
        LOG('Você já atingiu seu Stop Loss de hoje. Não desanime, amanhã você vai recuperar!')
    else:
        podeExecutar = True
        stake = getStake(balance)
    return podeExecutar, stake


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