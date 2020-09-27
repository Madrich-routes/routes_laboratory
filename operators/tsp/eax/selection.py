import random

from solvers.construction_heuristics.tsp import generate_initial_solution
from utils.types import Array


def initial_population(matrix: Array, n: int):
    return [generate_initial_solution(matrix) for i in range(n)]


def generate_children(a: Array, b: Array, n: int):
    """
    Генерируем нужное количество детей от родителей
    """
    raise NotImplementedError


def run_evolution(
        matrix: Array,
        np: int,  # размер популяции
        nch: int,  # количество детей от двух родителей
        max_populations: int,  # максимальное количество популяций
):
    population = initial_population(matrix, np)
    t = 0
    while True:
        random.shuffle(population)

        for i in range(np):
            a, b = population[i], population[(i + 1) % np]
            children = generate_children(a, b, nch)
            population[i] = max(children + [a], lambda x: x.fitenss)

        if t >= max_populations:
            break
        else:
            t += 1

    return max(population, lambda x: x.fitenss)
