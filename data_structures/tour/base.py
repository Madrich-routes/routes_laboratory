import numpy as np

from models.rich_vrp.agent import Agent
# TODO: возможно, этот объект плохо спроектирован. Нет Single responsibility
from models.rich_vrp.geometries.base import BaseGeometry
from utils.algorithms import start_tw
from utils.data_formats import format_distance
from utils.iteration import sets_union


class Tour:
    """
    Круговой маршрут без повторов.
    Начинается и заканчивается в одной и той же точке.
    """

    def __init__(
            self,
            nodes: np.ndarray,
            matrix: BaseGeometry,
            agent: Agent,
    ):
        """
        Храним набор вершин, которые
        :param problem:
        :param nodes:
        """
        self.matrix = matrix
        self.nodes = nodes
        self.agent = agent

    def __str__(self):
        return (f"Tour(len={self.size}), "
                f"capacity={self.amounts():.2f}/{self.max_amounts():.1f}, path={self.distance():.1f}")

    @property
    def size(self):
        """
        Считаем длину маршрута в количестве точек
        """
        return len(self.nodes)

    def distance(self):
        """
        Общая длина тура
        """
        raise NotImplementedError

    def prev(self, a: int):
        raise NotImplementedError

    def next(self, a: int):
        raise NotImplementedError

    def between(self, a: int, b: int, c: int) -> bool:
        raise NotImplementedError

    def flip(self, a: int, b: int, c: int, d: int) -> None:
        raise NotImplementedError

    def edges(self):
        raise NotImplementedError

    # Характеристики тура

    def jobs_num(self):
        return len(self.nodes) - 1

    def jobs(self):
        # TODO:
        ...

    def points(self):
        ...
        # TODO:

    def max_amounts(self):
        # TODO
        ...
        # return self.agent.

    def amounts(self):
        ...

    def time(self):
        ...

    def time_from_depot_to_start(self):
        """

        """
        ...

    def time_from_finish_to_depot(self):
        """

        """
        ...

    def required_skills(self):
        """
        Набор всех необходимых скилов для порохождения этого тура
        """
        return sets_union(j.required_skills for j in self.jobs())

    # -------------------------------------- protected methods -------------------------------------------------

    def travel_times(self):
        return self.nodes

    def tw_list(self):
        ...

    # def time_window(self):
    #     return start_tw(time, travel_times=[])

    def stats(self):
        """
        Печатаем общую статистику тура
        """
        return (
                f'Ограничения: {self.amounts()}/{self.amounts()}, '
                f'{format_distance(self.distance(), with_name=True, with_units=True)}, '
                f'Скилы: {self.required_skills()}, Хопы {self.jobs_num()}, '
                f'Время в пути(с депо): {self.time() / 3600:.2f}'
                f'({self.time() / 3600:.2f})ч, '

                # f'Скорость: {self.agent.type.speed * 3.6:.2f}км/ч '

                + (
                    f'Окно: ({self.min_time() / 3600:.1f},{self.max_time() / 3600:.1f}), '
                    if self.min_time() + self.max_time() > 0 else ''
                )
        )
