#!/usr/bin/python3

import datetime
import string
import random
from werkzeug.security import generate_password_hash
import psycopg2

import config
from app_ticker import get_tickers_list, ticker_price_to_ma

def tickers_list_update():
    result = False
    tickers = get_tickers_list()
    db_connection = psycopg2.connect(user=config.db_connection['user'],
                                     password=config.db_connection['password'],
                                     host=config.db_connection['host'],
                                     port=config.db_connection['port'],
                                     database=config.db_connection['database'])
    with db_connection:
        with db_connection.cursor() as cursor:
            for ticker in tickers.keys():
                cursor.execute("SELECT ticker_id FROM stock_exchange WHERE ticker_id = %s", (ticker,))
                exist_ticker = cursor.fetchone()
                if exist_ticker is None:
                    cursor.execute("INSERT INTO stock_exchange(ticker_id, ticker_desc) VALUES(%s, %s)",
                                   (ticker, tickers[ticker]))
            result = True
    if result:
        db_connection.close()
        user_id = 'default'
        write_to_log(user_id, f'Обновлен список тикетов с биржи')
    return result


def load_all_tickers():
    result_list = list()
    db_connection = psycopg2.connect(user=config.db_connection['user'],
                                     password=config.db_connection['password'],
                                     host=config.db_connection['host'],
                                     port=config.db_connection['port'],
                                     database=config.db_connection['database'])
    with db_connection:
        with db_connection.cursor() as cursor:
            cursor.execute("SELECT ticker_id, ticker_desc FROM stock_exchange")
            result_tmp = cursor.fetchall()
    for ticker_id, ticker_desc in result_tmp:
        result_list.append({ 'id': ticker_id,
                             'name': ticker_desc })
    db_connection.close()
    return result_list


def randompassword(min, max):
    chars = string.ascii_uppercase + string.ascii_lowercase + string.digits
    size = random.randint(min, max)
    return ''.join(random.choice(chars) for x in range(size))


def get_new_pwd(user_id):
    user_id = str(user_id)
    if not is_user(user_id):
        create_user(user_id)
    if is_user(user_id):
        new_pwd = randompassword(7, 9)
        hash_pwd = generate_password_hash(new_pwd)
        db_connection = psycopg2.connect(user=config.db_connection['user'],
                                         password=config.db_connection['password'],
                                         host=config.db_connection['host'],
                                         port=config.db_connection['port'],
                                         database=config.db_connection['database'])
        with db_connection:
            with db_connection.cursor() as cursor:
                cursor.execute("UPDATE users SET user_pwd = %s WHERE user_id = %s", (hash_pwd, user_id))
        db_connection.close()
        write_to_log(user_id, f'Сгенерирован пароль для пользователя {user_id}')
        get_new_token(user_id)
        return new_pwd
    else:
        return None


def get_new_token(user_id):
    user_id = str(user_id)
    if not is_user(user_id):
        create_user(user_id)
    if is_user(user_id):
        new_token = randompassword(20, 30)
        hash_token = generate_password_hash(new_token)
        db_connection = psycopg2.connect(user=config.db_connection['user'],
                                         password=config.db_connection['password'],
                                         host=config.db_connection['host'],
                                         port=config.db_connection['port'],
                                         database=config.db_connection['database'])
        with db_connection:
            with db_connection.cursor() as cursor:
                cursor.execute("UPDATE users SET token = %s, token_exp = %s WHERE user_id = %s",
                                (hash_token, datetime.datetime.now(), user_id))
        db_connection.close()
        write_to_log(user_id, f'Обновлен токен для пользователя {user_id}')
        return new_token
    else:
        return None


def get_hash_pwd(user_id):
    user_id = str(user_id)
    pwd = None
    db_connection = psycopg2.connect(user=config.db_connection['user'],
                                     password=config.db_connection['password'],
                                     host=config.db_connection['host'],
                                     port=config.db_connection['port'],
                                     database=config.db_connection['database'])
    with db_connection:
        with db_connection.cursor() as cursor:
            cursor.execute("SELECT user_pwd FROM users WHERE user_id = %s", (user_id,))
            pwd = cursor.fetchone()
    db_connection.close()
    if pwd is not None:
        return pwd[0]
    else:
        return None


def get_token(user_id):
    user_id = str(user_id)
    token = None
    db_connection = psycopg2.connect(user=config.db_connection['user'],
                                     password=config.db_connection['password'],
                                     host=config.db_connection['host'],
                                     port=config.db_connection['port'],
                                     database=config.db_connection['database'])
    with db_connection:
        with db_connection.cursor() as cursor:
            cursor.execute("SELECT token FROM users WHERE user_id = %s AND token_exp > %s - interval '30 days'",
                           (user_id, datetime.datetime.now()))
            token = cursor.fetchone()
    db_connection.close()
    if token is not None:
        return token[0]
    else:
        return None


def write_to_log(user_id, message):
    result = False
    user_id = str(user_id)
    if not is_user(user_id):
        create_user(user_id)
    db_connection = psycopg2.connect(user=config.db_connection['user'],
                                     password=config.db_connection['password'],
                                     host=config.db_connection['host'],
                                     port=config.db_connection['port'],
                                     database=config.db_connection['database'])
    with db_connection:
        with db_connection.cursor() as cursor:
            cursor.execute("INSERT INTO logs(date, user_id, message) VALUES(%s, %s, %s)", (datetime.datetime.now(),
                                                                                           user_id, message))
            result = True
    if result:
        db_connection.close()
    return result

def is_user(user_id):
    user_id = str(user_id)
    db_connection = psycopg2.connect(user=config.db_connection['user'],
                                     password=config.db_connection['password'],
                                     host=config.db_connection['host'],
                                     port=config.db_connection['port'],
                                     database=config.db_connection['database'])
    with db_connection:
        with db_connection.cursor() as cursor:
            cursor.execute("SELECT user_id FROM users WHERE user_id = %s", (user_id,))
            record = cursor.fetchone()
    db_connection.close()
    if record is not None:
        return True
    else:
        return False


def default_user_create():
    result = False
    user_id = 'default'
    if not is_user(user_id):
        db_connection = psycopg2.connect(user=config.db_connection['user'],
                                         password=config.db_connection['password'],
                                         host=config.db_connection['host'],
                                         port=config.db_connection['port'],
                                         database=config.db_connection['database'])
        with db_connection:
            with db_connection.cursor() as cursor:
                cursor.execute("INSERT INTO users(user_id, alarm) VALUES(%s, %s)", (user_id, 'False'))
                cursor.execute("DELETE FROM tickers WHERE user_id = %s", (user_id,))
                for ticker in config.tickers:
                    cursor.execute("INSERT INTO tickers(user_id, ticker_id, ticker_desc) VALUES(%s, %s, %s)",
                                   (user_id, *ticker))
                result = True
    if result:
        db_connection.close()
        write_to_log(user_id, f'Создан новый пользователь {user_id}')
    return result


def create_user(user_id):
    result = False
    user_id = str(user_id)

    if not is_user(user_id) and user_id != 'unknown':
        db_connection = psycopg2.connect(user=config.db_connection['user'],
                                         password=config.db_connection['password'],
                                         host=config.db_connection['host'],
                                         port=config.db_connection['port'],
                                         database=config.db_connection['database'])
        with db_connection:
            with db_connection.cursor() as cursor:
                cursor.execute("INSERT INTO users(user_id, alarm) VALUES(%s, %s)", (user_id, 'False'))
                cursor.execute("DELETE FROM tickers WHERE user_id = %s", (user_id,))
                for ticker in config.tickers:
                    deviat_month, deviat_week = ticker_price_to_ma(ticker[0])
                    if deviat_month == 'error': deviat_month = 0
                    if deviat_week == 'error': deviat_week = 0
                    cursor.execute("INSERT INTO tickers(user_id, ticker_id, ticker_desc, deviat_month, deviat_week) "
                                   "VALUES(%s, %s, %s, %s, %s)", (user_id, *ticker, deviat_month, deviat_week))
                result = True
    if result:
        db_connection.close()
        write_to_log(user_id, f'Создан новый пользователь {user_id}')
    return result


def remove_user(user_id):
    result = False
    user_id = str(user_id)

    if is_user(user_id):
        db_connection = psycopg2.connect(user=config.db_connection['user'],
                                         password=config.db_connection['password'],
                                         host=config.db_connection['host'],
                                         port=config.db_connection['port'],
                                         database=config.db_connection['database'])
        with db_connection:
            with db_connection.cursor() as cursor:
                cursor.execute("DELETE FROM users WHERE user_id = %s", (user_id,))
                result = True
    if result:
        db_connection.close()
        #write_to_log(user_id, f'Пользователь {user_id} удален')
    return result


def load_tickers(user_id):
    user_id = str(user_id)
    result_list = list()
    if not is_user(user_id):
        user_id = 'default'
    db_connection = psycopg2.connect(user=config.db_connection['user'],
                                     password=config.db_connection['password'],
                                     host=config.db_connection['host'],
                                     port=config.db_connection['port'],
                                     database=config.db_connection['database'])
    with db_connection:
        with db_connection.cursor() as cursor:
            cursor.execute("SELECT ticker_id, ticker_desc, deviat_month, deviat_week, update_date FROM tickers WHERE user_id = %s", (user_id,))
            result_tmp = cursor.fetchall()
    for ticker_id, ticker_desc, deviat_month, deviat_week, update_date in result_tmp:
        result_list.append({ 'id': ticker_id,
                             'name': ticker_desc,
                             'deviat_month': deviat_month,
                             'deviat_week': deviat_week,
                             'update_date': str(update_date).split(" ")[0] })
    db_connection.close()
    return result_list


def get_all_tickers():
    tmp_list = list()
    db_connection = psycopg2.connect(user=config.db_connection['user'],
                                     password=config.db_connection['password'],
                                     host=config.db_connection['host'],
                                     port=config.db_connection['port'],
                                     database=config.db_connection['database'])
    with db_connection:
        with db_connection.cursor() as cursor:
            cursor.execute("SELECT ticker_id FROM tickers GROUP BY ticker_id")
            tmp_list = cursor.fetchall()
    result_list = [a[0] for a in tmp_list]
    db_connection.close()
    return result_list


def set_ticker_ma(ticker_id, ticker_ma20, ticker_ma5):
    db_connection = psycopg2.connect(user=config.db_connection['user'],
                                     password=config.db_connection['password'],
                                     host=config.db_connection['host'],
                                     port=config.db_connection['port'],
                                     database=config.db_connection['database'])
    with db_connection:
        with db_connection.cursor() as cursor:
            cursor.execute("UPDATE tickers SET deviat_month = %s, deviat_week = %s, update_date = %s WHERE ticker_id = %s",
                           (ticker_ma20, ticker_ma5, datetime.datetime.now(), ticker_id))
    db_connection.close()
    return True


def add_ticker(ticker, description, user_id):
    result = False
    user_id = str(user_id)
    if not is_user(user_id):
        create_user(user_id)
    deviat_month, deviat_week = ticker_price_to_ma(ticker)
    db_connection = psycopg2.connect(user=config.db_connection['user'],
                                     password=config.db_connection['password'],
                                     host=config.db_connection['host'],
                                     port=config.db_connection['port'],
                                     database=config.db_connection['database'])
    with db_connection:
        with db_connection.cursor() as cursor:
            cursor.execute("INSERT INTO tickers(user_id, ticker_id, ticker_desc, deviat_month, deviat_week, update_date) "  
                           "VALUES(%s, %s, %s, %s, %s, %s)", (user_id, ticker, description, deviat_month, deviat_week, datetime.datetime.now()))
            result = True
    if result:
        db_connection.close()
        write_to_log(user_id, f'Пользователь {user_id} добавил новый тикет {ticker} с описанием {description}')
    return result


def update_ticker(ticker, description, user_id):
    result = False
    user_id = str(user_id)
    if not is_user(user_id):
        create_user(user_id)
    db_connection = psycopg2.connect(user=config.db_connection['user'],
                                     password=config.db_connection['password'],
                                     host=config.db_connection['host'],
                                     port=config.db_connection['port'],
                                     database=config.db_connection['database'])
    with db_connection:
        with db_connection.cursor() as cursor:
            cursor.execute("UPDATE tickers SET ticker_desc = %s WHERE user_id = %s AND ticker_id = %s",
                           (description, user_id, ticker))
            result = True
    if result:
        db_connection.close()
        write_to_log(user_id, f'Пользователь {user_id} изменил описание тикета {ticker} на {description}')
    return result


def remove_ticker(ticker_to_remove, user_id):
    result = False
    user_id = str(user_id)
    if not is_user(user_id):
        create_user(user_id)
    db_connection = psycopg2.connect(user=config.db_connection['user'],
                                     password=config.db_connection['password'],
                                     host=config.db_connection['host'],
                                     port=config.db_connection['port'],
                                     database=config.db_connection['database'])
    with db_connection:
        with db_connection.cursor() as cursor:
            cursor.execute("DELETE FROM tickers WHERE user_id = %s AND ticker_id = %s", (user_id, ticker_to_remove))
            result = True
    if result:
        db_connection.close()
        write_to_log(user_id, f'Пользователь {user_id} удалил тикет {ticker_to_remove}')
    return result


def is_subscribe(user_id):
    user_id = str(user_id)
    result = None
    db_connection = psycopg2.connect(user=config.db_connection['user'],
                                     password=config.db_connection['password'],
                                     host=config.db_connection['host'],
                                     port=config.db_connection['port'],
                                     database=config.db_connection['database'])
    with db_connection:
        with db_connection.cursor() as cursor:
            cursor.execute("SELECT alarm FROM users WHERE user_id = %s", (user_id,))
            result = cursor.fetchone()
    db_connection.close()
    if result is not None:
        return bool(result[0])
    else:
        return False


def subscribe_add_remove(user_id):
    user_id = str(user_id)
    if not is_user(user_id):
        create_user(user_id)
    db_connection = psycopg2.connect(user=config.db_connection['user'],
                                     password=config.db_connection['password'],
                                     host=config.db_connection['host'],
                                     port=config.db_connection['port'],
                                     database=config.db_connection['database'])
    with db_connection:
        with db_connection.cursor() as cursor:
            cursor.execute("UPDATE users SET alarm = NOT alarm WHERE user_id = %s", (user_id,))
    db_connection.close()
    write_to_log(user_id, f'Пользователь {user_id} изменил статус своей подписки на {is_subscribe(user_id)}')


def subscribers_list():
    result = list()
    db_connection = psycopg2.connect(user=config.db_connection['user'],
                                     password=config.db_connection['password'],
                                     host=config.db_connection['host'],
                                     port=config.db_connection['port'],
                                     database=config.db_connection['database'])
    with db_connection:
        with db_connection.cursor() as cursor:
            cursor.execute("SELECT user_id FROM users WHERE user_id != 'default' AND alarm = true")
            result = [a[0] for a in cursor.fetchall()]
    db_connection.close()
    return result


def get_status():
    result = ""
    db_connection = psycopg2.connect(user=config.db_connection['user'],
                                     password=config.db_connection['password'],
                                     host=config.db_connection['host'],
                                     port=config.db_connection['port'],
                                     database=config.db_connection['database'])
    with db_connection:
        with db_connection.cursor() as cursor:
            cursor.execute("SELECT COUNT(user_id)-1 FROM users")
            result = "Всего пользователей: " + str(cursor.fetchone()[0])
    db_connection.close()
    return result


def get_all_users():
    tmp_list = list()
    db_connection = psycopg2.connect(user=config.db_connection['user'],
                                     password=config.db_connection['password'],
                                     host=config.db_connection['host'],
                                     port=config.db_connection['port'],
                                     database=config.db_connection['database'])
    with db_connection:
        with db_connection.cursor() as cursor:
            cursor.execute("SELECT user_id FROM users")
            tmp_list = cursor.fetchall()
    result_list = [a[0] for a in tmp_list]
    db_connection.close()
    return result_list