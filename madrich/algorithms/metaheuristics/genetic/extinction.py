"""Здесь описаны методы, по которым происходит вымирание поколения.

Это чистое вымирание без детей и так далее.
"""
import random

from madrich.algorithms.metaheuristics.genetic.models import BaseIndividual
from madrich.temp.tsp import List


# TODO: бенчмарки: рандомные. Сделать хорошие композитные операторы с элитизмом


def tournament_extinction(
    population: List[BaseIndividual],
    desired_size: int,
):
    """Особи встречаются группами и выживает только сильнейший. Размер группы: 2.

    Parameters
    ----------
    population :
    desired_size :

    Returns
    -------
    Выжившая часть популяции
    """
    n = len(population)
    while len(population) > desired_size:
        i, j = random.sample(range(n), 2)

        if population[i].fitness > population[j].fitness:
            del population[j]
        else:
            del population[i]

    return population
