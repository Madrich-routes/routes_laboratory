from dataclasses import dataclass
from typing import Optional, List, Dict

import numpy as np

from madrich.problems.models import State, Matrix, Point, Window, Cost

array = np.ndarray


@dataclass
class Storage:
    name: str  # адрес или название; unique
    load: int  # перегрузка\загрузка
    skills: List[str]  # требуемые навыки
    location: Point   # расположение
    work_time: Window  # время работы


@dataclass
class Job:
    job_id: str  # unique
    delay: int  # время на передачу
    value: array  # физические размеры; [1, 2, 3, ...]
    skills: List[str]  # требуемые умения
    location: Point  # расположение
    time_windows: List[Window]  # временные окна доставки


@dataclass
class Courier:
    name: str  # имя; unique
    profile: str  # профиль матрицы
    cost: Cost  # стоимость работы
    value: array  # физические размеры; [1, 2, 3, ...]
    skills: List[str]  # навыки
    max_distance: int   # максимальная дистанция за смену
    work_time: Window  # время работы
    start_location: Point  # место начала работы
    end_location: Point  # место окончания работы


@dataclass
class Route:
    storage: Storage
    courier: Courier
    matrix: Matrix
    start_time: int
    jobs: List[Job]
    travel_time: int
    distance: int
    cost: float

    def save_state(self, state: State) -> None:
        self.travel_time += state.travel_time
        self.cost += state.cost
        self.distance += state.distance

    def new_route(self, jobs: List[Job]) -> 'Route':
        return Route(self.storage, self.courier, self.matrix, self.start_time, jobs, -1, -1, -1.)

    def __len__(self):
        return len(self.jobs)


@dataclass
class Tour:
    storage: Storage
    routes: List[Route]
    unassigned_jobs: List[Job]

    def get_state(self) -> State:
        cost, travel_time, distance = 0., 0, 0
        for route in self.routes:
            cost += route.cost
            travel_time += route.travel_time
            distance += route.distance
        return State(travel_time, distance, cost, None)

    def len_jobs(self) -> int:
        s = 0
        for route in self.routes:
            s += len(route)
        s += len(self.unassigned_jobs)
        return s

    def __len__(self):
        return len(self.routes)


class Problem:

    @staticmethod
    def init(storage: Storage, jobs: List[Job], couriers: List[Courier], matrices: Dict[str, Matrix]) -> Tour:
        pass

    @staticmethod
    def get_state(route: Route) -> Optional[State]:
        pass
