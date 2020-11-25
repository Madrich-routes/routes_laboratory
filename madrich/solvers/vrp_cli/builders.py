from typing import Dict, Tuple, List
import numpy as np
from madrich.solvers.madrich.api_module.osrm_module import get_matrix
from madrich.models.rich_vrp.geometries.geometry import HaversineGeometry
from madrich.models.rich_vrp.job import Job
from madrich.models.rich_vrp.depot import Depot
from madrich.models.rich_vrp.place_mapping import PlaceMapping
from madrich.models.rich_vrp.problem import RichVRPProblem, RichMDVRPProblem


def build_matrix(points: np.ndarray, factor: str, geom_type: str, def_speed: float) -> np.ndarray:
    """
    Универсальня функция, возвращающая матрицу расстояний для указанных точек,
    в соответствии с требуемым транспортом и его средней скоростью

    Parameters
    ----------
    points: Точки, для которых мы строим матрицу
    factor: Тип искомой матрицы
    transport: Тип транспорта и его средняя скорость, при наличии

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
        pass
    else:
        if not np.isnan(def_speed) and factor == "duration":
            res = get_matrix(points=points, factor="distance", transport=geom_type)
            res /= def_speed
        else:
            res = get_matrix(points=points, factor=factor, transport=geom_type)
    return res


def get_geometries(pts: np.ndarray, profiles: Dict[str, Tuple[str, float]]) -> dict:
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
