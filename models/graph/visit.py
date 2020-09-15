from dataclasses import dataclass

from models.graph.vertex import Vertex


@dataclass
class Visit:
    __slots__ = ('point', 'time')

    def __str__(self):
        return f'Visit({self.point}, {self.time / 3600:.2f}ч)'

    vertex: Vertex
    time: int
