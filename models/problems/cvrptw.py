from dataclasses import dataclass
from typing import Tuple

import numpy as np

from formats.tsplib import dumps_matrix


@dataclass
class MTSPProblem(RoutingProblem):
    vehicles: int
    max_len: int

    def lkh_par(self) -> str:
        par = ''
        par += 'SPECIAL\n'
        par += f'VEHICLES = {self.vehicles}\n'
        par += f'DISTANCE = {self.max_len}\n'
        par += f'DEPOT = 1\n'
        par += f'INITIAL_TOUR_ALGORITHM = MTSP\n'
        par += f'MTSP_OBJECTIVE = MINMAX\n'

    def pragmatic(self):
        ...


@dataclass
class CVRPTWProblem(RoutingProblem):
    vehicles: int
    vehicles_capacity: int
    max_len: int
    max_hops: int

    time_windows: Tuple[Tuple[int, int], ...]

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
        res += r'NAME: CVRPTW',
        res += r'TYPE: CVRPTW',
        res += f'DIMENSION: {len(self.matrix)}'
        res += f'VEHICLES: {self.vehicles}'
        res += f'CAPACITY: {self.vehicles_capacity}'
        res += f'DISTANCE: {self.max_len}'
        res += dumps_matrix(self.matrix)
        res += 'TIME_WINDOW_SECTION'
        res += '\n'.join(
            ' '.join([i, w[0], w[1]]) for i, w in enumerate(self.time_windows)
        )
        res += 'DEPOT_SECTION\n'
        res += f"1"  # TODO: any depot
        res += f"-1"
        res += f"EOF\n",

        return res

    def pragmatic(self):
        ...
