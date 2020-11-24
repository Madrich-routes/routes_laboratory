import random
from typing import List

import numpy as np

from madrich.algorithms.metaheuristics.genetic.models import BaseIndividual


def tournament_selection(
    population: List[BaseIndividual],
    desired_size: int,  # сколько мы хотим отобрать
):
    """По двое выбираем из популяции.

    Худшего выкидываем.
    """
    n = len(population)
    while len(population) > desired_size:
        i, j = random.sample(range(n), 2)

        if population[i].fitness > population[j].fitness:
            del population[j]
        else:
            del population[i]

    return population


def fitness_proportionate_replication(
    population: List[BaseIndividual],
):
    """Roulette wheel Отбираем двух родителей пропорционально значению их fitness.

    :param population:
    :return:
    """
    fitnesses = np.array([i.fitness for i in population])
    probas = fitnesses / fitnesses.sum()

    return random.choices(range(len(population)), weights=probas, k=2)
