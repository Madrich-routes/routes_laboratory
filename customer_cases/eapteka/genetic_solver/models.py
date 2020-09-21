from dataclasses import dataclass
from typing import List, Tuple, Dict, Union

Point = Tuple[float, float]
Location = Union[int, Point]


@dataclass
class Task:
    location: int  # id in matrix
    time_windows: List[Tuple[str, str]]  # временные окна
    delay: float  # время обслуживания на точке
    value: List[int]  # объем груза напр. [вес, объем]
    priority: int  # 1 - высший приоритет


@dataclass
class Depot:
    name_id: str  # можно название
    location: int  # id in matrix
    reload: float
    load: float


@dataclass
class Courier:
    type_id: str  # как в примере
    profile: str  # что это такое курьер/водитель (пешком/на машине)
    name: str  # индетификатор (название какое-нибудь, можно имя)
    costs: Dict[str, float]  # на сколько дорого обходится использования средства (fixed, time, distance)
    time_windows: List[Tuple[str, str]]  # временные окна
    priority: int  # 1 - высший приоритет
    value: List[int]  # вместимость
    start: int  # точка начала, что брать - хз
    end: int  # точка конца, что брать - хз
