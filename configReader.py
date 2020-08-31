import configparser

ERROR_MESSAGE = '[CONFIG_READER] Erro ao ler configurações. Contate o administrador!'
SECTION_NAME = 'GetRichBOT'
FILE_NAME = 'config.ini'

def getReader():
    parser = None
    try:
        parser = configparser.ConfigParser()
        parser.read(FILE_NAME, encoding='utf-8')
    except:
        print(ERROR_MESSAGE)

    return parser

def get(name):
    config = None
    parser = getReader()
    if parser != None:
        config = parser.get(SECTION_NAME, name)

    return config


def getAll():
    configs = []
    parser = getReader()
    if parser != None:
        for config in parser[SECTION_NAME]:
            configs.append(config)
    return configs

def edit(name, value):
    edited = False
    parser = getReader()
    if parser != None:
        parser.set(SECTION_NAME, name, value)
        with open(FILE_NAME, 'w') as configfile:
            parser.write(configfile)
        edited = True
    return edited
