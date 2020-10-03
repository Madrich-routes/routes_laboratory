import random
from typing import List

import numpy as np


class BaseIndividual:
    """
    Класс для примера. Что-то, у чего есть fitness
    """
    def __init__(self, fitness: float):
        self.fitness = fitness  # type: float


def tournament_selection(
        population: List[BaseIndividual],
        desired_size: int,  # сколько мы хотим отобрать
):
    """
    По двое выбираем из популяции. Худшего выкидываем.
    """
    n = len(population)
    while len(population) > desired_size:
        i, j = random.sample(range(n), 2)

        if population[i].fitness > population[j].fitness:
            del population[j]
        else:
            del population[i]

    return population


def truncate_extinction(
        population: List[BaseIndividual],
        truncated_frac: float = 0.5
):
    """
    Очень тупой и очень быстрый оператор вымирания.
    Просто выкидываем худшую часть популяции.
    :param population:
    :param truncated_frac:
    :return:
    """
    return sorted(population, key=lambda x: x.fitness)[:len(population) * (1 - truncated_frac)]


def fitness_proportionate_replication(
        population: List[BaseIndividual],
):
    """
    Roulette wheel
    Отбираем двух родителей пропорционально значению их fitness.
    :param population:
    :return:
    """
    fitnesses = np.array([i.fitness for i in population])
    probas = fitnesses / fitnesses.sum()

    parents = random.choices(range(len(population)), weights=probas, k=2)

    return parents
