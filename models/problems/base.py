import uuid
from abc import ABC

import numpy as np


class BaseRoutingProblem:
    def __init__(self, matrix: np.ndarray):
        self.matrix = matrix
        self.uuid = uuid.uuid4()

    @property
    def size(self) -> int:
        return len(self.matrix)

    def __str__(self) -> str:
        return str(self.matrix)

    def __repr__(self) -> str:
        return str(self.matrix)

    # ---------------------------------- Характеристики проблемы (а они нам нужны?) ---------------------------
    #
    # def is_multi_depot(self) -> bool:
    #     raise NotImplementedError


class RustSolvable(BaseRoutingProblem, ABC):
    def pragmatic(self) -> str:
        """
        Сформулировать проблему pragmatic-формате
        TODO: мб это все должно быть в классах солверов? Чем в каждую проблему пихать?
        """
        raise NotImplementedError


class LKHSolvable(BaseRoutingProblem, ABC):
    def lkh_problem(self) -> str:
        """
        Сформировать файл проблемы для LKH-решалки
        """
        raise NotImplementedError

    def lkh_par(self) -> str:
        """
        Сформировать параметры для файла параметров lkh
        """
        raise NotImplementedError


class WithDelays(BaseRoutingProblem, ABC):
    @property
    def delays(self) -> np.ndarray:
        raise NotImplementedError
