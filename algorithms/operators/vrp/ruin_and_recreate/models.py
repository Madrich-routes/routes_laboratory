import random
from dataclasses import dataclass
from typing import List

from utils.types import Array


@dataclass
class Customer:
    tw_start: int
    tw_end: int
    demand: int

@dataclass
class VRPSolution:
    matrix: Array

    tours: List[List[Customer]]

    capacity_slacks: List[int]
    time_slacks: List[int]

    capacity: int

    unassigned: List[Customer]

    def recreate(
            self,
            sort='no',
            gamma: float = 0.85,  # вероятность моргания
            shuffle_tours: bool = False,  # перемешивать ли туры или испольщовать как есть
    ):
        if shuffle_tours:
            random.shuffle(self.tours)

        for c in self.unassigned:
            gain = float('-inf')
