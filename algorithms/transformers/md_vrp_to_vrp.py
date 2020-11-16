from typing import List

import numpy as np

from models.rich_vrp import Depot, Job, Visit
from models.rich_vrp.geometries.geometry import DistanceAndTimeMatrixGeometry
from models.rich_vrp.problem import RichVRPProblem
from models.rich_vrp.solution import VRPSolution
from utils.types import Array
from .base import BaseTransformer
from ..utils.costs import get_inf


def _transform_new_new(
    matrix: Array,
    n: int,
    inf: int,
    ids: List[int]
):
    #  old | new | fake
    #  new | >x< |  01
    #  fake|  10 |  0

    for i in range(len(ids)):
        for index in range(len(ids)):
            # square of inf for new_jobs (moves between them)
            # make inf between in and out
            if i == index:
                matrix[n + i, n + i] = inf
                matrix[n + i + 1, n + i + 1] = inf
            else:
                matrix[n + i, n + i + index] = matrix[n + i, ids[index]]
                matrix[n + i + 1, ids[i]] = matrix[n + i + 1, ids[index]]
                matrix[n + i + index, n + i] = matrix[ids[index], n + i]
                matrix[ids[i], n + i + 1] = matrix[ids[index], n + i + 1]


def _transform_matrix(
    matrix: Array,
    pass_num: int,  # количество проходов
    ids: List[int],
) -> Array:
    inf = get_inf(matrix)
    n = len(matrix)
    new_size = n + 1 + pass_num * 2
    new_matrix = np.zeros((new_size, new_size))

    new_matrix[:n, :n] = matrix

    for index in ids:
        for k in range(pass_num):
            # copy depot table for this two
            new_matrix[n + k + index, :n] = matrix[index, :n]
            new_matrix[:n, n + k + index] = matrix[:n, index]
            new_matrix[n + k + 1 + index, :n] = matrix[index, :n]
            new_matrix[:n, n + k + 1 + index] = matrix[:n, index]

            # 0 and inf for fake
            # in
            new_matrix[n + k + index, -1] = 0
            new_matrix[-1, n + k + index] = inf
            # out
            new_matrix[n + k + 1 + index, -1] = inf
            new_matrix[-1, n + k + 1 + index] = 0

        # - depots
        new_matrix[index, :] = inf
        new_matrix[:, index] = inf

    _transform_new_new(matrix, n, inf)
    return new_matrix


class TransformerMdVrpToVrp(BaseTransformer):
    def __init__(self, pass_num: int = 50):
        self.pass_num = pass_num

    def transform(
        self,
        problem: RichVRPProblem,
        pass_num: int
    ) -> RichVRPProblem:
        # 1) check geom
        # 2) create fake deport
        # 3) move depots in jobs 'pass_num' times
        # 4) create matrixes

        for idx in problem.matrix.geometries:
            geometry = problem.matrix.geometries[idx]

            if not isinstance(geometry, DistanceAndTimeMatrixGeometry):
                raise ValueError

        place_mapping = problem.matrix

        # TODO: change params
        # TODO: я поставил пустые параметры, и как вы выдаете id я не знаю
        fake_depot = Depot(id=0, time_windows=[], lat=0, lon=0, delay=0)

        for idx in place_mapping.geometries:
            geometry = place_mapping.geometries[idx]

            matrix = geometry.dist_matrix()
            t_matrix = geometry.time_matrix()

            ids = []
            for depot in problem.depots:
                ids.append(place_mapping.mapping[depot])
                # + pass_num * 2
                new_jobs = []
                for _ in range(pass_num):
                    # create new job in and out
                    job_in = Job(id=depot.id, name=depot.name + '_in', lat=depot.lat, lon=depot.lon, x=depot.x,
                                 y=depot.y, time_windows=depot.time_windows, delay=depot.delay)
                    job_out = Job(id=depot.id, name=depot.name + '_out', lat=depot.lat, lon=depot.lon, x=depot.x,
                                  y=depot.y, time_windows=depot.time_windows, delay=depot.delay)
                    problem.jobs.append(job_in)
                    problem.jobs.append(job_out)

                    # just for updating points in geometry
                    new_jobs.append(job_in)
                    new_jobs.append(job_out)

            new_matrix = _transform_matrix(matrix, pass_num, ids)
            new_t_matrix = _transform_matrix(t_matrix, pass_num, ids)
            # TODO :: insert new matrix in geometry

        # TODO :: update points and mapping
        ###

        problem.depots = [fake_depot]
        return problem

    @staticmethod
    def restore(self, solution: VRPSolution) -> VRPSolution:
        pass_num = 5
        problem = self.transform(solution.problem, pass_num)
        routes = solution.routes

        # n | c * 2 | fake
        # ................
        visited_places = {}
        n = len(solution.problem.depots)
        for plan in routes:
            # change waypoints
            #   remove old
            #   add new in, out, fake
            # it's all

            waypoints = plan.waypoints
            # there is old_places but which of them - depots
            # TODO :: Делать ли чек на problem is RichVRPProblem
            for dep_id in range(len(solution.problem.depots)):
                # TODO :: Нужно ли соблюдать порядок в plan.waypoints
                # TODO :: Точно ли несколько depots в wapoints
                dep = solution.problem.depots[dep_id]
                depots_waypoints = list(filter(lambda x: x.place == dep, waypoints))
                for depots_waypoint in depots_waypoints:
                    # add in, out, fake
                    time_in = depots_waypoint.time

                    # get from dep current job_in id in jobs
                    current_pass = visited_places.get(dep, 0)
                    visited_places[dep] += 1

                    job_in_id = n + dep_id * pass_num + current_pass
                    job_out_id = job_in_id + 1

                    job_in_place = problem.jobs[job_in_id]
                    job_out_place = problem.jobs[job_out_id]
                    fake_place = problem.depots[0]

                    waypoints.append(Visit(job_in_place, time_in))
                    waypoints.append(Visit(fake_place, time_in))
                    waypoints.append(Visit(job_out_place, time_in))

                # remove depots
                waypoints = list(filter(lambda x: x.place != dep, waypoints))

        return VRPSolution(problem, routes)

# TODO :: Проверить трансформацию на ошибки
# TODO :: Проверить восстановление пути на ошибки
