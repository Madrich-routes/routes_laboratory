"""
Агент — модель для курьера, машины и чего угодно, что может двигать и выполнять джобы.
В этом модуле класс агента и все, что к нему относится
"""
from dataclasses import dataclass
from typing import Dict

from typing import List, Optional, Set, Tuple

from models.rich_vrp.depot import Depot
from models.rich_vrp.place import Place


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
    name: str

    costs: Dict[str, float]
    capacity_constraints: List[int]

    time_windows: List[Tuple[int, int]]
    compatible_depots: Set[Depot]
    start_place: Optional[Place]
    end_place: Optional[Place]

    profile: str
    skills: List[str]
