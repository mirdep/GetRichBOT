print('===========>>> GetRich BOT <<<==========')
print('Seu exclusivo leitor de sinais ao vivo!')
print('Created by Mirdep')
print('Acesse nossos repositórios https://github.com/mirdep')
print('========================================')

import configReader
import sys

MEU_ID = configReader.get('meu_id')
idAutorizados = ['945914960','1042619274','865937158']
if not MEU_ID in idAutorizados:
	input('>>> ACESSO NÃO AUTORIZADO <<<\n\nAperte enter para sair...')
	sys.exit()
import telegramGetRich
