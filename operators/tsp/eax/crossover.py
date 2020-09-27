import random
from typing import List, Tuple

from utils.types import Array


def build_graph(a: Array, b: Array):
    """
    Получаем граф
    """
    n = len(a)
    graph = [[] for _ in range(n)]

    for i in range(n):
        a_from, a_to = a[i], a[(i + 1) % n]
        b_from, b_to = b[i], b[(i + 1) % n]

        graph[a_from] += [(a_to, 'a')]
        graph[a_to] += [(a_from, 'a')]

        graph[b_from] += [(b_to, 'b')]
        graph[b_to] += [(b_from, 'b')]

    return graph


def build_random_cycle(graph: List[List[Tuple[int, str]]]):
    """
    Получаем цикл с чередующимися ребрами.
    """
    n = len(graph)
    first = random.choice(range(n))
    res = [first]

    visited = [False] * n
    curr_node = first
    prev_edge_parent = None

    while True:
        random.shuffle(graph[first])  # TODO: мб это тут не нужно так часто?
        for edge in graph[first]:
            if edge[1] == prev_edge_parent:
                continue

            curr_node = edge[0]

            # TODO: доделать


def build_edge_set(cycles: List[List[int]], n: int):
    graph = [[] for _ in range(n)]

    for cycle in cycles:
        l = len(cycle)
        for i in range(len(cycle)):
            f, t = cycle[i], cycle[(i + 1) % l]
            graph[f] += [cycle[t]]
            graph[t] += [cycle[f]]

    return graph

def apply(eset, cycle):
    ...


def reconnect_cycle():
    ...
