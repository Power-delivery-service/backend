from aiohttp import web
from app import context
from app import srotage
import typing as tp
from app import models
from app.utils import a_star_pathfinder
import pickle
import abc
from app.utils import direction_finder


class BaseHandler(abc.ABC):
    async def __call__(
        self, request: web.Request, ctx: context.AppContext
    ) -> tp.Optional[web.Response]:
        if request.method == "POST":
            await self.__post_check(request)
        return await self.handle(request, ctx)

    @staticmethod
    async def __post_check(request: web.Request):
        data = await request.json()

        if not ("application/json" in request.headers["Content-Type"]):
            return web.Response(text="Data must be in JSON format")

        if not all(x.isdigit() for x in data.values()):
            return web.Response(text="All coordinates must be integers")

    @abc.abstractmethod
    async def handle(self, request: web.Request, ctx: context.AppContext) -> None:
        raise NotImplemented


class CorsOptionsHandler(BaseHandler):
    async def handle(
        self, request: web.Request, ctx: context.AppContext
    ) -> web.Response:
        return web.Response(
            status=200,
            headers={
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "POST, GET, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type",
            },
        )


class SetGeodataHandler(BaseHandler):
    async def handle(
        self, request: web.Request, ctx: context.AppContext
    ) -> web.Response:
        request_data = await request.json()

        angles, distances = await self.calculate(request_data)
        movements_list = await self.to_response(angles, distances)
        srotage.task_push(ctx, await self.serialise(movements_list))

        return web.Response(text="Waypoints calculated")

    async def calculate(
        self, request_data: dict
    ) -> tp.Tuple[tp.List[float], tp.List[float]]:
        algorythm = a_star_pathfinder.AStar()
        algorythm.maze = models.Maze.maze_thin  # TODO: сделать обработку исключений
        algorythm.points = await self.from_request(request_data)
        algorythm.a_star_search()

        path = algorythm.get_path()
        smoothed = await algorythm.smooth_path(path)
        angles = await algorythm.get_angles(smoothed)

        distances = [
            await direction_finder.get_distance(smoothed[_], smoothed[_ + 1])
            for _ in range(len(smoothed) - 1)
        ]

        await algorythm.visualise(smoothed, models.Maze.maze_thin)
        await algorythm.visualise(path, models.Maze.maze_thin)

        return angles, distances

    @staticmethod
    async def from_request(json):
        sector_target = json["sector_target"]

        waypoints = {
            "0": (4, 8),
            "1": (0, 0),
            "2": (3, 35),
            "3": (4, 52),
            "4": (21, 4),
            "5": (23, 16),
            "6": (0, 0),
            "7": (22, 51),
        }

        return (4, 16), waypoints[sector_target]

    @staticmethod
    async def serialise(path: tp.Dict[str, tp.List[tp.Dict[str, float]]]) -> bytes:
        return pickle.dumps(path)

    @staticmethod
    async def to_response(
        angles: tp.List[float], distances: tp.List[float]
    ) -> tp.Dict[str, tp.List[tp.Dict[str, float]]]:
        row: tp.Dict[str, tp.List[tp.Dict[str, float]]] = {"way": []}
        for i in range(len(angles)):
            row["way"].append({"type": "rotate", "value": angles[i]})
            row["way"].append({"type": "run", "value": distances[i]})

        return row


class GetWaypointsHandler(BaseHandler):
    async def handle(
        self, request: web.Request, ctx: context.AppContext
    ) -> web.Response:
        return web.json_response(srotage.get_waypoints(ctx))
