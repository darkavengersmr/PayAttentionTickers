#!/usr/bin/python3

import time
import logging
from os import getenv
from sys import exit

from aiogram import Bot, Dispatcher, executor, types
from aiogram.utils.exceptions import BotBlocked
import asyncio
import aioschedule

import config, async_app_db, async_app_ticker

bot_token = getenv("BOT_TOKEN")
if not bot_token:
    exit("Error: no token provided")

bot = Bot(token=bot_token)

dp = Dispatcher(bot)
logging.basicConfig(level=logging.INFO)


@dp.errors_handler(exception=BotBlocked)
async def error_bot_blocked(update: types.Update, exception: BotBlocked):
    print(f"Меня заблокировал пользователь!\nСообщение: {update}\nОшибка: {exception}")
    return True


async def main_menu(message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    btn_list = ['\U0001F4C8 Анализ отклонений', '\U0001F4CA График по тикеру',
                '\U0001F4CB Список тикеров', '\U000023F0 Оповещения',
                '\U00002795 Добавить тикер', '\U00002796 Удалить тикер',
                '@ Запрос пароля']

    user_id = message.chat.id
    if await async_app_db.is_user(user_id):
        btn_list[2] = '\U0001F4CB Мои тикеры'
    keyboard.add(*btn_list)
    return keyboard


async def tickers_menu(user_id, operation='!'):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    all_tickers = await async_app_db.load_tickers(user_id)
    btn_list = []
    for tick in all_tickers:
        btn_list.append(f'{operation}{tick["id"]}')
    btn_list.append('\U0001F519 Назад')
    keyboard.add(*btn_list)
    return keyboard


@dp.message_handler(commands="start")
async def start_command(message: types.Message):
    bot_message = "\U0001F4B9 Бот предназначен для анализа котировок отслеживаемых ценных бумаг на отклонения от" \
                  " среднемесячных и средних за неделю значений и оповещения при наличии существенных отклонений"
    await message.answer(bot_message, reply_markup=await main_menu(message))


@dp.message_handler(lambda message: message.text == "status")
async def get_status(message: types.Message):
    bot_message = await async_app_db.get_status()
    await message.answer(bot_message, reply_markup=await main_menu(message))


@dp.message_handler(lambda message: message.text == "@ Запрос пароля")
async def get_password(message: types.Message):
    user_id = message.chat.id
    bot_message = f"Ваш логин {user_id} Новый пароль для входа {await async_app_db.get_new_pwd(user_id)}"
    await message.answer(bot_message, reply_markup=await main_menu(message))


@dp.message_handler(lambda message: message.text[0] == "+")
async def add_ticker(message: types.Message):
    user_id = message.chat.id
    tick = message.text[1:].split(',')[0]
    if message.text[1:].find(',') >= 0:
        desc = message.text[1:].split(',')[1].lstrip().rstrip()
    else:
        desc = tick

    ticker_incontrol = await async_app_ticker.exist_ticker(tick, user_id)
    if not ticker_incontrol:
        ticker_online = await async_app_ticker.probe_ticker(tick)
    else:
        ticker_online = True

    if ticker_online and not ticker_incontrol:
        tick_add_complete = await async_app_db.add_ticker(tick, desc, user_id)
        if tick_add_complete:
            bot_message = f'Добавлен тикер {tick} с описанием {desc}'
        else:
            bot_message = f'Не удалось добавить тикер {tick} с описанием {desc}'
    if ticker_incontrol:
        bot_message = f'Тикер {tick} уже отслеживается'
    if not ticker_online:
        bot_message = f'Тикер {tick} не найден на бирже'

    await message.answer(bot_message, reply_markup=await main_menu(message))


@dp.message_handler(lambda message: message.text.find('\U00002716') >= 0)
async def delete_ticker(message: types.Message):
    user_id = message.chat.id
    tick = message.text[1:]
    if await async_app_ticker.exist_ticker(tick, user_id):
        tick_remove_complete = await async_app_db.remove_ticker(tick, user_id)
        if tick_remove_complete:
            bot_message = f'Удален тикер {tick}'
        else:
            bot_message = f'Не удалось удалить тикер {tick}'
    else:
        bot_message = f'Тикер {tick} не отслеживается'

    await message.answer(bot_message, reply_markup=await main_menu(message))


@dp.message_handler(lambda message: message.text.find('\U0001F4C9') >= 0)
async def send_chart(message: types.Message):
    user_id = message.chat.id
    ticker = message.text[1:]
    chart_result = await async_app_ticker.chart_to_image(ticker)
    if chart_result:
        bot_message = f'График по тикеру {ticker} за последние три месяца'
        await async_app_db.write_to_log(user_id, f'Пользователю {user_id} отправлен график {ticker}')
    else:
        bot_message = f'Тикер {ticker} на бирже не найден'

    await bot.send_photo(message.chat.id,
                         open(config.FILEPATHS['charts'] + config.SYSTEM_SLASH + f'{ticker}.png', 'rb'),
                         caption=bot_message)


@dp.message_handler(lambda message: message.text == "\U0001F4C8 Анализ отклонений")
async def send_analized_tickers(message: types.Message):
    user_id = message.chat.id
    await message.answer(await async_app_ticker.analize_tickers(user_id, 1), reply_markup=await main_menu(message))
    await async_app_db.write_to_log(user_id, f'Пользователь {user_id} запросил анализ отклонений')


@dp.message_handler(lambda message: message.text == '\U0001F4CB Список тикеров' or message.text == '\U0001F4CB Мои тикеры')
async def get_my_tickers(message: types.Message):
    user_id = message.chat.id
    all_tickers = await async_app_db.load_tickers(user_id)

    if await async_app_db.is_user(user_id):
        bot_message = '\U0001F4CB Список отслеживаемых тикеров:\n'
    else:
        bot_message = '\U0001F4CB Список отслеживаемых Вами тикеров:\n'
    for tick in all_tickers:
        bot_message += "%s - %s\n" % (tick["id"], tick["name"])

    await message.answer(bot_message, reply_markup=await main_menu(message))


@dp.message_handler(lambda message: message.text == '\U000023F0 Оповещения')
async def set_alarms(message: types.Message):
    user_id = message.chat.id
    if await async_app_db.is_user(user_id) and await async_app_db.is_subscribe(user_id):
        bot_message = '\U000023F0 Отключил подписку на твои отслеживаемые тикеры. Больше ' + \
                              'не побеспокою.'
        await async_app_db.subscribe_add_remove(user_id)
    elif await async_app_db.is_user(user_id) and not await async_app_db.is_subscribe(user_id):
        bot_message = '\U000023F0 Включил подписку на твои отслеживаемые тикеры. Если будут ' + \
                              'существенные отклонения, я пришлю сообщение.'
        await async_app_db.subscribe_add_remove(user_id)
    elif not await async_app_db.is_user(user_id):
        bot_message = '\U000023F0 Я не веду список тикеров для тебя, поэтому не знаю на что ' + \
                              'тебя подписать. Если хочешь свой список, просто начинай добавлять или ' + \
                              'удалять тикеры, я создам для тебя личный список и ты сможешь подписаться.'
    if bot_message is not None:
        await message.answer(bot_message, reply_markup=await main_menu(message))


@dp.message_handler(lambda message: message.text == '\U0001F4CA График по тикеру')
async def select_ticker_to_make_chart(message: types.Message):
    user_id = message.chat.id
    await message.answer("Выберите тикер чтобы построить график", reply_markup=await tickers_menu(user_id,
                                                                                                   "\U0001F4C9"))


@dp.message_handler(lambda message: message.text == '\U00002795 Добавить тикер')
async def add_ticker(message: types.Message):
    await message.answer('\U0001F520 Введите имя тикера в формате +TICK,описание например +BABA, ' +
                        'Alibaba Group. Посмотреть список тикеров можно на https://finance.yahoo.com')


@dp.message_handler(lambda message: message.text == '\U00002796 Удалить тикер')
async def add_ticker(message: types.Message):
    user_id = message.chat.id
    await message.answer("Выберите тикер для удаления", reply_markup=await tickers_menu(user_id, "\U00002716"))


@dp.message_handler(lambda message: message.text == '\U0001F519 Назад')
async def go_back(message: types.Message):
    await message.answer("\U0001F4B9 Выберите команду в меню", reply_markup=await main_menu(message))


async def subscribe_daemon():
    subscribers = await async_app_db.subscribers_list()
    for user_id in subscribers:
        try:
            bot_message = await async_app_ticker.analize_tickers(user_id, 2)
            await bot.send_message(user_id, bot_message)
        except Exception:
            print(f'chat with {user_id} not found')


async def scheduler():
    aioschedule.every().day.at("11:45").do(subscribe_daemon)
    while True:
        await aioschedule.run_pending()
        await asyncio.sleep(60)


async def on_startup(_):
    asyncio.create_task(scheduler())


if __name__ == "__main__":
    while True:
        try:
            executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
        except Exception:
            print("Ошибка связи с Telegram API")
            time.sleep(30)

