#!/usr/bin/python3

from datetime import datetime

from sqlalchemy.orm import declarative_base, sessionmaker, relationship, backref

# создаем метод описания БД (Создаем базовый класс для декларативных определений классов.)
Base = declarative_base()

# импортируем ORM для работы с БД
from sqlalchemy import (
    Boolean,
    Column,
    String,
    Integer,
    DateTime,
    Text,
    Float,
    ForeignKey,
    func
)

class Users(Base):
    __tablename__ = 'users'

    user_id = Column(String(32), unique=True, primary_key=True)
    alarm = Column(Boolean, nullable=False, default=False)
    alarm_limit = Column(Integer, default=0)
    user_pwd = Column(Text, default='', server_default='')
    token = Column(Text, default='', server_default='')
    token_exp = Column(DateTime)

    #tickers = relationship('Tickers', backref='ticker_user', passive_deletes=True)

    def __repr__(self):
        return f'{self.user_id} {self.alarm} {self.alarm_limit} {self.user_pwd} ' \
               f'{self.token} {self.token_exp}'


class Tickers(Base):
    __tablename__ = 'tickers'

    key_id = Column(Integer, unique=True, primary_key=True, autoincrement=True)
    user_id = Column(String(32), ForeignKey('users.user_id', ondelete='CASCADE'))
    ticker_id = Column(String(32), nullable=False)
    ticker_desc = Column(Text)
    deviat_month = Column(Float)
    deviat_week = Column(Float)
    update_date = Column(DateTime)

    #users = relationship('Users', backref='ticker_user', lazy='subquery')
    users = relationship('Users', backref=backref('ticker_user', passive_deletes=True))


    def __repr__(self):
        return f'{self.key_id} {self.user_id} {self.ticker_id} {self.ticker_desc} ' \
               f'{self.deviat_month} {self.deviat_week} {self.update_date}'

class Logs(Base):
    __tablename__ = 'logs'

    log_id = Column(Integer, unique=True, primary_key=True, autoincrement=True)
    date = Column(DateTime, nullable=False, default=datetime.utcnow, server_default=func.now())
    user_id = Column(String(32), ForeignKey('users.user_id'))
    message = Column(Text, nullable=False, default='', server_default='')

    users = relationship('Users', backref='log_user', lazy='subquery')

    def __repr__(self):
        return f'{self.log_id} {self.date} {self.user_id} {self.message}'

class StockExchange(Base):
    __tablename__ = 'stock_exchange'

    ticker_id = Column(String(32), nullable=False, unique=True, primary_key=True)
    ticker_desc = Column(Text)

    def __repr__(self):
        return f'{self.ticker_id} {self.ticker_desc}'