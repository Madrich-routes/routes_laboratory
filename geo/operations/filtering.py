import math
from typing import Optional, Tuple

square_bounds = {
    "мкад": ((54.288066, 57.172201), (34.619289, 39.724750)),
    "область": ((55.572208, 55.920812), (37.349728, 37.860592)),
}

radial_bounds = {
    "бетонка": 0.5,
    'мкад': 0.25,
}

points = {
    'moscow_center': (55.7558, 37.6173)
}


def check_circle(
        lat: float,
        lon: float,
        center: Tuple[float, float],
        radius: float,
) -> bool:
    """
    Проверяем, что точка принадлежит окружности

    Parameters
    ----------
    lat : широта
    lon : долгота
    center : координаты центра
    radius : радиус

    Returns
    -------
    bool, True — если лежит в круге
    """

    dist = math.sqrt(
        (lat - center[0]) ** 2 + (lon - center[1]) ** 2
    )

    return dist < radius


def check_square(
        lat: float,
        lon: float,
        borders: Optional[Tuple[Tuple[float, float], Tuple[float, float]]] = None,
        region: Optional[str] = None,
) -> bool:
    """
    Проверяем, что точка лежит в квадрате

    >>> check_square(0, 1, ((-1, 1), (-1, 1)))
    True
    >>> check_square(0, 1, ((1, 2), (1, 2)))
    False

    Returns
    -------
    bool, True — если лежит в квадрате
    """
    borders = square_bounds.get(region, borders)
    if borders is None:
        raise ValueError("Нужноп передать границы!")

    return borders[0][0] <= lat <= borders[0][1] and borders[1][0] <= lon <= borders[1][1]
