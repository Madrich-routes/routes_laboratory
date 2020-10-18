from dataclasses import dataclass

from models.rich_vrp.job import Place


@dataclass
class Visit:
    __slots__ = ('point', 'time')

    def __str__(self):
        return f'Visit({self.point}, {self.time / 3600:.2f}ч)'

    point: Place
    time: int
