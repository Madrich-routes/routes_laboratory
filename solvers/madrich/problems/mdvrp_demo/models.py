from dataclasses import dataclass, field
from typing import List, Optional, Dict

import numpy as np

from madrich.problems.models import Window, Cost, Matrix, State, Point

array = np.ndarray


@dataclass
class Job:
    job_id: str  # unique
    delay: int  # время на передачу
    value: array  # физические размеры; [1, 2, 3, ...]
    skills: List[str]  # требуемые умения
    location: Point  # расположение
    time_windows: List[Window]  # временные окна доставки

    def __repr__(self):
        return f'Job id: {self.job_id}, window: {self.time_windows}, location: {self.location}'


@dataclass
class Storage:
    name: str  # адрес или название; unique
    load: int  # перегрузка\загрузка
    skills: List[str]  # требуемые навыки
    location: Point  # расположение
    work_time: Window  # время работы
    assigned_jobs: List[Job]  # распределенные задачи
    unassigned_jobs: List[Job]  # нераспределенные задачи

    def __repr__(self):
        return f'Storage: {self.name}, location: {self.location}'


@dataclass
class Courier:
    name: str  # имя; unique
    profile: str  # профиль матрицы
    cost: Cost  # стоимость работы
    value: array  # физические размеры; [1, 2, 3, ...]
    skills: List[str]  # навыки
    max_distance: int  # максимальная дистанция за смену
    work_time: Window  # время работы
    start_location: Point  # место начала работы
    end_location: Point  # место окончания работы
    storages: List[Storage]  # которые он может посетить

    def __repr__(self):
        return f'Courier, name: {self.name}, profile: {self.profile}'


@dataclass
class Track:
    storage: Storage  # к какому складу привязан
    jobs: List[Job] = field(default_factory=list)  # заказы, заказы только из определенного склада

    def __len__(self):
        return len(self.jobs)

    def __repr__(self):
        return f'Track; storage: {self.storage.name}, jobs: {len(self.jobs)}'


@dataclass
class Route:
    courier: Courier  # курьер
    matrix: Matrix  # матрица расстояний\времени
    start_time: int  # время выезда курьера
    state: State = field(default_factory=State.empty)  # мера тура
    tracks: List[Track] = field(default_factory=list)  # все подмаршруты
    vec: int = 2  # длина вектора груза

    def get_state(self) -> State:
        return self.state

    def __len__(self):
        return sum([len(track.jobs) for track in self.tracks])

    def __repr__(self):
        return f'Route, courier: {self.courier.name}, tracks: {len(self.tracks)}, state: {self.state}'


@dataclass
class Tour:
    storages: List[Storage]  # склады
    routes: List[Route] = field(default_factory=list)  # все маршруты

    def get_state(self) -> State:
        state = State.empty()
        for route in self.routes:
            state += route.state
        return state

    def __len__(self):
        return len(self.routes)

    def __repr__(self):
        return f'Tour: {self.get_state()}, routes: {len(self.routes)}, storages: {len(self.storages)}'


class Problem:

    @staticmethod
    def init(vec: int, storages: List[Storage], couriers: List[Courier], matrices: Dict[str, Matrix]) -> Tour:
        pass

    @staticmethod
    def get_state(route: Route) -> Optional[State]:
        pass

    @staticmethod
    def get_state_track(track: Track, route: Route) -> Optional[State]:
        pass
