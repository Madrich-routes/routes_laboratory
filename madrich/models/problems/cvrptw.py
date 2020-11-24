from typing import List, Tuple

import numpy as np

from madrich.formats import tsplib
from madrich.models.problems.base import BaseRoutingProblem


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
            depot: int = 1,
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
        # f'DISTANCE = {self.max_len}',
        # f'CAPACITY = {self.vehicles_capacity}',
        # f'DEPOT = {self.depot}',
        return '\n'.join([
            f'VEHICLES = {self.vehicles}',
            f'MTSP_MAX_SIZE = {self.max_hops}',
            r'INITIAL_TOUR_ALGORITHM = WALK',
            r'MTSP_MIN_SIZE = 1',
        ])

    def lkh_problem(self):
        return '\n'.join([
            f'NAME: CVRPTW-{str(self.uuid)}',
            r'TYPE: CVRPTW',
            f'DIMENSION: {len(self.matrix)}',
            f'VEHICLES: {self.vehicles}',
            f'CAPACITY: {self.vehicles_capacity}',
            f'DISTANCE: {self.max_len}',
            tsplib.dumps_matrix(self.matrix),
            tsplib.dump_demands(self.demands),
            tsplib.dumps_time_windows(self.time_windows),
            f'DEPOT_SECTION',
            f"{self.depot}",
            f"-1",
            f"EOF",
        ])

    def pragmatic(self):
        raise NotImplementedError
