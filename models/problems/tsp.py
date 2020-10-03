import numpy as np

from models.problems.base import BaseRoutingProblem


class TSPProblem(BaseRoutingProblem):
    def __init__(self, matrix: np.ndarray):
        super().__init__(matrix)

    def lkh_par(self):
        res = ''
        res += 'TYPE: TSP'
        res += 'NAME: tsp'
        res += 'COMMENT: tsp'
        res += f'DIMENSION: {len(self.matrix)}'
        return res

    def lkh_problem(self) -> str:
        res = ''
        res += ''

    def is_multi_depot(self) -> bool:
        return False
