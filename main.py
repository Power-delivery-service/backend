import asyncio
import logging
from aiohttp import web
from app import routes, config
from app import context


async def create_app(secrets) -> web.Application:
    app = web.Application()
    ctx = context.AppContext(secrets)

    routes.setup_routes(app, ctx)

    app.on_startup.append(ctx.on_startup)
    app.on_shutdown.append(ctx.on_shutdown)

    return app


if __name__ == "__main__":
    logging.basicConfig(
        format="%(filename)s [LINE:%(lineno)d] #%(levelname)-8s [%(asctime)s]  %(message)s",
        level=logging.INFO,
    )

    loop = asyncio.new_event_loop()
    app = loop.run_until_complete(create_app(secrets={}))
    web.run_app(app, host=config.IP, port=config.SERVER_PORT)
