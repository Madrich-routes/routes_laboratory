"""
В этом модуле находится каркас и описание базовой схемы работы алгоритма
Variable Neighbourhood Search.

Написано по мотивам этой работы:
https://sci-hub.st/https://www.sciencedirect.com/science/article/pii/S1572528610000289

A General VNS heuristic for the traveling salesman problem with time windows.

Здесь смотрим на примере TSPTW.
"""
from algorithms.construction_heuristics import tsp
from utils.types import Array


def initial_solution(
        matrix: Array,
        tw: Array
):
    return tsp.random_tour(matrix)


def infeasibility_score(
        tour: Array,
        matrix: Array,
        tw: Array,
):
    """
    Оценка, насколько бессовестно нарушаются ограничения в решении.
    """
    # TODO:
    ...



def one_shift_local_search(
        start_point: Array,
        matrix: Array,
        tw: Array,
):
    ...


def constructive_vns(
        matrix: Array,
        tw: Array,
        max_trials: int
):
    """
    VNS для нахождения начального валидного решения
    """

    while True:
        level = 1
        X = initial_solution()
