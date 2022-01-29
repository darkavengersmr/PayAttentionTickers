#!/usr/bin/python3

import unittest

import app_db, app_ticker

TESTUSER = '733832502'


class TestAppDB(unittest.TestCase):
    def test_tickers_list_update(self):
        self.assertTrue(app_db.tickers_list_update())

    def test_randompassword(self):
        self.assertTrue(len(app_db.randompassword(6, 8)) > 5)
        self.assertFalse(len(app_db.randompassword(5, 5)) == 4)

    def test_get_hash_pwd(self):
        self.assertTrue(len(app_db.get_hash_pwd(TESTUSER)) > 20)
        self.assertFalse(app_db.get_hash_pwd('unknown') is not None)

    def test_get_token(self):
        self.assertTrue(len(app_db.get_token(TESTUSER)) > 20)
        self.assertFalse(app_db.get_token('unknown') is not None)

    def test_get_new_pwd(self):
        self.assertTrue(len(app_db.get_new_pwd('default')) > 5)
        self.assertFalse(app_db.get_new_pwd('unknown') is not None)

    def test_get_new_token(self):
        self.assertTrue(len(app_db.get_new_token(TESTUSER)) > 20)
        self.assertFalse(app_db.get_new_token('unknown') is not None)

    def test_is_user(self):
        self.assertTrue(app_db.is_user(TESTUSER))
        self.assertFalse(app_db.is_user('unknown'))

    def test_load_tickers(self):
        self.assertTrue(len(app_db.load_tickers('default')) > 5)
        self.assertFalse(len(app_db.load_tickers('unknown')) == 0)

    def test_get_all_tickers(self):
        self.assertTrue(len(app_db.get_all_tickers()) > 5)
        self.assertTrue('BABA' in app_db.get_all_tickers())
        self.assertFalse('BAB2' in app_db.get_all_tickers())

    def test_write_to_log(self):
        self.assertTrue(app_db.write_to_log('default', 'Проведен unittest'))

    def test_remove_create_user(self):
        self.assertTrue(app_db.create_user('unittest'))
        self.assertTrue(app_db.remove_user('unittest'))

    def test_add_update_remove_ticker(self):
        self.assertTrue(app_db.add_ticker('GE', 'Unittest ticker added', TESTUSER))
        self.assertTrue(app_db.update_ticker('GE', 'Unittest ticker updated', TESTUSER))
        self.assertTrue(app_db.remove_ticker('GE', TESTUSER))


class TestAppTicker(unittest.TestCase):

    def test_get_tickers_list(self):
        self.assertTrue(len(app_ticker.get_tickers_list()) > 100)

    def test_get_exist_ticker(self):
        self.assertTrue(app_ticker.exist_ticker('BABA', 'default'))
        self.assertFalse(app_ticker.exist_ticker('BABA2', 'default'))

    def test_probe_ticker(self):
        self.assertTrue(app_ticker.probe_ticker('BABA'))
        self.assertFalse(app_ticker.probe_ticker('BABA2'))

    def test_ticker_ma_to_db(self):
        self.assertTrue(app_ticker.ticker_ma_to_db() > 5)

if __name__ == '__main__':
    unittest.main()