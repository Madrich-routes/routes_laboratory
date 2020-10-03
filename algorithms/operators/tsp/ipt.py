"""
Реализация алгоритма IPT: Iterated partial transcription
"""

from random import randint
from typing import List, Dict, Union

import numpy as np


# TODO: как будто бы нет объединения общих частей

def create_filled_matrix(size: int, max_weight: int = 10):
    """
    :param size: размер матрицы
    :param max_weight: максимальный вес ребра.
    Функция для создания рандомной симметричной матрицы маршрутов.
    Координаты каждой ячейки - адресация ребра графа. Т.е. (2,5) - ребро от 2й вершины к 5й.
    Число в ячейке - вес ребра.
    Фукнция нужна только для тестирования.
    """
    matrix = np.zeros((size, size), int)
    for i in range(size):
        for j in range(size):
            if i != j:  # оставляем маршруты от города к самому себе нулевыми по весу
                matrix[i, j] = matrix[j, i] = randint(1, max_weight)
    return matrix


def get_weight_of_subchain(matrix: np.array, route: List[int]) -> int:
    """
    Получить вес подмаршрута. Считается, что подмаршрут незамкнут.
    """
    weight = 0
    for i in range(len(route) - 1):
        x = i
        y = i + 1
        weight += matrix[x, y]
    return weight


def find_the_best_subchains(route1: List[int], route2: List[int], matrix: np.array):
    # Стартовое значение размера подмашрута.
    slice_size = 4
    # Копии переданных маршрутов для обработки.
    tmp_route1 = route1[:]
    tmp_route2 = route2[:]
    # Конечный список подмаршрутов с координатами для вставки-замены
    # в любой из двух переданных маршрутов.
    final_route = []  # type: List[Dict[str, Union[List[int], int]]]
    # Делаем поиск пока выполняется данное условие:
    # длина подмаршрута меньше половины длины маршрута.
    while slice_size <= len(route1) // 2:
        # Устанавливаем курсор поиска на начало маршрутов.
        i = 0
        # Обход маршрутов идёт от ноля и до длины машрута - текущая длина подмаршрута.
        while i <= len(tmp_route1) - slice_size:
            # Проверяем, что стартовая вершина первого подмаршрута есть
            # во 2м модифицированном машруте
            if tmp_route1[i] in tmp_route2:
                # если это так, то получаем индекс стартовой вершины второго подмаршрута.
                j = tmp_route2.index(tmp_route1[i])
                # Получаем подмаршруты из обоих маршрутов.
                subchain1 = tmp_route1[i:i + slice_size]
                subchain2 = tmp_route2[j:j + slice_size]
                # Проверяем, что:
                # 1. Они одинаковой длинны. Она может быть разная, если разница между индексами
                # стартовых вершин подмаршрутов отрицательная
                # (start_index_route1 - start_index_route2 < 0).
                # 2. Стартовые и конечные вершины подмаршрутов одинаковы.
                # 3. Сами подмаршруты не одинаковы.
                if len(subchain1) == len(subchain2) and tmp_route1[i] == tmp_route2[j] and \
                        tmp_route1[i + slice_size - 1] == tmp_route2[j + slice_size - 1] and \
                        subchain1 != subchain2:
                    # Считаем вес подмаршрутов.
                    subchain1_weight = get_weight_of_subchain(matrix, subchain1)
                    subchain2_weight = get_weight_of_subchain(matrix, subchain2)
                    # Выбираем лучший из двух и записываем в результат,
                    # добавляя координаты для вставки.
                    if subchain2_weight > subchain1_weight:
                        final_route.append({
                            'subchain': subchain1,
                            'begin': tmp_route1[i - 1],
                            'end': tmp_route1[i + slice_size]
                            if i + slice_size < len(tmp_route1) else None
                        })
                    else:
                        final_route.append({
                            'subchain': subchain2,
                            'begin': tmp_route2[j - 1],
                            'end': tmp_route2[j + slice_size]
                            if j + slice_size < len(tmp_route2) else None
                        })
                    #  Удаляем найденные подмашруты из машрутов.
                    tmp_route1 = tmp_route1[:i] + tmp_route1[i + slice_size:]
                    tmp_route2 = tmp_route2[:j] + tmp_route2[j + slice_size:]
                    # Продолжаем искать следующие подмаршруты той же длины, что и предыдущие.
                    # Вместо след.двух действий можно вставить break, тогда после нахождения
                    # подмашрутов n длины, следующий поиск уже будет для n+1.
                    i = 0  # обнуляем курсор по маршрутам, т.к. их длина и содержимое изменились.
                    continue
            i += 1
        slice_size += 1

    return final_route


def compile_route(subchains: List[Dict[str, Union[List[int], int]]], route: List[int]):
    """
    :param subchains: результат работы функции find_the_best_subchains
    :param route: любой из двух входящих маршрутов
    Функция для сборки финального машрута из найденых
    подмаршрутов и общих для обоих маршрутов частей.
    """
    # Убираем из машрута все вершины, котоыре попали в подмаршруты.
    # Оставшиеся вершины - общие для двух маршрутов.
    route = [el for el in route if all(el not in subchain['subchain'] for subchain in subchains)]
    # Вставку подмаршрутов начинаем с последнего найденного подмаршрута.
    subchains.reverse()
    for subchain in subchains:
        insert_index = route.index(subchain['begin'])
        for i, el in enumerate(subchain['subchain']):
            route.insert(i + insert_index + 1, el)
    return route


def ipt(route1: List[int], route2: List[int], matrix: np.array) -> List[int]:
    subchains = find_the_best_subchains(route1, route2, matrix)
    result = compile_route(subchains, route1)

    return result

# Немного тестовых данных:

# list1 = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
# list2 = [0, 1, 3, 4, 6, 5, 7, 8, 2, 9, 10]
# list1 = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
# list2 = [10, 9, 8, 7, 6, 5, 4, 3, 2, 1, 0]
#
# list3 = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 13, 11, 14]
# list4 = [0, 1, 3, 2, 4, 5, 6, 8, 7, 9, 10, 13, 11, 12, 14]
#
# print(ipt(route1=list1, route2=list2, matrix=create_filled_matrix(11)))
# print(ipt(route1=list3, route2=list4, matrix=create_filled_matrix(15)))
