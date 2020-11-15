from dataclasses import dataclass, field
from functools import cached_property, reduce
from typing import List, Optional, Set, Iterable, TYPE_CHECKING

from models.rich_vrp import Place
from utils.types import Array

if TYPE_CHECKING:
    from models.rich_vrp import Depot


@dataclass(unsafe_hash=True)
class Job(Place):
    """Класс для описания работы, которую необходимо проделать агенту.

    Это самый общий класс. В него добавляются любые характеристики.
    """
    amounts: Optional[Array] = None  # количество разгрузки в точке (той же размерности, что capacities)
    required_skills: Set[int] = field(default_factory=set)  # какой набор скилов тут будет необходим

    price: int = 0  # награда, получаемая за выполнение этой работы
    priority: int = 0  # приоритет выполнения этой работы

    depots: Optional[List['Depot']] = None

    def __post_init__(self):
        self.required_skills = frozenset(self.required_skills)
        self.depots = tuple(self.depots) if self.depots is not None else None

    def __le__(self, other):
        return self.id < other.id


class CompositeJob(Job):
    """Job, который представляет из себ объединение нескольких других джобов.

    Позволяет склеивать джобы, которые гарантированно нужны вместе.
    """

    def __init__(
        self,
        jobs: Iterable[Job]
    ):
        self.jobs = list(jobs)

    @cached_property
    def id(self):
        return tuple(c.id for c in self.jobs)

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
        """Общая цена всех заказов в списке."""
        return sum(c.amounts for c in self.jobs)

    @cached_property
    def required_skills(self):
        """Объединение required скилов от всех пацанов."""
        return list(reduce(lambda x, y: x.required_skills | y.required_skills, self.jobs, set()))

    @cached_property
    def price(self):
        """Общая цена всех заказов в списке."""
        return sum(c.price for c in self.jobs)
