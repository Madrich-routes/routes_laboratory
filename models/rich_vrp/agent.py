"""Агент — модель для курьера, машины и чего угодно, что может двигать и выполнять джобы.
В этом модуле класс агента и все, что к нему относится
 """
from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, List, Optional, Set, Tuple

if TYPE_CHECKING:
    from models.rich_vrp import Depot, Place
    from models.rich_vrp.agent_type import AgentType
    from models.rich_vrp.costs import AgentCosts


@dataclass
class Agent:
    """Агент, который может перемещаться и выполнять задачи.

    Args:
    id : Любой числовой уникальный id
    costs : Список стоимостей разных действий агента
    amounts : Список ограничение вместимости агента
    time_windows : Набор интервалов работы
    compatible_depots : Список депо, которыми можно пользоваться

    start_place : Начальная точка агента
    end_place : Конечная точка агента

    type : Тип этого агента
    priority : Приоритет этого агента при назначении

    name : Читаемое имя этого агента
    """
    id: int

    costs: AgentCosts
    amounts: List[int]

    time_windows: List[Tuple[int, int]]
    compatible_depots: Set[Depot]

    start_place: Optional[Place]
    end_place: Optional[Place]

    type: AgentType = None
    priority: int = 0

    name: str = ""
    # TODO:: здесь заглушка
    def __post_init__(self):
        if self.start_place is None:
            # if len(self.compatible_depots) > 1:
            #     print(len(self.compatible_depots))
            #     raise Exception
            # else:
            #     self.start_place = self.compatible_depots[0]
            #     self.end_place = self.compatible_depots[0]
            self.start_place = next(iter(self.compatible_depots))
            self.end_place = next(iter(self.compatible_depots))
