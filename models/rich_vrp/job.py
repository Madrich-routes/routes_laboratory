from dataclasses import dataclass
from functools import cached_property, reduce
from typing import Set, List

import numpy as np


@dataclass
class Job:
    """
    Класс для описания работы, которую необходимо проделать агенту.
    Это самый общий класс. В него добавляются любые характеристики.
    """
    id: int  # Просто какой-то уникальный id. Индекс в матрице хранят другие классы.  # TODO: а оно нам нужно? uuid?

    tw_start: int  # временные окна  # TODO: что задавать, если окна не заданы?
    tw_end: int  # временные окна

    delay: int  # время обслуживания на точке
    amounts: np.ndarray  # количество разгрузки в точке (той же размерности, что capacities)

    required_skills: Set[int]  # какой набор скилов тут будет необходим

    price: int = 0  # награда, получаемая за выполнение этой работы

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
