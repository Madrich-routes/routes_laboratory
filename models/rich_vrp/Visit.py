from dataclasses import dataclass


@dataclass
class Visit:
    __slots__ = ('point', 'time')

    def __str__(self):
        return f'Visit({self.point}, {self.time / 3600:.2f}ч)'

    point: Point  # TODO: ...
    time: int
