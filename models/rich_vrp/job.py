from dataclasses import dataclass, field
from functools import cached_property, reduce
from typing import Set, List, Optional, Tuple

import numpy as np


@dataclass
class Place:
    id: int  # Просто какой-то уникальный id. Индекс в матрице хранят другие классы.  # TODO: а оно нам нужно? uuid?

    lat: Optional[float] = None
    lon: Optional[float] = None

    x: Optional[int] = None
    y: Optional[int] = None


@dataclass
class Job(Place):
    """
    Класс для описания работы, которую необходимо проделать агенту.
    Это самый общий класс. В него добавляются любые характеристики.
    """
    time_windows: List[Tuple[int, int]] = field(default_factory=list)

    delay: int = 0  # время обслуживания на точке
    amounts: np.ndarray = None  # количество разгрузки в точке (той же размерности, что capacities)

    required_skills: Set[int] = field(default_factory=set)  # какой набор скилов тут будет необходим

    price: int = 0  # награда, получаемая за выполнение этой работы
    priority: int = 0

    def __le__(self, other):
        return self.id < other.id


class CompositeJob(Job):
    """
    Job, который представляет из себ объединение нескольких других джобов.
    Позволяет склеивать джобы, которые гарантированно нужны вместе.
    """

    def __init__(self, jobs: List[Job]):
        self.jobs = jobs[:]

    @cached_property
    def id(self):
        return tuple(c.id for c in self.containers)

    @cached_property
    def tw_start(self):
        ...  # TODO:

    @cached_property
    def tw_end(self):
        ...  # TODO:

    @cached_property
    def delay(self):
        ...  # TODO

    @cached_property
    def amounts(self):
        """
        Общая цена всех заказов в списке
        """
        return sum(c.amounts for c in self.containers)

    @cached_property
    def required_skills(self):
        """
        Объединение required скилов от всех пацанов
        """
        return list(reduce(lambda x, y: x.required_skills | y.required_skills, self.containers, set()))

    @cached_property
    def price(self):
        """
        Общая цена всех заказов в списке
        """
        return sum(c.price for c in self.containers)
