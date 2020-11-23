from dataclasses import dataclass, field
from typing import List, Optional

import numpy as np

from models.rich_vrp import Place, Depot


@dataclass
class Job(Place):
    """Класс для описания работы, которую необходимо проделать агенту.

    Это самый общий класс. В него добавляются любые характеристики.
    """
    capacity_constraints: Optional[np.array] = None  # количество разгрузки в точке (той же размерности, что capacities)
    required_skills: List[str] = field(default_factory=list)  # какой набор скиллов тут будет необходим

    price: int = 0  # награда, получаемая за выполнение этой работы
    priority: int = 0  # приоритет выполнения этой работы

    depots: Optional[List[Depot]] = None

    def __le__(self, other):
        return self.id < other.id

    def __hash__(self):
        return hash(self.descriptor)
