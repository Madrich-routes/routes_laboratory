"""
Тут реализованы разные популярные кросоверы для tsp
"""
import random
from collections import defaultdict
from itertools import chain
from typing import List

from more_itertools import windowed
import numpy as np


# TODO: все используют tournament selection почему-то.

# TODO: проследить, какую границу берем, какую не берем. С этим много косяков мб.

def get_neighbours(p: List[int]):
    """
    Получаем список всех ребер
    """
    res = defaultdict(set)
    for a, b in windowed(p, 2):
        res[a].add(b)
        res[b].add(a)

    res[p[0]].add(p[-1])
    res[p[-1]].add(p[0])

    return res


def edge_recombination_crossover(p1: List[int], p2: List[int]):
    """
    Считается лучшим кросовером, но долго считается
    Источники: http://www.rubicite.com/Tutorials/GeneticAlgorithms/CrossoverOperators/EdgeRecombinationCrossoverOperator.aspx
    TODO: Мб можно сделать его рандомизированную версию, которая существенно быстрее
    TODO: Можно сделать версию, которая будет считать ребра ориентированными
    """
    assert len(p1) == len(p2)

    neighbours = defaultdict(set)
    child = []
    unused = set(p1)

    def add_neighbours(p: List[int]):
        """
        Получаем список всех ребер
        """
        nonlocal neighbours
        for a, b in windowed(p, 2):
            neighbours[a].add(b)
            neighbours[b].add(a)

        neighbours[p[0]].add(p[-1])
        neighbours[p[-1]].add(p[0])

    def neighbour_with_fewest_neighbours(x):
        return min(neighbours[x], key=lambda n: len(neighbours[n]))

    def remove_from_neighbours(x):
        for n in neighbours[x]:
            n.remove(x)

    add_neighbours(p1)
    add_neighbours(p2)

    x = random.choice([p1[0], p2[0]])
    while len(child) != len(p1):
        child += [x]
        unused.remove(x)
        remove_from_neighbours(x)

        if neighbours[x]:
            x = neighbour_with_fewest_neighbours(x)
        else:
            x = next(iter(unused))

    # TODO: возможно, это оптимизируется. Квадрат не оч :(

    return child


def order1_crossover(p1: List[int], p2: List[int]):
    """
    Копируем кусок из родителя, остальное вставляем как пойдет от второго
    http://www.rubicite.com/Tutorials/GeneticAlgorithms/CrossoverOperators/Order1CrossoverOperator.aspx
    TODO: Multiple — это то же самое, только дырок больше
    """
    child = [None] * len(p1)
    i, j = random.sample(range(len(p1)), 2)

    copied = set()

    if i < j:
        child[i:j] = p1[i:j]
        copied.update(p1[i:j])
    else:
        child[i:] = p1[i:]
        child[:j] = p1[:j]
        copied.update(p1[i:])
        copied.update(p1[:j])

    left = (x for x in p2 if x not in copied)
    for i, v in enumerate(child):
        if v is None:
            child[i] = next(left)

    return child


def cycle_crossover_operator(p1: List[int], p2: List[int]):
    """
    Находим циклы перестановках. Копируем циклы по очереди то из одного, то из другого родителя.
    Источник: http://www.rubicite.com/Tutorials/GeneticAlgorithms/CrossoverOperators/CycleCrossoverOperator.aspx
    TODO: можно выбирать только лучшие циклы, будет почти IPT (или прямо IPT)
    """
    child = [None] * len(p1)

    # Строим обратный индекс для p1
    reverse_index_p1 = [None] * len(p1)
    for i, v in enumerate(p1):
        reverse_index_p1[v] = i

    # Строим обратный индекс для p2
    reverse_index_p2 = [None] * len(p2)
    for i, v in enumerate(p2):
        reverse_index_p1[v] = i

    # Присваиваем родителей переменным, которые потом будут меняться местами
    a, b = p1, p2
    r_ind_a, r_ind_b = reverse_index_p1, reverse_index_p2

    # пищем индекс, которые еще не скопирован
    for i in range(len(p1)):

        idx = i  # первый индекс
        if child[idx] is None:
            # меняем родителя, от которого будем копировать цикл
            a, b = b, a
            r_ind_a, r_ind_b = r_ind_b, r_ind_a

            # находим и копируем цикл от индекса idx
            while child[idx] is None:
                v = a[idx]
                idx = r_ind_a[v]

                child[idx] = v

    return child


def pmx(p1: List[int], p2: List[int]):
    """
    Источник: http://www.rubicite.com/Tutorials/GeneticAlgorithms/CrossoverOperators/PMXCrossoverOperator.aspx
    """
    child = [None] * len(p1)
    i, j = random.sample(range(len(p1)), 2)
    copied = set()

    # Строим обратный индекс для p2
    reverse_index = [None] * len(p1)
    for i, v in enumerate(p2):
        reverse_index[v] = i

    # копируем кусок в ребенка
    if i < j:
        child[i:j] = p1[i:j]
        copied.update(p1[i:j])
    else:
        child[i:] = p1[i:]
        child[:j] = p1[:j]
        copied.update(p1[i:])
        copied.update(p1[:j])

    # находим отличающиеся на тех же позициях
    if i < j:
        different = [x for x in p2[i:j] if x not in copied]
    else:
        different = [x for x in chain(p2[i:], p2[:j]) if x not in copied]

    # Ищем, куда распихать тех, кто на той же позиции
    for x in different:
        v = x
        while True:
            i = reverse_index[v]
            v = p1[i]
            i2 = reverse_index[v]

            # i2 не в скопированном чанке
            # out = (not i <= i2 < j) if i < j else (j < i2 <= i)  # норм ли условие?
            if child[i2] is None:  # похоже, что этой проверки на None достаточно
                child[i2] = x
                break

    # все что не заполнили, просто копируем от второго родителя
    for i, v in enumerate(child):
        if v is None:
            child[i] = p2[i]

    return child


def hgrex(p1: List[int], p2: List[int], matrix: np.ndarray):
    """
    Говорят, эта эвристика неплоха и вообще лучше всех.
    Comparison of eight evolutionary crossover operators for the
    vehicle routing problem
    Krunoslav Puljic´
    1,∗and Robert Manger1
    # TODO: говорят, что она неплоха.
    """

    n1 = get_neighbours(p1)
    n2 = get_neighbours(p2)

    nn = {i: n1[i] | n2[i] for i in p1}

    for i in range(len(p1)):
        ...
