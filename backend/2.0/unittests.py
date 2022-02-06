#!/usr/bin/python3

import asyncio

import aiounittest

import async_app_db, async_app_ticker

TESTUSER = 'default'


class TestAppDB(aiounittest.AsyncTestCase):
    async def test_tickers_list_update(self):
        self.assertTrue(await async_app_db.tickers_list_update())

    async def test_randompassword(self):
        self.assertTrue(len(await async_app_db.randompassword(6, 8)) > 5)
        self.assertFalse(len(await async_app_db.randompassword(5, 5)) == 4)

    async def test_get_hash_pwd(self):
        self.assertTrue(len(await async_app_db.get_hash_pwd(TESTUSER)) > 20)
        self.assertFalse(await async_app_db.get_hash_pwd('unknown') is not None)

    async def test_get_token(self):
        self.assertTrue(len(await async_app_db.get_token(TESTUSER)) > 20)
        self.assertFalse(await async_app_db.get_token('unknown') is not None)

    async def test_get_new_pwd(self):
        self.assertTrue(len(await async_app_db.get_new_pwd('default')) > 5)

    async def test_get_new_token(self):
        self.assertTrue(len(await async_app_db.get_new_token(TESTUSER)) > 20)

    async def test_is_user(self):
        self.assertTrue(await async_app_db.is_user(TESTUSER))
        self.assertFalse(await async_app_db.is_user('unknown'))

    async def test_load_tickers(self):
        self.assertTrue(len(await async_app_db.load_tickers('default')) > 5)
        self.assertFalse(len(await async_app_db.load_tickers('unknown')) == 0)

    async def test_get_all_tickers(self):
        self.assertTrue(len(await async_app_db.get_all_tickers()) > 5)
        self.assertTrue('BABA' in await async_app_db.get_all_tickers())
        self.assertFalse('BAB2' in await async_app_db.get_all_tickers())

    async def test_load_tickers(self):
        self.assertTrue(len(await async_app_db.load_tickers('default')) > 5)
        self.assertFalse(len(await async_app_db.load_tickers('unknown')) == 0)

    async def test_get_all_tickers(self):
        self.assertTrue(len(await async_app_db.get_all_tickers()) > 5)
        self.assertTrue('BABA' in await async_app_db.get_all_tickers())
        self.assertFalse('BAB2' in await async_app_db.get_all_tickers())

    async def test_write_to_log(self):
        self.assertTrue(await async_app_db.write_to_log('default', 'Проведен unittest'))

    async def test_remove_create_user(self):
        if (not await async_app_db.is_user('unittest')):
            self.assertTrue(await async_app_db.create_user('unittest'))
        self.assertTrue(await async_app_db.remove_user('unittest'))

    async def test_add_update_remove_ticker(self):
        self.assertTrue(await async_app_db.add_ticker('GE', 'Unittest ticker added', TESTUSER))
        self.assertTrue(await async_app_db.update_ticker('GE', 'Unittest ticker updated', TESTUSER))
        self.assertTrue(await async_app_db.remove_ticker('GE', TESTUSER))

    def get_event_loop(self):
        self.my_loop = asyncio.get_event_loop()
        return self.my_loop


class TestAppTicker(aiounittest.AsyncTestCase):

    async def test_get_tickers_list(self):
        self.assertTrue(len(await async_app_ticker.get_tickers_list()) > 100)

    async def test_get_exist_ticker(self):
        self.assertTrue(await async_app_ticker.exist_ticker('BABA', 'default'))
        self.assertFalse(await async_app_ticker.exist_ticker('BABA2', 'default'))

    async def test_probe_ticker(self):
        self.assertTrue(await async_app_ticker.probe_ticker('BABA'))
        self.assertFalse(await async_app_ticker.probe_ticker('BABA2'))

    async def test_ticker_ma_to_db(self):
        self.assertTrue(await async_app_ticker.ticker_ma_to_db() > 5)

    def get_event_loop(self):
        self.my_loop = asyncio.get_event_loop()
        return self.my_loop







