#!/usr/bin/python3

from datetime import datetime, timedelta
import string
import random

from werkzeug.security import generate_password_hash

import asyncio

# импортируем асинхронные методы sqlalchemy для работы с БД
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

# импортируем метод работы с бд, фабрику сессий и связи
from sqlalchemy.orm import declarative_base, sessionmaker, relationship, joinedload

from sqlalchemy import select, delete, update, insert

from config import db_connection, tickers

from models import Users, Tickers, Logs, StockExchange

from async_app_ticker import get_tickers_list, ticker_price_to_ma

# создаем движок
engine = create_async_engine(db_connection, echo=False)

# создаем метод описания БД (Создаем базовый класс для декларативных определений классов.)
Base = declarative_base()

# создаем сессию (Фабрика sessionmaker генерирует новые объекты Session при вызове)
Session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def write_to_log(user_id, message):
    result = False
    user_id = str(user_id)
    if not await is_user(user_id):
        await create_user(user_id)
    async with Session() as session:
        async with session.begin():
            log = Logs(date=datetime.now(), user_id=user_id, message=message)
            session.add(log)


async def is_user(user_id):
    user_id = str(user_id)
    async with Session() as session:
        statement = (
            select(Users.user_id)
                .where(Users.user_id == user_id)
        )
        result = await session.execute(statement)
        if result.scalar() == user_id:
            return True
        else:
            return False


async def create_user(user_id):
    result = False
    user_id = str(user_id)

    user = await is_user(user_id)
    if not user and user_id != 'unknown':
        async with Session() as session:
            async with session.begin():
                user = Users(user_id=user_id)
                session.add(user)

        async with Session() as session:
            statement = (
                delete(Tickers)
                    .where(Tickers.user_id == user_id)
            )
            await session.execute(statement)
            await session.commit()

        for ticker in tickers:
            deviat_month, deviat_week = await ticker_price_to_ma(ticker[0])
            if deviat_month == 'error': deviat_month = 0
            if deviat_week == 'error': deviat_week = 0
            async with Session() as session:
                async with session.begin():
                    new_ticket = Tickers(user_id=user_id, ticker_id=ticker[0], ticker_desc=ticker[0], deviat_month=deviat_month, deviat_week=deviat_week)
                    session.add(new_ticket)


async def remove_user(user_id):
    result = False
    user_id = str(user_id)

    if user_id != 'unknown':
        async with Session() as session:
            statement = (
                delete(Tickers)
                    .where(Tickers.user_id == user_id)
            )
            await session.execute(statement)
            statement = (
                delete(Users)
                    .where(Users.user_id == user_id)
            )
            await session.execute(statement)
            await session.commit()
            result = True
    return result

async def load_tickers(user_id):
    user_id = str(user_id)
    result_list = list()
    user = await is_user(user_id)
    if not user:
        user_id = 'default'

    async with Session() as session:
        statement = (
            select(Tickers.ticker_id, Tickers.ticker_desc, Tickers.deviat_month, Tickers.deviat_week, Tickers.update_date)
                .where(Tickers.user_id == user_id)
        )
        result_tmp = await session.execute(statement)

        for ticker_id, ticker_desc, deviat_month, deviat_week, update_date in result_tmp:
            result_list.append({ 'id': ticker_id,
                                 'name': ticker_desc,
                                 'deviat_month': deviat_month,
                                 'deviat_week': deviat_week,
                                 'update_date': str(update_date).split(" ")[0] })
    return result_list


async def get_all_tickers():
    tmp_list = list()
    async with Session() as session:
        statement = (
            select(Tickers.ticker_id)
                .group_by(Tickers.ticker_id)
        )
        tmp_list = await session.execute(statement)
    result_list = [a[0] for a in tmp_list]
    return result_list


async def set_ticker_ma(ticker_id, ticker_ma20, ticker_ma5):
    tmp_list = list()
    async with Session() as session:
        statement = (
            update(Tickers)
                .where(Tickers.ticker_id == ticker_id)
                .values(deviat_month=ticker_ma20, deviat_week=ticker_ma5, update_date=datetime.now())
        )
        await session.execute(statement)
        await session.commit()
    return True


async def add_ticker(ticker, description, user_id):
    result = False
    user_id = str(user_id)
    if not await is_user(user_id):
        await create_user(user_id)
    deviat_month, deviat_week = await ticker_price_to_ma(ticker)
    async with Session() as session:
        statement = (
            insert(Tickers)
                .values(user_id=user_id, ticker_id=ticker, ticker_desc=description, deviat_month=deviat_month, deviat_week=deviat_week, update_date=datetime.now())
        )
        await session.execute(statement)
        await session.commit()
        result = True
        await write_to_log(user_id, f'Пользователь {user_id} добавил новый тикер {ticker} с описанием {description}')
    return result


async def update_ticker(ticker, description, user_id):
    result = True
    user_id = str(user_id)
    if not await is_user(user_id):
        await create_user(user_id)

    async with Session() as session:
        statement = (
            update(Tickers)
                .where(Tickers.ticker_id==ticker, Tickers.user_id==user_id)
                .values(ticker_desc=description)
        )
        await session.execute(statement)
        await session.commit()
        await write_to_log(user_id, f'Пользователь {user_id} изменил описание тикера {ticker} на {description}')
    return result


async def remove_ticker(ticker_to_remove, user_id):
    result = False
    user_id = str(user_id)
    if not await is_user(user_id):
        await create_user(user_id)

    async with Session() as session:
        statement = (
            delete(Tickers)
                .where(Tickers.user_id == user_id, Tickers.ticker_id == ticker_to_remove)
        )
        await session.execute(statement)
        await session.commit()
        result = True
        await write_to_log(user_id, f'Пользователь {user_id} удалил тикер {ticker_to_remove}')
    return result


async def is_subscribe(user_id):
    user_id = str(user_id)
    async with Session() as session:
        statement = (
            select(Users.alarm)
                .where(Users.user_id == user_id)
        )
        result = await session.execute(statement)
        result = list(result)
        if len(result)>0:
            return bool(result[0][0])
        else:
            return False


async def subscribe_add_remove(user_id):
    user_id = str(user_id)
    if not await is_user(user_id):
        await create_user(user_id)

    alarm = not await is_subscribe(user_id)

    async with Session() as session:
        statement = (
            update(Users)
                .where(Users.user_id==user_id)
                .values(alarm=alarm)
        )
        await session.execute(statement)
        await session.commit()
        #await write_to_log(user_id, f'Пользователь {user_id} изменил статус своей подписки на {is_subscribe(user_id)}')


async def subscribers_list():
    async with Session() as session:
        statement = (
            select(Users.user_id)
                .where(Users.user_id!='default', Users.alarm==True)
        )
        tmp_list = await session.execute(statement)
    result_list = [a[0] for a in tmp_list]
    return result_list


async def get_status():
    async with Session() as session:
        statement = (
            select(Users.user_id)
                .where(Users.user_id!='default')
        )
        tmp_list = await session.execute(statement)
    result_list = [a[0] for a in tmp_list]
    result = "Всего пользователей: " + str(len(result_list))
    return result


async def get_all_users():
    async with Session() as session:
        statement = (
            select(Users.user_id)
        )
        tmp_list = await session.execute(statement)
    result_list = [a[0] for a in tmp_list]
    return result_list


async def get_token(user_id):
    async with Session() as session:
        statement = (
            select(Users.token)
                .where(Users.user_id==user_id, Users.token_exp > datetime.now() - timedelta(days=30))
        )
        token = await session.execute(statement)
    result_list = [a[0] for a in token]
    if len(result_list)>0:
        return result_list[0]
    else:
        return None


async def get_hash_pwd(user_id):
    async with Session() as session:
        statement = (
            select(Users.user_pwd)
                .where(Users.user_id==user_id)
        )
        token = await session.execute(statement)
    result_list = [a[0] for a in token]
    if len(result_list)>0:
        return result_list[0]
    else:
        return None


async def randompassword(min, max):
    chars = string.ascii_uppercase + string.ascii_lowercase + string.digits
    size = random.randint(min, max)
    return ''.join(random.choice(chars) for x in range(size))


async def get_new_token(user_id):
    user_id = str(user_id)
    if not await is_user(user_id):
        await create_user(user_id)

    new_token = await randompassword(20, 30)
    hash_token = generate_password_hash(new_token)

    async with Session() as session:
        statement = (
            update(Users)
                .where(Users.user_id == user_id)
                .values(token=hash_token, token_exp=datetime.now())
        )
        await session.execute(statement)
        await session.commit()
        await write_to_log(user_id, f'Обновлен токен для пользователя {user_id}')
    return new_token


async def get_new_pwd(user_id):
    user_id = str(user_id)
    if not await is_user(user_id):
        await create_user(user_id)

    new_pwd = await randompassword(7, 9)
    hash_pwd = generate_password_hash(new_pwd)

    async with Session() as session:
        statement = (
            update(Users)
                .where(Users.user_id == user_id)
                .values(user_pwd=hash_pwd)
        )
        await session.execute(statement)
        await session.commit()
        await write_to_log(user_id, f'Сгенерирован пароль для пользователя {user_id}')
        await get_new_token(user_id)
    return new_pwd


async def load_all_tickers():
    result_list = list()

    async with Session() as session:
        statement = (
            select(StockExchange.ticker_id, StockExchange.ticker_desc)
        )
        result_tmp = await session.execute(statement)

        for ticker_id, ticker_desc in result_tmp:
            result_list.append({'id': ticker_id,
                                'name': ticker_desc})
    return result_list


async def tickers_list_update():
    result = False
    tickers = await get_tickers_list()
    db_tickers = await load_all_tickers()
    db_tickers = {d['id']: d['name'] for d in db_tickers}

    for ticker in tickers.keys():
        if ticker in db_tickers.keys() and db_tickers[ticker] != tickers[ticker]:
            async with Session() as session:
                statement = (
                    update(StockExchange)
                        .where(StockExchange.ticker_id == ticker)
                        .values(ticker_desc=db_ticker)
                )
                await session.execute(statement)
                await session.commit()
                result = True
        elif ticker not in db_tickers.keys():
            async with Session() as session:
                statement = (
                    insert(StockExchange)
                        .values(ticker_id=ticker, ticker_desc=tickers[ticker])
                )
                await session.execute(statement)
                await session.commit()
                result = True
        for db_ticker in db_tickers.keys():
            if db_ticker not in tickers.keys():
                async with Session() as session:
                    statement = (
                        delete(StockExchange)
                            .where(StockExchange.ticker_id == db_ticker)
                    )
                    await session.execute(statement)
                    await session.commit()

        await write_to_log('default', f'Обновлен список тикеров с биржи')
    return result


async def default_user_create():
    result = False
    user_id = 'default'
    if not await is_user(user_id):
        async with Session() as session:
            statement = (
                insert(Users)
                    .values(user_id=user_id, alarm=False)
            )
            await session.execute(statement)

            statement = (
                delete(Tickers)
                    .where(Tickers.user_id == user_id)
            )
            await session.execute(statement)

            for ticker in tickers:
                statement = (
                    insert(Tickers)
                        .values(user_id=user_id, ticker_id=ticker[0], ticker_desc=ticker[1])
                )
                await session.execute(statement)

            await session.commit()
            result = True
            await write_to_log(user_id, f'Создан новый пользователь {user_id}')
    return result

