from telethon import TelegramClient, events
from iqoptionapi.stable_api import IQ_Option
import logging
import configReader
from datetime import datetime
import sys
import time
import signalGetRich
import threading

logging.basicConfig(format='[%(levelname) 5s/%(asctime)s] %(name)s: %(message)s', level=(logging.WARNING))

print('Iniciado em: '+str(datetime.now()))

import iqoptionGetRich

#========= TELEGRAM START ==========
API_ID = configReader.get('api_id')
API_HASH = configReader.get('api_hash')
MEU_NICK = configReader.get('meu_nick')
print('[TELEGRAM API] Inicializando...')
telegramClient = TelegramClient('GetRichBOT', API_ID, API_HASH)


#============= MAIN ===============
MEU_ID = configReader.get('meu_id')
commandState = [0, 0]
lastConfig = ''

def isAscii(char):
    isAscii = False
    allowedChars = 'abcdefghijklmnopqrstuvwxyz0123456789 /:;\n'
    for i in allowedChars:
        if char == i:
            isAscii = True
            break
    return isAscii


def cleanMessage(message):
    cleaned_message = ''
    for i in message:
        if isAscii(i):
            cleaned_message = cleaned_message + i
    return cleaned_message


async def getUsername():
    user = await telegramClient.get_me()
    return user.username


async def sendMessage(message):
    if message:
        await telegramClient.send_message(MEU_NICK, '====[GetRich BOT]====\n' + message)


def isMe(event):
    isMe = False
    info = str(event)
    index = info.find('user_id=')
    if index != -1:
        indexFim = index+8
        while info[indexFim].isdigit():
            indexFim += 1
        if info[index + 8:indexFim] == MEU_ID:
            isMe = True
    return isMe


def isOverMilionarios(sender):
    OVERMILIONARIOS_ID = configReader.get('overmilionarios_id')
    return str(sender.id) == OVERMILIONARIOS_ID


def isForwarded(event):
    info = str(event)
    id = None
    if info.find('from_id=' + MEU_ID) != -1:
        if info.find('fwd_from=None') == -1:
            index = info.find('channel_id')
            if index != -1:
                if info[index + 11:index + 15] != 'None':
                    id = info[index + 11:index + 21]
    return id

async def cmd_adicionarLista(message):
    global commandState
    if commandState[1] == 0:
        await sendMessage('Vamos adicionar uma lista de execução!\nSua lista possui a duração por sinal?[S,N]')
        commandState[1] = 1

    elif commandState[1] == 1:
        message = message.upper().strip()
        if message == 'S':
            await sendMessage('OK. Envie a lista desejada, sendo 1 sinal por linha, e remova linhas extras.')
            commandState[1] = 11
        elif message == 'N':
            await sendMessage('OK. Envie a lista desejada, sendo a 1ª linha com o tempo "M1" ou "M5" ou "M15", e as próximas linhas com os sinais.')
            commandState[1] = 21
        else:
            await sendMessage('Comando inválido. Você voltará para o menu inicial.')
            commandState = [0, 0]

    elif commandState[1] == 11 or commandState[1] == 21:
        await sendMessage('Iniciando verificação da lista. Pode demorar alguns segundos...')
        if commandState[1] == 11:
            isValid, qtdSinaisValidos = iqoptionGetRich.addList(message, 'single')
        else:
            isValid, qtdSinaisValidos = iqoptionGetRich.addList(message, 'group')

        if isValid:
            await sendMessage('Lista verificada! Foram adicionados '+str(qtdSinaisValidos)+' sinais.')
        else:
            await sendMessage('Nenhum sinal válido foi identificado. Tente novamente.')
        commandState = [0, 0]


async def cmd_listarFilaSinais():
    await sendMessage(iqoptionGetRich.getSignalsInLine())


async def cmd_zerarFila():
    await sendMessage(iqoptionGetRich.clearSignalsLine())


async def cmd_mostrarSaldo():
    await sendMessage(iqoptionGetRich.getSaldo())


async def cmd_desligar():
    await sendMessage('Até mais noia!\nDesligando...')
    iqoptionGetRich.desligar()
    time.sleep(3)
    await telegramClient.disconnect()
    sys.exit()


async def cmd_entradasExecutadas():
    entradas = ''
    for entrada in iqoptionGetRich.getEntradasExecutadasHoje():
        entradas += entrada + '\n'

    await sendMessage(entradas)


async def cmd_editarConfigs(message):
    global commandState
    global lastConfig
    if commandState[1] == 0:
        configs = configReader.getAll()
        reply = ''
        for config in configs:
            reply += '- '+config+'\n'
        reply += '\nDeseja alterar qual configuração? Digite X para cancelar.'
        await sendMessage(reply)
        commandState[1] = 1

    elif commandState[1] == 1:
        if message.strip().upper() == 'X':
            commandState = [0,0]
        else:
            try:
                config = configReader.get(message)
                await sendMessage('Valor atual - '+message +' = '+ config+'\nDigite o novo valor da configuração! X para cancelar')
                commandState[1] = 2
                lastConfig = message
            except:
                await sendMessage('A configuração escolhida não existe, tente novamente.')
                commandState = [0,0]

    elif commandState[1] == 2:
        if message.strip().upper() != 'X':
            edited = configReader.edit(lastConfig, message.strip())
            if edited:
                await sendMessage('Você alterou o valor de "'+lastConfig+'" para "'+message.strip()+'".')
            else:
                await sendMessage('Não foi possível alterar a condiguração.')
        commandState = [0,0]

async def cmd_resetarSaldo(message):
    global commandState
    if commandState[1] == 0:
        await sendMessage('Esse comando serve para zerar a contagem do lucro de hoje.\nDeseja continuar? (S/N)')
        commandState[1] = 1

    elif commandState[1] == 1:
        if message == 'S':
            iqoptionGetRich.resetarBanca()
            await sendMessage('Lucro resetado com sucesso!')
            await cmd_mostrarSaldo()
        commandState = [0,0]


@telegramClient.on(events.NewMessage)
async def my_event_handler(event):
    global commandState
    message = event.text
    sender = await event.get_sender()

    from_id = isForwarded(event)
    if from_id != None:
        commandState = [0, 0]
        await sendMessage('Mensagem foi encaminhada do ID = ' + from_id)

    elif isOverMilionarios(sender):
        result = iqoptionGetRich.addSignal_OverMilionarios(message)
        await sendMessage(result)

    elif isMe(event):
        if commandState[0] == 0:
            command = message.lower()
            if command == '/lista':
                commandState = [1, 0]
            elif command == '/fila':
                commandState = [2, 0]
            elif command == '/zerarfila':
                commandState = [3, 0]
            elif command == '/saldo':
                commandState = [4, 0]
            elif command == '/desligar':
                commandState = [5, 0]
            elif command == '/executadas':
                commandState = [6, 0]
            elif command == '/config':
                commandState = [7, 0]
            elif command == '/resetar':
                commandState = [8, 0]
            else:
                await sendMessage('Olá seu noiado!\nSegue a lista de comandos disponíveis: \n\n/lista \n/fila \n/zerarfila \n/saldo \n/desligar \n/executadas \n/config \n/resetar')

        if commandState[0] == 1:
            await cmd_adicionarLista(message)

        elif commandState[0] == 2:
            await cmd_listarFilaSinais()
            commandState = [0, 0]

        elif commandState[0] == 3:
            await cmd_zerarFila()
            commandState = [0, 0]

        elif commandState[0] == 4:
            await cmd_mostrarSaldo()
            commandState = [0, 0]

        elif commandState[0] == 5:
            await cmd_desligar()
            commandState = [0, 0]

        elif commandState[0] == 6:
            await cmd_entradasExecutadas()
            commandState = [0, 0]

        elif commandState[0] == 7:
            await cmd_editarConfigs(message)

        elif commandState[0] == 8:
            await cmd_resetarSaldo(message)

#======= TESTES
#iqoptionGetRich.execSignal(signalGetRich.Signal(1598590445,100,'EURUSD','put',1))
#iqoptionGetRich.execSignal(signalGetRich.Signal(1598590445,100,'EURUSD','call',1))

def startTelegram():
    try:
        telegramClient.start(configReader.get('telefone'))
        print('[TELEGRAM API] Login feito com sucesso!')
        print('[GetRich BOT] Bot já está aguardando por novos sinais!')
        telegramClient.run_until_disconnected()
    except:
        startTelegram()

startTelegram()