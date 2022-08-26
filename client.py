from aiohttp import web
import logging
from aiohttp import web


async def hello(request: web.Request):
    print(request.headers)
    return web.Response(status=200, headers={'Access-Control-Allow-Origin': '*',
                                             'Access-Control-Allow-Methods': 'POST, GET, OPTIONS',
                                             'Access-Control-Allow-Headers': 'Content-Type'})
    # return web.Response(text="Hello, world")


async def test(request: web.Request):
    data = await request.json()
    print(data)
    return web.Response(status=200, text='asd', headers={'Host': '192.168.43.172:7777',
                                                         'Connection': 'keep-alive',
                                                         'Content-Length': '20', '3': '1',
                                                         'Content-Type': 'application/json; charset=utf-8',
                                                         'Accept': '*/*',
                                                         'Access-Control-Allow-Origin': 'http://localhost:50887'})


logging.basicConfig(format=u'%(filename)s [LINE:%(lineno)d] #%(levelname)-8s [%(asctime)s]  %(message)s',
                    level=logging.INFO,
                    )
logging.info('asdasd')
app = web.Application()
app.add_routes([web.options('/', hello), web.post('/', test)])
web.run_app(app, host='192.168.43.172', port=7777)

# from flask import Flask, request
# app = Flask(__name__)
#
#
# @app.route('/')
# def query_example():
#     # if key doesn't exist, returns None
#     language = request.headers
#     print(language)
#     return 'asd'
#
#
# if __name__ == "__main__":
#     app.run(host='192.168.43.172', port=7777)
