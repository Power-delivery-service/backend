from aiohttp import web
from app import context
from app import srotage
import typing as tp
from app import models
from app.utils import a_star_pathfinder
import pickle
import abc


class BaseHandler(abc.ABC):
    async def __call__(self, request: web.Request, ctx: context.AppContext) -> tp.Optional[web.Response]:
        if request.method == 'POST':
            await self.__post_check(request)
        return await self.handle(request, ctx)

    @staticmethod
    async def __post_check(request: web.Request):
        data = await request.json()

        if not ("application/json" in request.headers["Content-Type"]):
            return web.Response(text='Data must be in JSON format')

        if not all(x.isdigit() for x in data.values()):
            return web.Response(text='All coordinates must be integers')

    @abc.abstractmethod
    async def handle(self, request: web.Request, ctx: context.AppContext) -> None:
        raise NotImplemented


class SetGeodataHandler(BaseHandler):
    async def handle(self, request: web.Request, ctx: context.AppContext) -> web.Response:
        request_data = await request.json()

        algorythm = a_star_pathfinder.AStar()
        algorythm.maze = models.Maze.maze
        algorythm.points = models.DataPoints.from_request(request_data)
        await algorythm.solve()
        path = [(x.point_x, x.point_y) for x in algorythm.get_path()]

        srotage.task_push(ctx, await self.serialise(path))

        return web.Response(text='Waypoints calculated')

    @staticmethod
    async def serialise(path: tp.List[tp.Tuple[int, int]]) -> bytes:
        waypoints = {i: x for i, x in enumerate(path)}
        return pickle.dumps(waypoints)


class GetWaypointsHandler(BaseHandler):
    async def handle(self, request: web.Request, ctx: context.AppContext) -> web.Response:
        return web.json_response(srotage.get_waypoints(ctx))





