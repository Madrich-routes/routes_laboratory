"""
В этом модуле описываются промежуточные классы и структуры, используемые во время работы с ребрами-кандидатами.
"""
from dataclasses import dataclass
from typing import Set


@dataclass
class CandidateEdge:
    src: int  # откуда
    dst: int  # куда
    time: int  # сколько времени занимает проезд

    alpha_measure: float = None  # альфа-мера качества ребра
    length: int = None  # какая длина
    tw: int = None  # насколько узкое у ребра максимальное временное окно
    agents: Set[int] = None  # какие агенты могут по ребру проезжать

# class EdgeSet:
#     def __init__(self, edges: List[Edge]):
#         self.edges = set(edges)
#
#         self.in_idx = defaultdict(list)
#         self.out_idx = defaultdict(list)
#
#         for e in edges:
#             self.in_idx[e.end] += [e.start]
#             self.out_idx[e.start] += [e.end]
#
#     def __contains__(self, e: Edge):
#         return e in self.edges
