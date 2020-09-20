from dataclasses import dataclass
from typing import Tuple, List, Dict, Optional
import numpy as np

Point = Tuple[float, float]


@dataclass
class Task:
    id: int  # индекс в матрице
    tw_start: str  # временные окна
    tw_end: str  # временные окна
    delay: float  # время обслуживания на точке


@dataclass
class Vehicle:
    costs: Dict[str, float]  # на сколько дорого обходится использования средства (fixed, time, distance)
    value: List[int]  # вместимость (можно inf, ну или очень много)
    start_time: str  # время начала работы
    end_time: str  # время конца работы

    start_place: int  # стартовая точка
    end_place: int  # конечная точка прибытия


class DistanceMatrix:
    def __init__(
            self,
            dist_matrix: np.ndarray,
            time_matrix: np.ndarray = None,
            speed: float = None,
    ):
        self.dist_matrix = dist_matrix
        self._time_matrix = time_matrix
        self.speed = speed

    @property
    def time_matrix(self):
        if self._time_matrix is not None:
            return self._time_matrix
        else:
            return (self.dist_matrix / self.speed).astype('int')


@dataclass
class Tour:
    vehicle_id: str
    type_id: str
    statistic: dict
    stops: List[dict]


@dataclass
class Solution:
    statistic: dict
    tours: List[Tour]
    unassigned: Optional[dict]
