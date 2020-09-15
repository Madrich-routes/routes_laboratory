"""
TODO: забрать решалку из моего репозитория и оформить
"""
from formats.tsplib import dumps_matrix
from models.problems.base import BaseRoutingProblem
import numpy as np


class MTSPProblem(BaseRoutingProblem):
    def __init__(
            self,
            matrix: np.ndarray,
            m: int
    ):
        """
        TODO: вероятно, она лучше решитсяс помощью LKH2 а не 3
        """
        super().__init__(matrix)
        self.m = m

    def lkh_problem(self) -> str:
        # TODO: тут нужно что-то добавить
        return dumps_matrix(self.matrix)

    def lkh_par(self) -> str:
        par = ''
        par += f'VEHICLES = {self.m}\n'
        par += f'MTSP_OBJECTIVE = MINMAX\n'  # TODO: передавать как параметр
        par += f'DEPOT = 1\n'
        par += f'INITIAL_TOUR_ALGORITHM = MTSP\n'  # TODO: WALK? OTHER?

        return par

    def pragmatic(self) -> str:
        # TODO: добавить формулировку
        raise NotImplementedError

    def is_multi_depot(self) -> bool:
        return False
