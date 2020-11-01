import logging
from typing import Dict, List, Optional, Tuple

from solvers.madrich.api_module import osrm_module
from solvers.madrich.problems.models import Matrix
from solvers.madrich.problems.vrp_demo.models import Courier, Job, Problem, Storage
from solvers.madrich.problems.vrp_demo.operators.improve import improve_tour
from solvers.madrich.utils import to_array


class PointsMapping:

    def __init__(self):
        self.__mapping: Dict[Tuple[float, float], int] = {}
        self.__counter = 0

    def __getitem__(self, item: Tuple[float, float]) -> Optional[int]:
        return self.__mapping[item] if item in self.__mapping else None

    def points(self) -> List[Tuple[float, float]]:
        return [point for point in self.__mapping]

    def add_point(self, point: Tuple[float, float]) -> int:
        if point not in self.__mapping:
            self.__mapping[point] = self.__counter
            self.__counter += 1
        return self.__mapping[point]

    def add_points(self, points: List[Tuple[float, float]]) -> List[int]:
        points_ids = []
        for point in points:
            points_ids.append(self.add_point(point))
        return points_ids


class SearchEngine:

    def __init__(self, jobs: List[Job], couriers: List[Courier], storage: Storage, problem: Problem, improve=True):
        self.points = PointsMapping()
        self.problem = problem
        self.profiles = [courier.profile for courier in couriers]

        logging.info('Generating matrix...')
        self.__generate_matrix(jobs, couriers, storage)
        logging.info('Generating tour...')
        self.tour = problem.init(storage, jobs, couriers, self.matrix)

        if improve:
            _, self.tour = improve_tour(self.tour, self.problem, False, False)

    def __generate_matrix(self, jobs: List[Job], couriers: List[Courier], storage: Storage) -> None:
        points = [storage.location.point]
        points += [job.location.point for job in jobs]
        points += [courier.start_location.point for courier in couriers]
        points += [courier.end_location.point for courier in couriers]
        self.points.add_points(points)

        storage.location.matrix_id = self.points[storage.location.point]
        for job in jobs:
            job.location.matrix_id = self.points[job.location.point]
        for courier in couriers:
            courier.start_location.matrix_id = self.points[courier.start_location.point]
            courier.end_location.matrix_id = self.points[courier.end_location.point]
        self.__update_matrix()

    def __update_matrix(self):
        self.matrix = {}
        for profile in self.profiles:
            d, s = osrm_module.coefficient['distance_car'], osrm_module.coefficient['speed_car']
            osrm = osrm_module.get_matrix(to_array(self.points.points()), 'distance')
            distance, travel_time = osrm * d, (osrm * d) / s
            self.matrix[profile] = Matrix(profile, distance, travel_time)

    def improve(self, cross=False, three_opt=False) -> bool:
        result, self.tour = improve_tour(self.tour, self.problem, cross, three_opt)
        return result

    def insert_job(self, job: Job) -> None:
        self.insert_jobs([job])

    def insert_jobs(self, jobs: List[Job]) -> None:
        self.points.add_points([job.location.point for job in jobs])
        for job in jobs:
            job.location.matrix_id = self.points[job.location.point]
        self.tour.unassigned_jobs += jobs
        self.__update_matrix()
        for route in self.tour.routes:
            route.matrix = self.matrix[route.courier.profile]
