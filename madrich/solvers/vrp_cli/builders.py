from typing import Dict, Tuple, List, Union

import numpy as np

from madrich.models.rich_vrp.depot import Depot
from madrich.models.rich_vrp.geometries.geometry import HaversineGeometry
from madrich.models.rich_vrp.geometries.transport import TransportMatrixGeometry
from madrich.models.rich_vrp.job import Job
from madrich.models.rich_vrp.place_mapping import PlaceMapping
from madrich.models.rich_vrp.problem import RichVRPProblem
from madrich.solvers.madrich.api_module.osrm_module import get_matrix

Points = Union[np.ndarray, list]


def build_matrix(points: Points, factor: str, geom_type: str, def_speed: float) -> np.ndarray:
    """
    Универсальня функция, возвращающая матрицу расстояний для указанных точек,
    в соответствии с требуемым транспортом и его средней скоростью

    Parameters
    ----------
    points: Точки, для которых мы строим матрицу
    factor: Тип искомой матрицы
    geom_type: тип матрицы геометрии
    def_speed: заранее заданная средня скорость, если нуна матричная - nan

    Returns
    ----------
    Матрица расстояний или времен перемещений
    """

    if geom_type == "haversine":
        # если скорость не задана - устанавливаем равной 15
        geom = HaversineGeometry(points, default_speed=def_speed if not np.isnan(def_speed) else 15)
        if factor == "distance":
            res = geom.dist_matrix()
        else:
            res = geom.time_matrix()
    elif geom_type == "transport":
        dist_between_points = get_matrix(points=points, factor="distance", transport="foot")
        if factor == "distance":
            res = dist_between_points
        else:
            transport_geom = TransportMatrixGeometry(points=points, distance_matrix=dist_between_points)
            res = transport_geom.time_matrix()
    else:
        if not np.isnan(def_speed) and factor == "duration":
            res = get_matrix(points=points, factor="distance", transport=geom_type)
            res /= def_speed
        else:
            res = get_matrix(points=points, factor=factor, transport=geom_type)
    return res


def get_geometries(pts: Points, profiles: Dict[str, Tuple[str, float]]) -> dict:
    """
    Строим словарь геометрий для PlaceMapping.

    Parameters
    ----------
    pts: Массив точек
    profiles: Словарь описаний профилей в формате: название_профиля:(тип_транспорта, средняя_скорость)

    Returns
    ----------
    Словарь геометрий, в формате описанном в PlaceMapping

    """
    geometries = {
        profile: {
            "dist_matrix": build_matrix(points=pts, factor="distance", geom_type=transport[0], def_speed=transport[1]),
            "time_matrix": build_matrix(points=pts, factor="duration", geom_type=transport[0], def_speed=transport[1]),
        }
        for profile, transport in profiles.items()
    }
    return geometries


def get_problems(
    jobs_list: List[Job], depots_list: List[Depot], profiles: Dict[str, Tuple[str, float]]
) -> List[RichVRPProblem]:
    """
    Собираем список RichVRPProblem из полученных данных для последующего построения RichMDVRPProblem

    Parameters
    ----------
    jobs_list: Список задач на доставку
    depots_list: Список депо
    profiles: Профили для построения матриц расстояний в объектах задач

    Returns
    ----------
    Список RichVRPProblem
    """
    problems = []

    for depot in depots_list:
        this_depot_jobs = [job for job in jobs_list if job.depot.id == depot.id]

        pts = [(job.lat, job.lon) for job in this_depot_jobs] + [(depot.lat, depot.lon)]
        geometries = get_geometries(pts, profiles)
        places = [depot] + this_depot_jobs  # noqa
        problem = RichVRPProblem(
            place_mapping=PlaceMapping(places=places, geometries=geometries),
            agents=[],
            jobs=this_depot_jobs,
            depot=depot,
        )
        problems.append(problem)

    return problems
