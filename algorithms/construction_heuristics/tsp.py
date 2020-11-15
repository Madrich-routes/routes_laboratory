import random
from itertools import combinations
from random import choice, randrange

import numexpr as ne
import numpy as np
from blist._blist import blist
from data_structures.unionfind import UnionFind
from scipy.sparse.csgraph._min_spanning_tree import minimum_spanning_tree

from utils.types import Array


# TODO: TSP, convex hull?
# TODO: Найти все жадные туры одновременно, вероятно, можно быстро. (За квадрат)

def random_tour(matrix: Array):
    """Случайный тур коммивояжера."""
    n = len(matrix)
    tour = np.arange(n)
    np.random.shuffle(tour)

    return tour


def sweep(points: Array):
    """Идем по кругу и в этом порядке берем точки."""
    t = np.arctan2(points[:, 0], points[:, 1])
    return np.argsort(t)


def walk(matrix: Array, candidates: Array, first: int = None):
    """Идем по ребрам-кандидатам до тех пор, пока можем.

    Если не можем, берем кратчайшее неиспользованное. Кандидаты — списки смежности
    """
    n = len(matrix)
    used = np.zeros(n, dtype=bool)
    res = np.zeros(n, dtype=np.int32)

    current = first if first is not None else randrange(n)
    for i in range(n):
        res[i] = current
        used[current] = True

        unused_candidates = [c for c in candidates[i] if not used[c]]
        if unused_candidates:  # если есть неиспользованные кандидаты — рандомно выбираем из них
            current = choice(unused_candidates)
        else:  # если кандидатов нет, берем ближайшего незанятого соседа
            current = (matrix[current] + np.iinfo(np.int32).max * used).argmin()

    return res


def tsp_nn(matrix: Array, first: int = None):
    """Тур, получаемый присоединением случайного соседа начиная с first.

    # TODO: можно сделать быстрее
    """
    n = len(matrix)
    used = np.zeros(n, dtype=bool)
    res = np.zeros(n, dtype=np.int32)
    inf = np.iinfo(np.int32).max

    current = first if first is not None else randrange(n)
    for i in range(n):
        res[i] = current
        used[current] = True

        current = ne.evaluate('matrix[current] * (1-used) + used * inf').argmin()

    return res


def greedy(matrix: np.ndarray):
    """Жадный алгоритм для задачи коммивояжера."""
    assert matrix.shape[0] == matrix.shape[1]
    n = len(matrix)

    partial_routes = [[i] for i in range(n)]  # создаем начальные маршруты
    sets = UnionFind(size=n)
    edges = sorted(((i, j) for i, j in combinations(range(n), 2) if i != j), key=lambda e: matrix[e])

    for i, j in edges:
        ri, rj = partial_routes[sets.find(i)], partial_routes[sets.find(j)]

        # заменить конкатенации на туплы с флагом или генераторы
        if not sets.coonnected(i, j):
            new_route = connect(i, j, ri, rj)
            if new_route is not None:
                union_id = sets.union(i, j)
                partial_routes[union_id] = new_route

    return partial_routes[sets.find(0)]


def mst_approx(matrix: np.ndarray):
    """2-приближение через MST.

    # TODO: закончить эту штуку
    """
    minimum_spanning_tree(matrix)


def cheapest_insertion(
    matrix: Array,
    first: int = None,
):
    # TODO:
    n = len(matrix)
    tour = blist()
    current = first if first is not None else randrange(n)

    tour += [current]


def generate_initial_solution(matrix: Array, points: Array = None, candidates: Array = None):
    """Генерируем случайное случайным методом генерации."""
    methods = [
        lambda: random_tour(matrix),
        lambda: sweep(points),
        lambda: walk(matrix, candidates),
        lambda: tsp_nn(matrix),
        lambda: greedy(matrix),
    ]

    return random.choice(methods)()


# ----------------------------------------------- helpers -----------------------------------------------------------

def connect(i, j, ri, rj):
    """Соединяем ri, rj в правильном порядке.

    # TODO: попробовать эту же тему, вместо объединения брать tuple с флагом reversed
    """
    if ri[0] == i and rj[0] == j:
        # переворачиваем тот кусок, который меньше
        return ri[::-1] + rj if len(ri) < len(rj) else ri + rj[::-1]
    elif ri[-1] == i and rj[0] == j:
        return ri + rj
    elif ri[0] == i and rj[-1] == j:
        return rj + ri
    elif ri[-1] == i and rj[-1] == j:
        return ri[::-1] + rj if len(ri) < len(rj) else ri + rj[::-1]
    else:
        return None
