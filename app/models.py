from __future__ import annotations
import dataclasses
import typing as tp
import numpy as np


@dataclasses.dataclass
class Maze:
    maze: np.array
    maze = np.array([[0, 0, 0, 0, 1, 0, 0, 0, 0, 0],
                     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     [0, 0, 0, 0, 1, 0, 0, 0, 0, 0],
                     [0, 0, 0, 0, 1, 0, 0, 0, 0, 0],
                     [0, 0, 0, 0, 1, 0, 0, 0, 0, 0],
                     [0, 0, 0, 0, 1, 0, 0, 0, 0, 0],
                     [0, 0, 0, 0, 1, 0, 0, 0, 0, 0],
                     [0, 0, 0, 0, 1, 0, 0, 0, 0, 0],
                     [0, 0, 0, 0, 1, 0, 0, 0, 0, 0],
                     [0, 0, 0, 0, 1, 0, 0, 0, 0, 0],
                     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0], ])


@dataclasses.dataclass
class WayPoint:
    point_x: tp.Optional[int]
    point_y: tp.Optional[int]

    @classmethod
    def from_request(cls, point: tp.Tuple[int, int]) -> WayPoint:
        return cls(point_x=point[0], point_y=point[1])


@dataclasses.dataclass
class DataPoints:
    start: WayPoint
    target: WayPoint

    @classmethod
    def from_request(cls, json):
        point_start_x = int(json['point_start_x'])
        point_start_y = int(json['point_start_y'])
        point_target_x = int(json['point_target_x'])
        point_target_y = int(json['point_target_y'])

        return cls(start=WayPoint.from_request((point_start_x, point_start_y)),
                   target=WayPoint.from_request((point_target_x, point_target_y)))

