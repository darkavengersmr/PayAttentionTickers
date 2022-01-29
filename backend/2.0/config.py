#!/usr/bin/python3

#file  -- config.py --

# asyncPayAttentionTickers

import platform
import os

db_connection = 'postgresql+asyncpg://pi:raspberry@192.168.32.64:5433/PayAttentionTickers'

redis_connection = {'host': '192.168.32.64', 'port': 6379, 'db': 0}

tickers = [('VOO', 'S&P 500'),
               ('IMOEX.ME', 'Индекс Мосбиржи'),
               ('GAZP.ME', 'Газпром'),
               ('GMKN.ME', 'Норильский никель'),
               ('SBERP.ME', 'Сбербанк-п'),
               ('MTSS.ME', 'МТС'),
               ('LKOH.ME', 'Лукойл'),
               ('SNGSP.ME', 'Сургутнефтегаз-п'),
               ('TATNP.ME', 'Татнефть-п'),
               ('BA', 'The Boeing Company'),
               ('CVX', 'Chevron'),
               ('XOM', 'Exxon Mobil'),
               ('BABA', 'Alibaba Group'),
               ('FXCN.ME', 'FinEx ETF Китайские компании'),
               ('FXDE.ME', 'FinEx ETF Немецкие компании'),
               ('FXGD.ME', 'FinEx ETF Золото')]

BOT_ID = ''

my_platform = platform.system()
if my_platform == 'Windows':
    SYSTEM_SLASH = '\\'
else:
    SYSTEM_SLASH = '/'

catalogs = ['charts', 'upload', 'download']
programm_path = os.path.dirname(os.path.realpath(__file__))

def make_paths():
    FILEPATHS = {}
    FILEPATHS_WEB = f'{programm_path}{SYSTEM_SLASH}web'
    if not os.path.exists(FILEPATHS_WEB):
        os.mkdir(FILEPATHS_WEB)
    FILEPATHS_WEB_STATIC = f'{programm_path}{SYSTEM_SLASH}web{SYSTEM_SLASH}static'
    if not os.path.exists(FILEPATHS_WEB_STATIC):
        os.mkdir(FILEPATHS_WEB_STATIC)
    for catalog in catalogs:
        FILEPATHS[catalog] = f'{programm_path}{SYSTEM_SLASH}web{SYSTEM_SLASH}static{SYSTEM_SLASH}{catalog}'
        if not os.path.exists(FILEPATHS[catalog]):
            os.mkdir(FILEPATHS[catalog])
    return FILEPATHS

FILEPATHS = make_paths()

UPLOAD_FOLDER = f'{programm_path}{SYSTEM_SLASH}web{SYSTEM_SLASH}static{SYSTEM_SLASH}upload'
ALLOWED_EXTENSIONS = {'xls', 'xlsx'}