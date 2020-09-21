from dataclasses import dataclass
from typing import Dict, List

from models.rich_vrp.agent_type import AgentType


@dataclass
class Agent:
    """
    Агент, который может перемещаться и выполнять задачи
    """

    costs: Dict[str, float]  # на сколько дорого обходится использования средства (fixed, time, distance)
    value: List[int]  # вместимость (можно inf, ну или очень много)
    start_time: str  # время начала работы
    end_time: str  # время конца работы

    start_place: int  # стартовая точка
    end_place: int  # конечная точка прибытия

    type: AgentType = None  # тип этого конкретного агента.
