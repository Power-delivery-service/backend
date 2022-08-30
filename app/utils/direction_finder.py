import asyncio
import math
from app import models
import numpy as np


def to_cartesian_coordinates(point: models.GridLocation, shape):
    return point[1], shape[1] - point[0]


def to_cartesian_coords_tuple(point: tuple, shape):
    return point[1], shape[1] - point[0]


async def get_distance(start: models.GridLocation, end: models.GridLocation):
    (start_x, start_y) = start
    (end_x, end_y) = end

    return round(
        math.sqrt(((end_x - start_x + 1) ** 2) + ((end_y - start_y + 1) ** 2)), 4
    )


async def get_rotation_angle(
    line_start: models.GridLocation,
    waypoint: models.GridLocation,
    line_end: models.GridLocation,
) -> float:
    (start_x, start_y) = line_start
    (waypoint_x, waypoint_y) = waypoint
    (end_x, end_y) = line_end

    vector_start = np.array([start_x - waypoint_x, start_y - waypoint_y])
    vector_end = np.array([end_x - waypoint_x, end_y - waypoint_y])

    vector_start_unit = vector_start / np.linalg.norm(vector_start)
    vector_end_unit = vector_end / np.linalg.norm(vector_end)
    angle = 180 - abs(
        float(
            np.degrees(
                np.arccos(
                    np.clip(np.dot(vector_start_unit, vector_end_unit), -1.0, 1.0)
                )
            )
        )
    )

    # D = (х3 - х1) * (у2 - у1) - (у3 - у1) * (х2 - х1)
    D = ((end_x - start_x) * (waypoint_y - start_y)) - (
        (end_y - start_y) * (waypoint_x - start_x)
    )

    if D < 0:
        angle = -angle  # left

    return round(angle, 4)
