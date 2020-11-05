import numpy as np
from more_itertools import windowed

from algorithms.metaheuristics.genetic.models import BaseIndividual
from temp.tsp import List


def sort_nondominated(
    population: List[BaseIndividual],
    k: int,
    first_front_only=False,
):
    if k == 0:
        return []


def crowding_distance(
    population: List[BaseIndividual]
) -> None:
    """
    Считаем crowding расстояние — мера того, насколько много у нас похожих по метрикам решений.

    Parameters
    ----------
    population : Популяция с индивидами

    Returns
    -------
    None
    """
    n, n_obj = len(population), len(population[0].metrics)  # размер популяции и критериев

    for i in range(n_obj):
        population.sort(key=lambda x: x.metrics[i])
        norm = (population[-1].metrics[i] - population[0].metrics[i]) * n_obj

        # На концах бесконечности. Если в концах будет несколько точек, то бесконечность получит случайная.
        # Поэтому я поменял на инкремент, чтобы их тоже можно было сравнивать.
        population[-1].crowding_dist += n_obj
        population[0].crowding_dist += n_obj

        # Нужно ли присваивать бесконечности, если норма 0?
        if norm == 0:
            continue

        # Смотрим, насколько близки его соседи.
        for p, current, n in windowed(population, 3):
            increment = n.metrics[i] - p.metrics[i]
            current.crowding_dist += increment / norm
