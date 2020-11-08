from dataclasses import dataclass
from typing import List

import numpy as np


@dataclass
class Customer:
    """Время указывается в секундах."""
    max_work_time: int
    tw_start: int
    tw_end: int

    # будем указывать по id
    start_loc: int
    end_loc: int


@dataclass
class Agent:
    # tw_start: int
    # tw_end: int

    def to_dict(self):
        return dict(
            type='car',
            # count=1234,
            value=[10, 10],
            # time_window_start='',

        )


class OMTSPTWProblem:
    """Open Multiple TSP With Time Windows."""

    def __init__(
            self,
            matrix: np.ndarray,
            points: List[int],
            vehicles: int,
            vehicles_start_points: List[int],
    ):
        self.matrix = matrix
        self.points = points
        self.vehicles = vehicles
        self.vehicles_start_points = vehicles_start_points

    def formulate_car(self, car_id: int):
        return dict(
            type='car',
            count='value',
            value='car_size',
            time_window_start='',
        )


class Formulator:
    def __init__(self):
        ...
