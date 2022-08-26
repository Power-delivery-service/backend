from __future__ import annotations

import copy
import logging
import heapq
import math
import typing as tp
import numpy as np
from app import models
from . import path_smoother
from . import direction_finder


class Node:
    """A node class for A* Pathfinding"""

    def __init__(self, parent: Node = None, position: models.WayPoint = None):
        self.parent: Node = parent
        self.position: models.WayPoint = position

        self.g = 0
        self.h = 0
        self.f = 0

    def __eq__(self, other):
        return self.position == other.position

    def __repr__(self):
        return f"{self.position} - g: {self.g} h: {self.h} f: {self.f}"

    # defining less than for purposes of heap queue
    def __lt__(self, other):
        return self.f < other.f

    # defining greater than for purposes of heap queue
    def __gt__(self, other):
        return self.f > other.f


class AStar:
    def __init__(self) -> None:
        self.__maze: tp.Optional[np.array] = None
        self.__start: tp.Optional[models.WayPoint] = None
        self.__target: tp.Optional[models.WayPoint] = None
        self.__result_path = tp.Optional[tp.List[tp.Tuple[int, int]]]

    @property
    def maze(self) -> np.array:
        return self.__maze

    @maze.setter
    def maze(self, maze: np.array) -> None:
        self.__maze = maze

    @property
    def points(self) -> models.DataPoints:
        return models.DataPoints(start=self.__start, target=self.__target)

    @points.setter
    def points(self, points: models.DataPoints) -> None:
        self.__maze_set_check()
        self.__points_reachable_check(points)

        self.__start = points.start
        self.__target = points.target

    def __maze_set_check(self) -> None:
        if self.__maze is None:
            raise Exception('Map needs to be set first')

    def __points_reachable_check(self, points: models.DataPoints) -> None:
        if (points.start.point_x > self.__maze.shape[0]) or \
                (points.start.point_y > self.__maze.shape[1]):
            raise Exception('Start is out of range')
        elif (points.target.point_x > self.__maze.shape[0]) or \
                (points.target.point_y > self.__maze.shape[1]):
            raise Exception('End is out of range')

        if self.__maze[points.start.point_x][points.start.point_y] == 1:
            raise Exception('Start is unreachable')
        elif self.__maze[points.target.point_x][points.target.point_y] == 1:
            raise Exception('End is unreachable')

    def __points_set_check(self) -> None:
        if self.__start is None or self.__target is None:
            raise Exception('Points need to be set')

    def __return_path(self, current_node) -> None:
        path = []
        current = current_node
        while current is not None:
            path.append(current.position)
            current = current.parent
        self.__result_path = path[::-1]

    def get_path(self) -> tp.Optional[tp.List[models.WayPoint]]:
        return self.__result_path

    async def smooth_path(self, path: tp.List[models.WayPoint]) \
            -> tp.List[models.WayPoint]:
        smoothed_path = [path[0]]
        flag = False

        l, r = 0, len(path) - 1
        while l < len(path) - 1:
            if await path_smoother.is_line_possible(path[l], path[r], self.__maze) is not None:
                smoothed_path.append(path[r])
                l = copy.copy(r)
                r = len(path) - 1
            else:
                r -= 1

        return smoothed_path

        # i = 0
        # while i < (len(path) - 2):
        #     if await path_smoother.is_line_possible(path[i], path[i + 2], self.__maze) is not None:
        #         smoothed_path.append(path[i + 2])
        #         i += 2
        #     else:
        #         smoothed_path.append(path[i + 1])
        #         i += 1
        #
        # # smoothed_path.append(path[-1])
        # print(smoothed_path)
        # return [_ for _ in smoothed_path]

    async def get_angles(self, points: tp.List[models.WayPoint]):
        start_vector_start = models.WayPoint.from_request((points[0].point_x, self.__maze.shape[1]))

        path = [start_vector_start]
        path.extend(points)
        angles_path = []

        for i in range(1, len(path) - 1):
            start = direction_finder.to_cartesian_coordinates((path[i - 1]), self.__maze.shape)
            waypoint = direction_finder.to_cartesian_coordinates(path[i], self.__maze.shape)
            end = direction_finder.to_cartesian_coordinates(path[i + 1], self.__maze.shape)

            angle = await direction_finder.get_rotation_angle(start, waypoint, end)
            angles_path.append(angle)

        return angles_path

    async def visualise(self, path: tp.List[models.WayPoint]) -> None:
        ind = 0
        path_maze = []
        print('\n')
        print(' ', [str(_) for _ in range(self.__maze.shape[1])])
        for i in range(self.__maze.shape[0]):
            a = []
            for j in range(self.__maze.shape[1]):
                if models.WayPoint.from_request((i, j)) in path:
                    # a.append(f'{ind}')
                    a.append('0')
                    ind += 1
                elif self.__maze[i][j] == 0:
                    a.append('.')
                elif self.__maze[i][j] == 1:
                    a.append('#')
            path_maze.append(a)

        for i in range(len(path_maze)):
            print(i, path_maze[i])

    async def solve(self) -> None:
        self.__maze_set_check()
        self.__points_set_check()
        start_node = Node(None, self.__start)
        start_node.g = start_node.h = start_node.f = 0
        target_node = Node(None, self.__target)
        target_node.g = target_node.h = target_node.f = 0

        open_list = []
        closed_list = []

        heapq.heapify(open_list)
        heapq.heappush(open_list, start_node)

        outer_iterations = 0
        # max_iterations = (len(self.__maze[0]) * len(self.__maze))
        max_iterations = 1e6

        adjacent_squares = ((0, -1), (0, 1), (-1, 0), (1, 0), (-1, -1), (-1, 1), (1, -1), (1, 1),)

        while len(open_list) > 0:
            outer_iterations += 1

            current_node = heapq.heappop(open_list)
            closed_list.append(current_node)

            if outer_iterations > max_iterations:
                logging.info("giving up on pathfinding too many iterations")
                return self.__return_path(current_node)

            if current_node == target_node:
                logging.info(f'{outer_iterations} iterations were spent')
                return self.__return_path(current_node)

            children = []
            for new_position in adjacent_squares:
                node_position = models.WayPoint.from_request(
                    (current_node.position.point_x + new_position[0],
                     current_node.position.point_y + new_position[1]))

                # Make sure within distance
                if (node_position.point_x > (len(self.__maze) - 1)) or \
                        (node_position.point_x < 0) or \
                        (node_position.point_y > (self.__maze.shape[1] - 1)) or \
                        (node_position.point_y < 0):
                    continue

                # Make sure walkable terrain
                if self.__maze[node_position.point_x][node_position.point_y] == 1:
                    continue

                children.append(Node(current_node, node_position))

            for child in children:
                # Child in the closed list
                if len([closed_child for closed_child in closed_list if closed_child == child]) > 0:
                    continue

                # Child is already in open list
                if len([open_node for open_node in open_list if
                        child.position == open_node.position and child.g > open_node.g]) > 0:
                    continue

                child.g = current_node.g + 1
                child.h = math.sqrt(((child.position.point_x - target_node.position.point_x) ** 2) +
                                    ((child.position.point_y - target_node.position.point_y) ** 2))
                # child.h = abs(child.position[0] - target_node.position[0]) - \
                #           abs(child.position[1] - target_node.position[1])
                child.f = child.g + child.h

                heapq.heappush(open_list, child)

        logging.info("Couldn't get a path to destination")
        return None
