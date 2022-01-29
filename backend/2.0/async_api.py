import asyncio
import aioredis
from aiohttp import web
from aiohttp_basicauth import BasicAuthMiddleware
import json

from config import redis_connection

import os
import logging
import config
from werkzeug.security import check_password_hash

from async_app_db import load_tickers, add_ticker, remove_ticker, update_ticker, \
                    get_hash_pwd, get_token, get_new_token, load_all_tickers, get_new_pwd

from async_app_ticker import probe_ticker, chart_to_image, export_to_excel, import_from_excel

from async_app_db import default_user_create
from async_app_ticker import ticker_ma_to_db_daemon

from config import redis_connection

class GlobalCache(object):
    def __init__(self, debug=False, db=0):
        self.debug = debug
        try:
            self.cache = aioredis.from_url(f'redis://{redis_connection["host"]}', db=db)
        except (aioredis.exceptions.ConnectionError, aioredis.exceptions.BusyLoadingError):
            if self.debug:
                print(f'redis offline')

    async def set(self, input):
        id, value = input
        id = str(id)
        try:
            await self.cache.set(id, value)
        except (aioredis.exceptions.ConnectionError, aioredis.exceptions.BusyLoadingError):
            if self.debug:
                print(f'redis offline')
            return False
        if self.debug:
            print("add to cache", input)
            print("cache size", await self.cache.dbsize())
        return True

    async def get(self, id):
        id = str(id)
        try:
            result = await self.cache.get(id)
        except (aioredis.exceptions.ConnectionError, aioredis.exceptions.BusyLoadingError):
            if self.debug:
                print(f'redis offline')
            return None
        if self.debug:
            if result is not None:
                print(f'found {result.decode("utf-8")} in cache by id {id}')
                return result.decode('utf-8')
            else:
                print(f'not found in cache by id {id}')
                return None

    async def delete(self, id):
        id = str(id)
        try:
            result = await self.cache.delete(id)
        except (aioredis.exceptions.ConnectionError, aioredis.exceptions.BusyLoadingError):
            if self.debug:
                print(f'redis offline')
            return False
        if result == 1:
            if self.debug:
                print(f'delete from cache by id {id}')
            return True
        else:
            if self.debug:
                print(f'not found in cache by id {id}')
            return False

    async def check(self, input):
        if type(input) is list:
            id, value = input
            try:
                result = await self.cache.get(id)
            except (aioredis.exceptions.ConnectionError, aioredis.exceptions.BusyLoadingError):
                if self.debug:
                    print(f'redis offline')
                return False
            if result is not None:
                if result.decode('utf-8') == value:
                    if self.debug:
                        print("in cache", input)
                    return True
                else:
                    if self.debug:
                        print("not in cache", input)
                    return False
            else:
                if self.debug:
                    print("not in cache", input)
                return False
        else:
            try:
                result = await self.cache.get(input)
            except (aioredis.exceptions.ConnectionError, aioredis.exceptions.BusyLoadingError):
                if self.debug:
                    print(f'redis offline')
            if result is not None:
                if self.debug:
                    print("in cache", input)
                return True
            else:
                if self.debug:
                    print("not in cache", input)
                return False


class CustomBasicAuth(BasicAuthMiddleware):
    async def verify_token(username, password):
        hash = await get_token(username)
        if hash is not None:
            return await check_password_hash(hash, password)
        else:
            return False

    async def verify_password(username, password):
        hash = await get_hash_pwd(username)
        if hash is not None:
            return await check_password_hash(hash, password)
        else:
            return False

    async def check_credentials(self, username, password, request):
        if not (username and password):
            return False
        else:
            if await users_cache.check([username, password]):
                return True
            elif await verify_token(username, password):
                await users_cache.set([username, password])
                return True
            elif await verify_password(username, password):
                await users_cache.set([username, password])
                return True
            else:
                await users_cache.delete(username)
                return False


auth = CustomBasicAuth(force=False)
router = web.RouteTableDef()


async def verify_token(username, password):
    hash = await get_token(username)
    if hash is not None:
        return check_password_hash(hash, password)
    else:
        return False


async def verify_password(username, password):
    hash = await get_hash_pwd(username)
    if hash is not None:
        return check_password_hash(hash, password)
    else:
        return False


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in config.ALLOWED_EXTENSIONS


@router.post("/upload")
@auth.required
async def upload_file(request):
    username = auth.parse_auth_header(request).login
    data = await request.post()
    data_file = data['file'].file
    content = data_file.read()
    with open(os.path.join('./web/static/upload', f'{username}.xlsx'), 'wb') as f:
        f.write(content)
    await import_from_excel(username, os.path.join(config.UPLOAD_FOLDER, f'{username}.xlsx'))
    await tickers_cache.delete(username)
    return web.json_response({ 'success': 'File Uploaded' })


@router.get("/download")
@auth.required
async def download_file(request: web.Request) -> web.Response:
    username = auth.parse_auth_header(request).login
    await export_to_excel(username)
    raise web.HTTPFound(f'/download/{username}.xlsx')


@router.get("/users/")
async def users_get(request: web.Request) -> web.Response:
    username = auth.parse_auth_header(request).login
    password = auth.parse_auth_header(request).password
    if await users_cache.check([username, password]) or await verify_token(username, password):
        return web.json_response({'login': 'ok', 'method': 'token', 'token': f'{password}'})
    else:
        if await verify_password(username, password):
            new_token = await get_new_token(username)
            return web.json_response({'login': 'ok', 'method': 'pwd', 'token': f'{new_token}'})
        else:
            return web.json_response({'login': 'failed'})


@router.get("/tickers/")
async def tickers_get_all(request: web.Request) -> web.Response:
    tickers_json = await tickers_cache.get('all')
    if tickers_json is None:
        tickers = await load_all_tickers()
        tickers_json = json.dumps(tickers)
        await tickers_cache.set(['all', tickers_json])
    else:
        tickers = json.loads(tickers_json)
    if len(tickers) > 0:
        return web.json_response(tickers)
    else:
        return web.json_response({ 'error': 'Data not found' })

@router.get("/tickers/{id}")
@auth.required
async def tickers_get_by_id(request: web.Request) -> web.Response:
    id = request.match_info["id"]
    tickers_json = await tickers_cache.get(id)
    if tickers_json is None:
        tickers = await load_tickers(id)
        tickers_json = json.dumps(tickers)
        await tickers_cache.set([id, tickers_json])
    else:
        tickers = json.loads(tickers_json)
    if len(tickers) > 0:
        return web.json_response(tickers)
    else:
        return web.json_response({'error': 'Data not found'})


@router.post("/tickers/{id}")
@auth.required
async def tickers_post_by_id(request: web.Request) -> web.Response:
    id = request.match_info["id"]
    json_request = await request.json()
    ticker = json_request["ticker"]
    description = json_request["description"]
    if description == '':
        description = ticker
    tickers_json = await tickers_cache.get(id)
    if tickers_json is None:
        tickers = await load_tickers(id)
        tickers_json = json.dumps(tickers)
        await tickers_cache.set([id, tickers_json])
    else:
        tickers = json.loads(tickers_json)
    for t in tickers:
        if (t['id'] == ticker):
            return web.json_response({ 'error': 'Ticker already exists' })
    if not await probe_ticker(ticker):
        return web.json_response({ 'error': 'Ticker not found in stock exchange' })
    await add_ticker(ticker, description, id)
    await tickers_cache.delete(id)
    return web.json_response({ 'success': 'Ticker added' })


@router.delete("/tickers/{id}")
@auth.required
async def tickers_delete_by_id(request: web.Request) -> web.Response:
    id = request.match_info["id"]
    ticker = request.query["ticker"]
    tickers_json = await tickers_cache.get(id)
    if tickers_json is None:
        tickers = await load_tickers(id)
        tickers_json = json.dumps(tickers)
        await tickers_cache.set([id, tickers_json])
    else:
        tickers = json.loads(tickers_json)
    for t in tickers:
        if (t['id'] == ticker):
            await remove_ticker(ticker, id)
            await tickers_cache.delete(id)
            return web.json_response({'success': f'Ticker {ticker} of user {id} deleted'})
    return web.json_response({ 'error': 'Ticker to delete not found' })


@router.put("/tickers/{id}")
@auth.required
async def tickers_put_by_id(request: web.Request) -> web.Response:
    id = request.match_info["id"]
    ticker = request.query["ticker"]
    description = request.query["description"]
    if description == '':
        description = ticker
    tickers_json = await tickers_cache.get(id)
    if tickers_json is None:
        tickers = await load_tickers(id)
        tickers_json = json.dumps(tickers)
        await tickers_cache.set([id, tickers_json])
    else:
        tickers = json.loads(tickers_json)
    for t in tickers:
        if (t['id'] == ticker):
            await update_ticker(ticker, description, id)
            await tickers_cache.delete(id)
            return web.json_response({'success': f"Description of Ticker {ticker} changed"})
    return web.json_response({'error': 'Ticker for this user not found'})


@router.get("/ticker/{id}")
@auth.required
async def chart_get_by_id(request: web.Request) -> web.Response:
    ticker = request.match_info["id"]
    if await chart_to_image(ticker):
        img_url = f"/charts/{ticker}.png"
        return web.json_response({ 'url': img_url })
    else:
        return web.json_response({ 'error': 'Data not found' })


async def root_handler(request):
    return web.HTTPFound('/index.html')


async def on_startup(app):
    await default_user_create()
    asyncio.create_task(ticker_ma_to_db_daemon())
    await users_cache.cache.flushdb()

async def init_app() -> web.Application:
    app = web.Application(middlewares=[auth], client_max_size=1024**3)
    app.add_routes(router)
    app.router.add_route('*', '/', root_handler)
    app.router.add_static('/', './web/static')
    app.on_startup.append(on_startup)
    logging.basicConfig(level=logging.DEBUG)
    return app

users_cache = GlobalCache(db=0, debug=False)
tickers_cache = GlobalCache(db=1, debug=False)

def api_daemon():
    web.run_app(init_app(), port=5000)

if __name__ == '__main__':
    web.run_app(init_app(), port=5000)