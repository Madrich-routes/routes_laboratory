from copy import deepcopy
from typing import List

import numpy as np

from models.rich_vrp import Depot, Job
from utils.types import Array

from .base import BaseTransformer

from models.rich_vrp.problem import RichVRPProblem
from models.rich_vrp.solution import VRPSolution
from models.rich_vrp.geometries.geometry import DistanceAndTimeMatrixGeometry
from ..utils.costs import get_inf


def add_depot():


def _transform_matrix(
    matrix: Array,
    pass_num: int,  # количество проходов
) -> Array:
    inf = get_inf(matrix)
    n = len(matrix)
    new_size = n + 1 + pass_num * 2
    new_matrix = np.zeros((new_size, new_size))

    new_matrix[:n, :n] = matrix


class TransformerMdVrpToVrp(BaseTransformer):
    def __init__(self, pass_num: int = 50):
        self.pass_num = pass_num

    def transform(
        self,
        problem: RichVRPProblem,
        count: int
    ) -> RichVRPProblem:
        # 1) check geom
        # 2) create fake deport
        # 3) move depots in jobs 'count' times
        # 4) create matrixes

        for idx in problem.matrix.geometries:
            geometry = problem.matrix.geometries[idx]

            if not isinstance(geometry, DistanceAndTimeMatrixGeometry):
                raise ValueError

        place_mapping = problem.matrix

        # where do you need to delete depot from and where to add as job
        # (except problem.depots, problem.jobs and matrixes)

        # change params
        # TODO: а что если 0 уже занят? В крайнем случаем можно сделать uuid, но лучше по-другому
        fake_depot = Depot(id=0, time_windows=[], lat=0, lon=0, delay=0)

        for idx in place_mapping.geometries:
            geometry = place_mapping.geometries[idx]

            # do something with places, points and mapping
            matrix = geometry.dist_matrix()
            t_matrix = geometry.time_matrix()

            inf = get_inf(matrix)
            t_inf = get_inf(t_matrix)

            n = len(matrix)

            new_size = n + 1 + count * 2

            new_matrix = np.zeros((new_size, new_size))
            new_matrix[:n, :n] = matrix

            new_t_matrix = np.zeros((new_size, new_size))
            new_t_matrix[:n, :n] = t_matrix

            # + fake + count * 2
            # - depots (there is a problem to rebuild whole matrix without depots points?)
            # save old data for depots and use in matrix for new jobs?
            ids = []
            for depot in problem.depots:
                # old index of depot
                index = place_mapping.mapping[depot]
                ids.append(index)
                # + count * 2
                new_jobs = []
                for k in range(count):
                    # create new job in and out
                    job_in = Job(id=depot.id, name=depot.name + '_in', lat=depot.lat, lon=depot.lon, x=depot.x,
                                 y=depot.y, time_windows=depot.time_windows, delay=depot.delay)
                    job_out = Job(id=depot.id, name=depot.name + '_out', lat=depot.lat, lon=depot.lon, x=depot.x,
                                  y=depot.y, time_windows=depot.time_windows, delay=depot.delay)
                    problem.jobs.append(job_in)
                    problem.jobs.append(job_out)

                    # copy depot table for this two
                    new_matrix[n + k, :n] = matrix[index, :n]
                    new_matrix[:n, n + k] = matrix[:n, index]
                    new_matrix[n + k + 1, :n] = matrix[index, :n]
                    new_matrix[:n, n + k + 1] = matrix[:n, index]

                    new_t_matrix[n + k, :n] = t_matrix[index, :n]
                    new_t_matrix[:n, n + k] = t_matrix[:n, index]
                    new_t_matrix[n + k + 1, :n] = t_matrix[index, :n]
                    new_t_matrix[:n, n + k + 1] = t_matrix[:n, index]

                    # 0 and inf for fake
                    # in
                    new_matrix[n + k, -1] = 0
                    new_matrix[-1, n + k] = inf
                    # out
                    new_matrix[n + k + 1, -1] = inf
                    new_matrix[-1, n + k + 1] = 0

                    # in
                    new_t_matrix[n + k, -1] = 0
                    new_t_matrix[-1, n + k] = inf
                    # out
                    new_t_matrix[n + k + 1, -1] = inf
                    new_t_matrix[-1, n + k + 1] = 0

                    # just for updating points in geometry
                    new_jobs.append(job_in)
                    new_jobs.append(job_out)
                # - depots
                new_matrix[index, :] = inf
                new_matrix[:, index] = inf
                new_t_matrix[index, :] = t_inf
                new_t_matrix[:, index] = t_inf

            #  old | new | fake
            #  new | >x< |  01
            #  fake|  10 |  0
            for i in range(len(ids)):
                for indx in range(len(ids)):
                    # square of inf for new_jobs (moves between them)
                    # make inf between in and out
                    if i == indx:
                        new_matrix[n + i, n + i] = inf
                        new_matrix[n + i + 1, n + i + 1] = inf

                        new_t_matrix[n + i, n + i] = t_inf
                        new_t_matrix[n + i + 1, n + i + 1] = t_inf
                    else:
                        new_matrix[n + i, n + i + indx] = new_matrix[n + i, ids[indx]]
                        new_matrix[n + i + 1, ids[i]] = new_matrix[n + i + 1, ids[indx]]
                        new_matrix[n + i + indx, n + i] = new_matrix[ids[indx], n + i]
                        new_matrix[ids[i], n + i + 1] = new_matrix[ids[indx], n + i + 1]

                        new_t_matrix[n + i, n + i + indx] = new_t_matrix[n + i, ids[indx]]
                        new_t_matrix[n + i + 1, ids[i]] = new_t_matrix[n + i + 1, ids[indx]]
                        new_t_matrix[n + i + indx, n + i] = new_t_matrix[ids[indx], n + i]
                        new_t_matrix[ids[i], n + i + 1] = new_t_matrix[ids[indx], n + i + 1]
            # add fake

        # TODO :: update points and mapping
        ###

        # add all fakes in problem.depots or only one?
        # Are all geometry.places the same ?
        problem.depots = [fake_depot]
        return problem

    @staticmethod
    def restore(self, solution: VRPSolution) -> VRPSolution:
        new_problem = solution.problem
        new_routes = solution.routes
        return VRPSolution(new_problem, new_routes)

# TODO :: Проверить трансформацию на ошибки
