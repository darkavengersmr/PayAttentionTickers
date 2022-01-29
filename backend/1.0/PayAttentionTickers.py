#!/usr/bin/python3

# PayAttentionTickers

from threading import Thread

import app_db
import app_ticker
import api

import config

config.make_paths()

app_db.default_user_create()

ticker_ma_to_db_daemon_thread = Thread(target=app_ticker.ticker_ma_to_db_daemon, args=())
ticker_ma_to_db_daemon_thread.start()

api.api_daemon()



