from dataclasses import dataclass
from typing import Tuple, List

import numpy as np

from formats import tsplib
from models.problems.base import BaseRoutingProblem


# @dataclass
# class MTSPProblem(BaseRoutingProblem):
#     vehicles: int
#     max_len: int
#
#     def lkh_par(self) -> str:
#         par = ''
#         par += 'SPECIAL\n'
#         par += f'VEHICLES = {self.vehicles}\n'
#         par += f'DISTANCE = {self.max_len}\n'
#         par += f'DEPOT = 1\n'
#         par += f'INITIAL_TOUR_ALGORITHM = MTSP\n'
#         par += f'MTSP_OBJECTIVE = MINMAX\n'
#
#     def pragmatic(self):
#         ...


class CVRPTWProblem(BaseRoutingProblem):
    def __init__(
            self,
            matrix: np.ndarray,
            vehicles: int,
            vehicles_capacity: int,
            max_len: int,
            max_hops: int,
            demands: List[int],
            time_windows: List[Tuple[int, int]],
            depot: int = 0,
    ):
        super().__init__(matrix)
        self.vehicles = vehicles
        self.vehicles_capacity = vehicles_capacity
        self.max_len = max_len
        self.max_hops = max_hops
        self.demands = demands
        self.time_windows = time_windows
        self.depot = depot

    def lkh_par(self) -> str:
        par = ''
        par += 'SPECIAL\n'
        par += f'VEHICLES = {self.vehicles}\n'
        par += f'DISTANCE = {self.max_len}\n'
        par += f'CAPACITY = {self.vehicles_capacity}'
        par += f'MTSP_MAX_SIZE = {self.max_hops}'

        par += f'DEPOT = 1\n'
        par += f'INITIAL_TOUR_ALGORITHM = WALK\n'

        return par

    def lkh_problem(self):
        res = '\n'
        res += f'NAME: CVRPTW-{str(self.uuid)}',
        res += r'TYPE: CVRPTW',
        res += f'DIMENSION: {len(self.matrix)}'
        res += f'VEHICLES: {self.vehicles}'
        res += f'CAPACITY: {self.vehicles_capacity}'
        res += f'DISTANCE: {self.max_len}'
        res += tsplib.dumps_matrix(self.matrix)
        res += tsplib.dump_demands(self.demands)
        res += tsplib.dumps_time_windows(self.time_windows)
        res += f'DEPOT_SECTION\n'
        res += f"{self.depot}"
        res += f"-1"
        res += f"EOF\n",

        return res

    def pragmatic(self):
        raise NotImplementedError
