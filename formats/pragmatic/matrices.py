from typing import Dict

import ujson

from models.rich_vrp.geometries.base import BaseGeometry
from utils.types import Matrix


def dumps_matrix(
    profile: str,
    distance_matrix: Matrix,
    time_matrix: Matrix,
) -> str:
    """Получаем pragmatic представление матрицы расстояний.

    Parameters
    ----------
    profile : профайл (например driver, foot, transport)
    distance_matrix : матрица расстояний
    time_matrix : матрица времениы

    Returns
    -------
    Строковое представление в pragmatic
    """
    obj = {
        "profile": profile,
        "travelTimes": time_matrix.flatten().tolist(),
        "distances": distance_matrix.flatten().tolist(),
    }

    return ujson.dumps(obj)


def build_matrices(
    geometries: Dict[str, BaseGeometry],
) -> Dict[str, str]:
    """Строим матрицы для словаря геометрий.

    Parameters
    ----------
    geometries : Словарь profile -> geometry

    Returns
    -------
    Словарь profile -> matrix
    """
    return {
        p: dumps_matrix(profile=p, distance_matrix=g.dist_matrix(), time_matrix=g.time_matrix())
        for p, g in geometries.items()
    }
