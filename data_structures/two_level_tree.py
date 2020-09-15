from dataclasses import dataclass

# TODO: возможно B-дерево с неявным ключем лучше справится?
from math import sqrt
from typing import List

"""
Каждый сегмент может быть sqrt(N)/2 - 2 * sqrt(N).
"""


@dataclass
class ParentNode:
    reversed: bool  # нужно обходить в обратном порядке

    next: "ParentNode"  # список
    prev: "ParentNode"  # двусвязный

    first: "Node"  # ссылки на начало и конец отрезка
    last: "None"

    num: int  # порядковый номер вершины в списке
    size: int  # количество точек в этом отрезке


@dataclass
class Node:
    _next: "Node"  # список
    _prev: "Node"  # двусвязный

    parent: "ParentNode"  # указание на сегмент

    # Порядковый номер вершины в сегменте. Не обязательно начинается с 1.
    # Нужен для того, чтобы быстро сравнивать какая вершина идет за какой.
    # В случае reversed можно брать со знаком -
    _num: int
    id: int  # id точки

    def is_reversed(self) -> bool:
        """
        Проверяем перевернут ли ее отрезок
        """
        return self.parent.reversed

    def num(self):
        """
        Номер с учетом reversed
        """
        return (1 - 2 * self.is_reversed()) * self._num

    def num_tup(self):
        """
        Тупл из номера родителя и собственного
        """
        return self.parent_num(), self.num()

    def parent_num(self):
        """
        Номер родителя
        """
        return self.parent.reversed

    def next(self):
        return self._prev if self.is_reversed() else self._next

    def prev(self):
        return self._next if self.is_reversed() else self._prev

    def is_between(self, a: "Node", b: "Node"):
        return a.num_tup() <= self.num_tup() <= b.num_tup()

    # ------------------------------------ Вспомогательные функции ----------------------------------------------------

    def same_segment(self, a: "Node"):
        return self.parent_num() == a.parent_num()


@dataclass
class TwoLevelTree:
    def __init__(self, data: List[int]):
        sq = sqrt(len(data))
        r = int(sq) * int(sq)

        # TODO: правильно проставить все ссылки и размеры
        self.nodes = [
            Node(_next=None, _prev=None, parent=None, _num=i, id=v)
            for i, v in enumerate(data)
        ]
        self.parents = [
            ParentNode(reversed=False, next=None, prev=None, first=None, last=None, num=i, size=0)
            for i in range(int(sq))
        ]

    # def flip(self, t1, t2, t3, t4):
    #     """
    #     (a, b), (c, d) -> (a, d), (b, c)
    #     """
    #     if t3 == t2.prev() or t3 == t2.next():
    #         return

    def revert_inside_segment(self, a: Node, b: Node):
        while a != b:
            a.prev, a


    def flip(self, a: Node, b: Node, c: Node, d: Node) -> None:
        if b.same_segment(d) or a.same_segment(c):
            ...

