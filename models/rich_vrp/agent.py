from dataclasses import dataclass
from typing import List, Tuple

from models.rich_vrp.agent_type import AgentType
from models.rich_vrp.costs import AgentCosts


@dataclass
class Agent:
    """
    Агент, который может перемещаться и выполнять задачи
    """
    id: int

    costs: AgentCosts  # на сколько дорого обходится использования средства (fixed, time, distance)
    value: List[int]  # вместимость (можно inf, ну или очень много)

    time_windows: List[Tuple[int, int]]

    start_place: int  # стартовая точка
    end_place: int  # конечная точка прибытия

    type: AgentType = None  # тип этого конкретного агента
    name: str = ""
