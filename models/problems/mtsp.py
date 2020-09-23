import numpy as np

from formats import tsplib
from models.problems.base import BaseRoutingProblem


class MTSPProblem(BaseRoutingProblem):
    def __init__(
            self,
            matrix: np.ndarray,
            vehicles: int,
            depot: int = 1,
            objective: str = 'MINSUM',
            max_size: int = 10 ** 5,
            min_size: int = 1,
    ):
        """
        objective = MINMAX | MINMAX_SIZE | MINSUM
        INITIAL_TOUR_ALGORITHM = MTSP — нужно передать в солвер
        """
        super().__init__(matrix)

        self.vehicles = vehicles
        self.depot = depot
        self.max_size = max_size
        self.min_size = min_size
        self.objective = objective

    def lkh_problem(self) -> str:
        return '\n'.join([
            f'NAME: MTSP-{str(self.uuid)}',
            r'TYPE: MTSP',
            f'DIMENSION: {len(self.matrix)}',
            f'VEHICLES: {self.vehicles}',
            tsplib.dumps_matrix(self.matrix),
            f'DEPOT_SECTION',
            f"{self.depot}",
            f"-1",
            f"EOF",
        ])

    def lkh_par(self) -> str:
        return '\n'.join([
            f'VEHICLES = {self.vehicles}',
            f'DEPOT = {self.depot}',
            f'MTSP_OBJECTIVE = {self.objective}',
            f'MTSP_MIN_SIZE = {self.min_size}',
            f'MTSP_MAX_SIZE = {self.max_size}',
        ])

    def pragmatic(self) -> str:
        # TODO: добавить формулировку
        raise NotImplementedError
