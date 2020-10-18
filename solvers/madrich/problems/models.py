from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Tuple

import numpy as np

array = np.ndarray


@dataclass
class Window:
    window: Tuple[int, int]

    def __init__(self, window: Tuple[str, str]):
        self.window = self.__to_sec(window[0]), self.__to_sec(window[1])

    @staticmethod
    def __to_sec(t: str) -> int:
        return int(datetime.strptime(t, '%Y-%m-%dT%H:%M:%SZ').timestamp())

    @staticmethod
    def __to_str(t: int) -> str:
        return datetime.fromtimestamp(t).strftime('%Y-%m-%dT%H:%M:%SZ')

    def __repr__(self):
        return f'{self.__to_str(self.window[0]), self.__to_str(self.window[1])}'


@dataclass
class Point:
    matrix_id: Optional[int]
    point: Tuple[float, float]
    address: Optional[str] = None

    def __repr__(self):
        return f'Matrix_id: {self.matrix_id}, Geo: {self.point}'


@dataclass
class Cost:
    start: float
    second: float
    meter: float

    def __repr__(self):
        return f'For start: {self.start}, second: {self.second}, meter: {self.meter}'


@dataclass
class Matrix:
    profile: str
    distance: array  # [[0, 1, 2], [1, 0, 2], [2, 3, 0]]
    travel_time: array  # [[0, 1, 2], [1, 0, 2], [2, 3, 0]]

    def __repr__(self):
        return f'Profile: {self.profile}, shape: {self.distance.shape}'


@dataclass
class State:
    travel_time: int
    distance: int
    cost: float
    value: Optional[array] = None

    @staticmethod
    def __value(lt: 'State', rt: 'State') -> Optional[array]:
        if lt.value is None and rt.value is None:
            return None
        elif lt.value is not None and rt.value is None:
            return lt.value
        elif lt.value is None and rt.value is not None:
            return rt.value
        else:
            return lt.value + rt.value

    @staticmethod
    def empty():
        return State(0, 0, 0.)

    def __add__(self, other: 'State'):
        return State(self.travel_time + other.travel_time, self.distance + other.distance,
                     self.cost + other.cost, self.__value(self, other))

    def __iadd__(self, other: 'State'):
        self.travel_time += other.travel_time
        self.distance += other.distance
        self.cost += other.cost
        self.value = self.__value(self, other)
        return self

    def __lt__(self, other: 'State'):
        if not self.travel_time == other.travel_time:
            return self.travel_time < other.travel_time
        if not self.cost == other.cost:
            return self.cost < other.cost
        if not self.distance == other.distance:
            return self.distance < other.distance
        return False

    def __repr__(self):
        return f'Travel time: {self.travel_time}, Distance: {self.distance}, Cost: {self.cost:0.1f}'
