from __future__ import annotations

import copy
import heapq
import math
import typing as tp
import numpy as np
from app import models
from . import path_smoother
from . import direction_finder


class PriorityQueue:
    def __init__(self):
        self.elements = []

    def empty(self) -> bool:
        return not self.elements

    def put(self, item, priority: float):
        heapq.heappush(self.elements, (priority, item))

    def get(self):
        return heapq.heappop(self.elements)[1]


class AStar:
    def __init__(self) -> None:
        self.__maze: tp.Optional[models.GridWithWeights] = None
        self.__start: tp.Optional[models.GridLocation] = None
        self.__target: tp.Optional[models.GridLocation] = None
        self.__result_path: tp.Optional[tp.List[models.GridLocation]] = None

    @property
    def maze(self) -> np.array:
        return self.__maze

    @maze.setter
    def maze(self, maze: np.array) -> None:
        width = maze.shape[0]
        heigth = maze.shape[1]
        self.__maze = models.GridWithWeights(width, heigth, maze)

    @property
    def points(self) -> (models.GridLocation, models.GridLocation):
        return self.__start, self.__target

    @points.setter
    def points(self, points: (models.GridLocation, models.GridLocation)) -> None:
        (start, target) = points
        self.__maze_set_check()
        self.__points_reachable_check(points)

        self.__start = start
        self.__target = target

    def __maze_set_check(self) -> None:
        if self.__maze is None:
            raise Exception("Map needs to be set first")

    def __points_reachable_check(
        self, points: (models.GridLocation, models.GridLocation)
    ) -> None:
        (start, target) = points
        if (start[0] > self.__maze.width) or (start[1] > self.__maze.height):
            raise Exception("Start is out of range")
        elif (target[0] > self.__maze.width) or (target[1] > self.__maze.height):
            raise Exception("End is out of range")

        if start in self.__maze.walls:
            raise Exception("Start is unreachable")
        elif target in self.__maze.walls:
            raise Exception("End is unreachable")

    def __points_set_check(self) -> None:
        if self.__start is None or self.__target is None:
            raise Exception("Points need to be set")

    def __return_path(self, current_node, came_from):
        path = []
        current = came_from[current_node]
        while current is not None:
            path.append(current)
            current = came_from[current]

        self.__result_path = path[::-1]

    def get_path(self) -> tp.Optional[tp.List[models.GridLocation]]:
        return self.__result_path

    async def smooth_path(
        self, path: tp.List[models.GridLocation]
    ) -> tp.List[models.GridLocation]:
        smoothed_path = [path[0]]

        l, r = 0, len(path) - 1
        while l < len(path) - 1:
            if (
                await path_smoother.is_line_possible(path[l], path[r], self.__maze)
                is not None
            ):
                smoothed_path.append(path[r])
                l = copy.copy(r)
                r = len(path) - 1
            else:
                r -= 1

        return smoothed_path

    async def get_angles(self, points: tp.List[models.GridLocation]):
        start_vector_start = (0, points[0][1])

        path = [start_vector_start]
        path.extend(points)
        angles_path: tp.List[float] = []

        for i in range(1, len(path) - 1):
            start = direction_finder.to_cartesian_coordinates(
                (path[i - 1]), (self.__maze.width, self.__maze.height)
            )
            waypoint = direction_finder.to_cartesian_coordinates(
                path[i], (self.__maze.width, self.__maze.height)
            )
            end = direction_finder.to_cartesian_coordinates(
                path[i + 1], (self.__maze.width, self.__maze.height)
            )

            angle = await direction_finder.get_rotation_angle(start, waypoint, end)
            angles_path.append(angle)

        return angles_path

    async def visualise(
        self, path: tp.List[models.GridLocation], maze: np.array
    ) -> None:
        ind = 0
        path_maze = []
        print("\n")
        print(" ", [str(_) for _ in range(self.__maze.height)])
        for i in range(self.__maze.width):
            a = []
            for j in range(self.__maze.height):
                if (i, j) in path:
                    # a.append(f'{ind}')
                    a.append("0")
                    ind += 1
                elif maze[i][j] == 0:
                    a.append(".")
                elif maze[i][j] == 1:
                    a.append("#")
            path_maze.append(a)

        for i in range(len(path_maze)):
            print(i, path_maze[i])

    @staticmethod
    def __heuristic(a: models.GridLocation, b: models.GridLocation) -> float:
        (x1, y1) = a
        (x2, y2) = b
        return math.sqrt(((x1 - x2) ** 2) + ((y1 - y2) ** 2))

    def a_star_search(self):
        graph = self.__maze
        start = (self.__start[0], self.__start[1])
        goal = (self.__target[0], self.__target[1])

        frontier = PriorityQueue()
        frontier.put(start, 0)
        came_from = {}
        cost_so_far = {}
        came_from[start] = None
        cost_so_far[start] = 0

        while not frontier.empty():
            current = frontier.get()

            if current == goal:
                self.__return_path(current, came_from)
                break

            for next in graph.neighbors(current):
                new_cost = cost_so_far[current] + graph.cost(current, next)
                if next not in cost_so_far or new_cost < cost_so_far[next]:
                    cost_so_far[next] = new_cost
                    priority = new_cost + self.__heuristic(next, goal)
                    frontier.put(next, priority)
                    came_from[next] = current
