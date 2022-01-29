#!/usr/bin/python3

from threading import Thread

import datetime
import time

import telebot
from telebot import types

import config
import app_db
import app_ticker

bot = telebot.TeleBot(config.BOT_ID, threaded=True)


def probe_user(user_id):
    message = 'Проверка соединения...'
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    try:
        bot.send_message(user_id, text=message, reply_markup=markup)
        return True
    except:
        return False


def main_menu(markup, user_id):
    btn_list = ['\U0001F4C8 Анализ отклонений', '\U0001F4CA График по тикеру',
                '\U0001F4CB Список тикеров', '\U000023F0 Оповещения',
                '\U00002795 Добавить тикер', '\U00002796 Удалить тикер',
                '@ Запрос пароля']

    if app_db.is_user(user_id):
        btn_list[2] = '\U0001F4CB Мои тикеры'

    markup.add(*btn_list)


def tickers_menu(markup, user_id, operation='!'):
    all_tickers = app_db.load_tickers(user_id)
    btn_list = []
    for tick in all_tickers:
        btn_list.append(types.KeyboardButton("%s%s" % (operation, tick['id'])))
    btn_list.append('\U0001F519 Назад')
    markup.add(*btn_list)


@bot.message_handler(commands=['start'])
def start_command(message):
    user_id = message.from_user.id
    bot_message = "\U0001F4B9 Бот предназначен для анализа котировок отслеживаемых ценных бумаг на отклонения от" \
                  " среднемесячных и средних за неделю значений и оповещения при наличии существенных отклонений"
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    main_menu(markup, user_id)
    bot.send_message(message.chat.id, text=bot_message, reply_markup=markup)


@bot.message_handler(content_types=['text'])
def send_text(message):
    user_id = message.from_user.id
    bot_message = ''

    if message.text == 'status':
        bot_message = app_db.get_status()

        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        main_menu(markup, user_id)
        bot.send_message(message.chat.id, text=bot_message, reply_markup=markup)

    elif message.text == '@ Запрос пароля':

        bot_message = f"Ваш логин {user_id} Новый пароль для входа {app_db.get_new_pwd(user_id)}"

        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        main_menu(markup, user_id)
        bot.send_message(message.chat.id, text=bot_message, reply_markup=markup)

    elif message.text[0] == '+':
        tick = message.text[1:].split(',')[0]
        if message.text[1:].find(',') >= 0:
            desc = message.text[1:].split(',')[1].lstrip().rstrip()
        else:
            desc = tick

        ticker_incontrol = app_ticker.exist_ticker(tick, user_id)
        if not ticker_incontrol:
            ticker_online = app_ticker.probe_ticker(tick)
        else:
            ticker_online = True

        if ticker_online and not ticker_incontrol:
            tick_add_complete = app_db.add_ticker(tick, desc, user_id)
            if tick_add_complete:
                bot_message = f'Добавлен тикер {tick} с описанием {desc}'
            else:
                bot_message = f'Не удалось добавить тикер {tick} с описанием {desc}'
        if ticker_incontrol:
            bot_message = f'Тикер {tick} уже отслеживается'
        if not ticker_online:
            bot_message = f'Тикер {tick} не найден на бирже'

        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        main_menu(markup, user_id)
        bot.send_message(message.chat.id, text=bot_message, reply_markup=markup)
    
    elif message.text.find('\U00002716') >= 0:
        tick = message.text[1:]
        if app_ticker.exist_ticker(tick, user_id):
            tick_remove_complete = app_db.remove_ticker(tick, user_id)
            if tick_remove_complete:
                bot_message = f'Удален тикер {tick}'
            else:
                bot_message = f'Не удалось удалить тикер {tick}'
        else:
            bot_message = f'Тикер {tick} не отслеживается'

        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        main_menu(markup, user_id)
        bot.send_message(message.chat.id, text=bot_message, reply_markup=markup)

    elif message.text.find('\U0001F4C9') >= 0:

        ticker = message.text[1:]
        chart_result = app_ticker.chart_to_image(ticker)
        bot.send_photo(user_id, open(config.FILEPATHS['charts'] + config.SYSTEM_SLASH + f'{ticker}.png', 'rb'))
        if chart_result:
            bot_message = f'График по тикеру {ticker} за последние три месяца'
            app_db.write_to_log(user_id, f'Пользователю {user_id} отправлен график {ticker}')
        else:
            bot_message = f'Тикер {ticker} на бирже не найден'

        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        main_menu(markup, user_id)
        bot.send_message(message.chat.id, text=bot_message, reply_markup=markup)

    elif message.text == '\U0001F4C8 Анализ отклонений':
        bot.send_message(message.chat.id, "\U0001F55A Пожалуйста, подождите...")
        app_db.write_to_log(user_id, f'Пользователь {user_id} запросил анализ отклонений')
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        main_menu(markup, user_id)
        bot.send_message(message.chat.id, text=app_ticker.analize_tickers(user_id, 1), reply_markup=markup)


    elif message.text == '\U0001F4CB Список тикеров' or message.text == '\U0001F4CB Мои тикеры':
        all_tickers = app_db.load_tickers(user_id)

        if app_db.is_user(user_id):
            all_tickers_message = '\U0001F4CB Список отслеживаемых тикеров:\n'
        else:
            all_tickers_message = '\U0001F4CB Список отслеживаемых Вами тикеров:\n'
        for tick in all_tickers:
            all_tickers_message += "%s - %s\n" % (tick["id"], tick["name"])
        #print (all_tickers_message)
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        main_menu(markup, user_id)
        bot.send_message(message.chat.id, text=all_tickers_message, reply_markup=markup)

    elif message.text == '\U000023F0 Оповещения':
        all_tickers_message = ''
        if app_db.is_user(user_id) and app_db.is_subscribe(user_id):
            all_tickers_message = '\U000023F0 Отключил подписку на твои отслеживаемые тикеры. Больше ' + \
                                  'не побеспокою.'
            app_db.subscribe_add_remove(user_id)
        elif app_db.is_user(user_id) and not app_db.is_subscribe(user_id):
            all_tickers_message = '\U000023F0 Включил подписку на твои отслеживаемые тикеры. Если будут ' + \
                                  'существенные отклонения, я пришлю сообщение.'
            app_db.subscribe_add_remove(user_id)
        elif not app_db.is_user(user_id):
            all_tickers_message = '\U000023F0 Я не веду список тикеров для тебя, поэтому не знаю на что ' + \
                                  'тебя подписать. Если хочешь свой список, просто начинай добавлять или ' + \
                                  'удалять тикеры, я создам для тебя личный список и ты сможешь подписаться.'

        # markup = telebot.types.InlineKeyboardMarkup()
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        main_menu(markup, user_id)
        bot.send_message(message.chat.id, text=all_tickers_message, reply_markup=markup)

    elif message.text == '\U0001F4CA График по тикеру':
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True,row_width=2)
        all_tickers = app_db.load_tickers(user_id)
        btn_list = []
        for tick in all_tickers:
            btn_list.append(types.KeyboardButton('%s' % tick['id']))
        markup.add(*btn_list)

        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        tickers_menu(markup, user_id, "\U0001F4C9")
        bot.send_message(message.chat.id, "Выберите тикер чтобы построить график:", reply_markup=markup)

    elif message.text == '\U00002795 Добавить тикер':
        bot.send_message(message.chat.id, '\U0001F520 Введите имя тикера в формате +TICK,описание например +BABA, ' +
                                          'Alibaba Group. Посмотреть список тикеров можно на https://finance.yahoo.com')
    elif message.text == '\U00002796 Удалить тикер':
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        tickers_menu(markup, user_id, "\U00002716")
        bot.send_message(message.chat.id, text='Выберите тикер для удаления', reply_markup=markup)
    elif message.text == '\U0001F519 Назад':
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        main_menu(markup, user_id)
        bot.send_message(message.chat.id, text="\U0001F4B9 Выберите команду в меню", reply_markup=markup)
    else:
        bot_message = "\U000026D4 команда не распознана"
        # markup = telebot.types.InlineKeyboardMarkup()
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        main_menu(markup, user_id)
        bot.send_message(message.chat.id, text=bot_message, reply_markup=markup)

def subscribe_daemon():
    while True:
        date = datetime.datetime.today()
        if date.strftime('%H') == '11':
            subscribers = app_db.subscribers_list()
            for user_id in subscribers:
                try:
                    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
                    bot.send_message(user_id, text=app_ticker.analize_tickers(user_id, 2), reply_markup=markup)
                    app_db.write_to_log(user_id, f'Выполнена рассылка пользователю {user_id}')
                except:
                    print(f'chat {user_id} not found')

        time.sleep(3600)


subscribe_daemon_thread = Thread(target=subscribe_daemon, args=())
subscribe_daemon_thread.start()

while True:
    bot.remove_webhook()
    try:
        bot.polling(none_stop=True)
    except Exception as e:
        app_db.write_to_log('default', "Ошибка связи с Telegram API")
        print("Ошибка связи с Telegram API")
        time.sleep(30)

