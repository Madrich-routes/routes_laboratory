from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from madrich.models.rich_vrp.depot import Depot
from madrich.models.rich_vrp.place import Place


@dataclass
class Job(Place):
    """Класс для описания работы, которую необходимо проделать агенту.

    Это самый общий класс. В него добавляются любые характеристики.
    """
    capacity_constraints: Optional[List[int]] = None  # количество разгрузки в точке
    required_skills: List[str] = field(default_factory=list)  # какой набор скиллов тут будет необходим

    price: int = 0  # награда, получаемая за выполнение этой работы
    priority: int = 0  # приоритет выполнения этой работы

    depots: Optional[List[Depot]] = None

    def __le__(self, other):
        return self.id < other.id

    def __hash__(self):
        return hash(self.descriptor)
