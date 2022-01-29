#!/usr/bin/python3

import os

from flask import Flask, flash, request, redirect, send_file
from flask_restful import Api, Resource, reqparse
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import check_password_hash
from werkzeug.utils import secure_filename

from app_db import load_tickers, add_ticker, remove_ticker, update_ticker, \
                    get_hash_pwd, get_token, get_new_token, load_all_tickers

from app_ticker import probe_ticker, chart_to_image, import_from_excel, export_to_excel

import config

app = Flask(__name__,
            static_url_path='',
            static_folder='web/static',
            template_folder='web/templates')

app.config['CORS_HEADERS'] = 'Content-Type'
api = Api(app)
auth = HTTPBasicAuth()


class GlobalCache(object):
    def __init__(self, size, debug=False):
        self.cache = []
        self.size = size
        self.debug = debug

    def check_by_all(self, input):
        if input in self.cache:
            if self.debug: print("in cache", input)
            return True
        else:
            if self.debug: print("not in cache", input)
            return False

    def check_by_id(self, id):
        id = str(id)
        if id in [a[0] for a in self.cache]:
            if self.debug: print("in cache", id)
            return True
        else:
            if self.debug: print("not in cache by id", id)
            return False

    def get_by_id(self, id):
        id = str(id)
        if id in [a[0] for a in self.cache]:
            for el in self.cache:
                if el[0] == id:
                    if self.debug: print("found in cache by id", id)
                    return el[1]

    def add(self, input):
        id, value = input
        id = str(id)
        self.cache.append([id, value])
        self.resize_to_cachesize()
        if self.debug:
            print("add to cache", self.cache)
            print("cache size", len(self.cache))

    def remove(self, id):
        id = str(id)
        if id in [a[0] for a in self.cache]:
            for el in self.cache:
                if el[0] == id:
                    if self.debug: print("remove from cache by id", id)
                    self.cache.remove(el)

    def resize_to_cachesize(self):
        if len(self.cache) > self.size:
            if self.debug: print("remove from cache by cache resize to limit", self.size)
            self.cache.remove(self.cache[0])


def verify_token(username, password):
    hash = get_token(username)
    if hash is not None:
        return check_password_hash(hash, password)
    else:
        return False


def verify_password(username, password):
    hash = get_hash_pwd(username)
    if hash is not None:
        return check_password_hash(hash, password)
    else:
        return False


@auth.verify_password
def verify(username, password):
    if not (username and password):
        return False
    else:
        if users_cache.check_by_all([username, password]):
            return True
        elif verify_token(username, password):
            users_cache.add([username, password])
            return True
        elif verify_password(username, password):
            users_cache.add([username, password])
            return True
        else:
            users_cache.remove(username)
            return False


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in config.ALLOWED_EXTENSIONS

@auth.login_required
@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    myauth = dict(auth.get_auth())
    username = myauth['username']
    if request.method == 'POST':
        # проверим, передается ли в запросе файл
        if 'file' not in request.files:
            # После перенаправления на страницу загрузки
            # покажем сообщение пользователю
            flash('Не могу прочитать файл')
            return "{ error: 'File Uploaded error' }", 500
        file = request.files['file']
        # Если файл не выбран, то браузер может
        # отправить пустой файл без имени.
        if file.filename == '':
            flash('Нет выбранного файла')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            # безопасно извлекаем оригинальное имя файла
            filename = secure_filename(file.filename)
            # сохраняем файл
            file.save(os.path.join(config.UPLOAD_FOLDER, filename))
            import_from_excel(username, os.path.join(config.UPLOAD_FOLDER, filename))
            tickers_cache.remove(username)
            return "{ success: 'File Uploaded' }", 200
    return "{ error: 'File Uploaded error' }", 500


@auth.login_required
@app.route('/download', methods=['GET', 'POST'])
def download_file():
    myauth = dict(auth.get_auth())
    username = myauth['username']
    export_to_excel(username)
    return send_file(f'{config.FILEPATHS["download"]}{config.SYSTEM_SLASH}{username}.xlsx', as_attachment=True,
                     mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                     attachment_filename=f"{username}.xlsx")


class TickersApi(Resource):

    @auth.login_required
    def get(self, id=''):
        if len(str(id)) > 1:
            if tickers_cache.check_by_id(id):
                tickers = tickers_cache.get_by_id(id)
            else:
                tickers = load_tickers(id)
                tickers_cache.add([id, tickers])
        else:
            if tickers_cache.check_by_id('all'):
                tickers = tickers_cache.get_by_id('all')
            else:
                tickers = load_all_tickers()
                tickers_cache.add(['all', tickers])
        if len(tickers) > 0:
            return tickers, 200
        else:
            return "{ error: 'Data not found'' }", 404

    # добавление новой записи
    @auth.login_required
    def post(self, id):
        parser = reqparse.RequestParser()
        parser.add_argument("ticker")
        parser.add_argument("description")
        params = parser.parse_args()
        new_ticker = params["ticker"]
        if params["description"] == '':
            params["description"] = params["ticker"]
        if tickers_cache.check_by_id(id):
            tickers = tickers_cache.get_by_id(id)
        else:
            tickers = load_tickers(id)
        for t in tickers:
            if (t['id'] == new_ticker):
                return "{ error: 'Ticker already exists' }", 400
        if not probe_ticker(params["ticker"]):
            return "{ error: 'Ticker not found in stock exchange' }", 400
        add_ticker(new_ticker, params["description"], id)
        tickers_cache.remove(id)
        return "{ success: 'Ticker added' }", 200

    # изменение существующей записи
    @auth.login_required
    def put(self, id):
        parser = reqparse.RequestParser()
        parser.add_argument("ticker")
        parser.add_argument("description")
        params = parser.parse_args()
        new_ticker = params["ticker"]
        if params["description"] == '':
            params["description"] = params["ticker"]
        if tickers_cache.check_by_id(id):
            tickers = tickers_cache.get_by_id(id)
        else:
            tickers = load_tickers(id)
        for t in tickers:
            if (t['id'] == new_ticker):
                update_ticker(new_ticker, params["description"], id)
                tickers_cache.remove(id)
                return f"Description of Ticker {new_ticker} changed", 201
        return "{ error: 'Ticker for this user not found' }", 400

    # удаление записи
    @auth.login_required
    def delete(self, id):
        parser = reqparse.RequestParser()
        parser.add_argument("ticker")
        params = parser.parse_args()
        del_ticker = params["ticker"]
        tickers = load_tickers(id)
        for t in tickers:
            if (t['id'] == del_ticker):
                remove_ticker(del_ticker, id)
                tickers_cache.remove(id)
                return f"Ticker {del_ticker} of user {id} deleted", 200
        return "{ error: 'Ticker to delete not found' }", 400


class TickerApi(Resource):
    # чтение записи
    @auth.login_required
    def get(self, ticker='default'):
        if chart_to_image(ticker):
            img_url = f"/charts/{ticker}.png"
            return { 'url': img_url }, 200
        else:
            return "{ error: 'Data not found' }", 404


class UserApi(Resource):
    def get(self, id='default'):
        myauth = dict(auth.get_auth())
        username = myauth['username']
        password = myauth['password']
        if users_cache.check_by_all([username, password]):
            return {'login': 'ok', 'method': 'token', 'token': f'{password}'}, 200
        elif verify_token(username, password):
            return {'login': 'ok', 'method': 'token', 'token': f'{password}'}, 200
        else:
            if verify_password(username, password):
                return {'login': 'ok', 'method': 'pwd', 'token': f'{get_new_token(username)}'}, 200
            else:
                return {'login': 'failed'}, 401


api.add_resource(TickersApi, "/tickers", "/tickers/", "/tickers/<int:id>")
api.add_resource(TickerApi, "/ticker", "/ticker/", "/ticker/<string:ticker>")
api.add_resource(UserApi, "/users", "/users/", "/users/<int:id>")

users_cache = GlobalCache(64, debug=False)
tickers_cache = GlobalCache(64, debug=False)

@app.route('/')
def hello():
    return redirect("index.html", code=302)

def api_daemon():
    app.config['UPLOAD_FOLDER'] = config.UPLOAD_FOLDER
    app.run(host='0.0.0.0', debug=True)

if __name__ == '__main__':
    app.config['UPLOAD_FOLDER'] = config.UPLOAD_FOLDER
    app.run(host='0.0.0.0', debug=True)
