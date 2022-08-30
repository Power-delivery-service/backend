import copy
from app import models
import typing as tp


async def is_line_possible(
    start: models.GridLocation,
    target: models.GridLocation,
    maze: models.GridWithWeights,
) -> tp.Optional[tp.List[models.WayPoint]]:
    # Brezenham's algorythm

    (start_x, start_y) = start
    (target_x, target_y) = target

    path = []
    d_x = 1 if (target_x - start_x) >= 0 else -1
    d_y = 1 if (target_y - start_y) >= 0 else -1

    length_x = abs(target_x - start_x)
    length_y = abs(target_y - start_y)
    length = max(length_x, length_y)

    if length == 0:
        path.append(start)
        return path

    if length_y <= length_x:
        x = copy.copy(start_x)
        y = copy.copy(start_y)
        c = 0

        for i in range(length + 1):
            if (x, y) in maze.walls:
                # print('Unreachable')
                return None
            path.append(models.WayPoint.from_request((x, (round(y)))))

            # y = z + c, где z это y, округленная до ближайшего целого, а с принадлежит отрезку [-0.5; 0.5]
            x += d_x
            c += float(length_y) / length_x
            if c > 0.5:
                c -= 1
                y += d_y
        return path

    else:
        x = copy.copy(start_x)
        y = copy.copy(start_y)
        c = 0

        for i in range(length + 1):
            if (x, y) in maze.walls:
                # print('Unreachable')
                return None

            path.append(models.WayPoint.from_request((round(x), y)))
            y += d_y
            c += float(length_x) / length_y
            if c > 0.5:
                c -= 1
                x += d_x

        return path
