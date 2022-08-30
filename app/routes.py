from aiohttp import web
from app.api import handlers
from app import context


def wrap_handler(handler, ctx: context.AppContext):
    async def wrapper(request):
        return await handler(request, ctx)

    return wrapper


def setup_routes(app: web.Application, ctx: context.AppContext) -> None:
    app.router.add_options(
        "/set_geodata", wrap_handler(handlers.CorsOptionsHandler(), ctx)
    )
    app.router.add_post("/set_geodata", wrap_handler(handlers.SetGeodataHandler(), ctx))
    app.router.add_get(
        "/get_geodata", wrap_handler(handlers.GetWaypointsHandler(), ctx)
    )
