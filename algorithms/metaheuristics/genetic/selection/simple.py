"""
Просто разные полезные способы выбрать индивидов из поколения
"""
import random
from typing import List, Callable

import numpy as np
from scipy.optimize import basinhopping

from algorithms.metaheuristics.genetic.models import BaseIndividual
from utils.types import Array


# Тупые методы

def select_random(
    population: List[BaseIndividual],
    k: int,
    with_replacements: bool = False,
) -> List[BaseIndividual]:
    """
    Выбираем рандомных
    """
    if with_replacements:
        return random.choices(population, k=k)
    else:
        return random.sample(population, k=k)


def select_worst(
    population: List[BaseIndividual],
    k: int,
) -> List[BaseIndividual]:
    """
    Выбираем худших
    """
    return sorted(population, key=lambda x: x.fitness)[:k]


def select_best(
    population: List[BaseIndividual],
    k: int,
) -> List[BaseIndividual]:
    """
    Выбираем лучших
    """
    return sorted(population, key=lambda x: x.fitness, reverse=True)[:k]


#  Отбираем по фитнесам

def fitness_proportionate_roulette(
    population: List[BaseIndividual],
    k: int,
    key: Callable[['BaseIndividual'], float]
) -> List[BaseIndividual]:
    population.sort(key=key, reverse=True)
    probas = normalize_fitnesses([i.fitness for i in population])

    return random.choices(population, weights=probas, k=k)


def stochastic_universal_sampling(
    population: List[BaseIndividual],
    k: int,
    key: Callable[['BaseIndividual'], float],
) -> List[BaseIndividual]:
    """
    Двигаемся равномерными шагами через распределение вероятностей.
    """
    population.sort(key=key)
    probability = normalize_fitnesses([key(i) for i in population])  # Нормализуем фитнесы
    points = (np.arange(k) + random.random()) * (probability.sum() / k)  # Рандомные шаги

    indices = np.searchsorted(probability.cumsum(), points)  # Получаем точки

    return np.array(population)[indices].tolist()


# Отбираем по рангам (используем только > <)

def select_tournament(
    population: List[BaseIndividual],
    k: int,
    group_size: int,
) -> List[BaseIndividual]:
    """
    Турнир группками.
    """
    chosen = []
    for _ in range(k):
        aspirants = select_random(population=population, k=group_size, with_replacements=False)
        chosen += [max(aspirants, key=lambda x: x.fitness)]

    return chosen

basinhopping()


def select_probability_tournament(
    population: List[BaseIndividual], k: int, prob: float, key: Callable[[BaseIndividual], float]
) -> List[BaseIndividual]:
    """
    Выбираем в турнире лучшего с некоторой вероятностью.
    (Можно брать турнир из большего количества)
    """
    chosen = []

    for _ in range(k):
        x, y = sorted(select_random(population, k=2, with_replacements=False), key=key)
        prob = 0.5 if key(x) == key(y) else prob
        chosen += [x if random.random() < prob else y]

    return chosen


# -----------------------------------------ы--- helper functions ----------------------------------------------------


def normalize_fitnesses(
    fitnesses: Array,
    equality_factor: float = 0.05,
) -> Array:
    """
    Нормализуем массив фитнесов так, чтобы можно было семлить из популяции.
    После применения этой функции гарантируется, что все значения будут неотрицательными и суммироваться в 1.
    При equality_factor -> -1, мы будем выбирать только самых лучших, при -> inf будем выбирать равномерно.

    Parameters
    ----------
    fitnesses : Массив фитенсов
    equality_factor : Число, которое определяет степень элитизма. Разумные значения (-1, 10].

    Returns
    -------
    Нормализованный массив
    """
    assert -1 < equality_factor <= 10

    fitnesses = np.array(fitnesses)
    fitnesses -= fitnesses.min()  # Все стали положительными, а наименьший 0
    fitnesses += equality_factor * fitnesses.max()  # Увеличиваем или уменьшаем равномерность
    fitnesses.clip(0, out=fitnesses)  # Откидываем тех, кто стал отрицательным
    fitnesses /= fitnesses.sum()  # Гарантируем, что суммируемся в 1

    return fitnesses
