from dataclasses import dataclass
from typing import Dict, List


@dataclass
class Agent:
    costs: Dict[str, float]  # на сколько дорого обходится использования средства (fixed, time, distance)
    value: List[int]  # вместимость (можно inf, ну или очень много)
    start_time: str  # время начала работы
    end_time: str  # время конца работы

    start_place: int  # стартовая точка
    end_place: int  # конечная точка прибытия
