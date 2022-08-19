from __future__ import annotations

import logging
import heapq
import math
import typing as tp
import numpy as np
from app import models


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
        if (points.start.point_x > self.__maze.shape[0]) or\
                (points.start.point_y > self.__maze.shape[1]):
            raise Exception('Start is out of range')
        elif (points.target.point_x > self.__maze.shape[0]) or\
                (points.target.point_y > self.__maze.shape[1]):
            raise Exception('End is out of range')

        if self.__maze[points.start.point_x][points.start.point_y] == 1:
            raise Exception('Start is unreachable')
        elif self.__maze[points.target.point_x][points.target.point_y] == 1:
            raise Exception('End is unreachable')

    def __points_set_check(self) -> None:
        if self.__start is None or self.__target is None:
            raise Exception('Points need to be set')

    def get_path(self) -> tp.Optional[tp.List[tp.Tuple[int, int]]]:
        return self.__result_path

    def __return_path(self, current_node) -> None:
        path = []
        current = current_node
        while current is not None:
            path.append(current.position)
            current = current.parent
        self.__result_path = path[::-1]

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
