from dataclasses import dataclass

from models.rich_vrp.job import Place


@dataclass
class Visit:
    __slots__ = ('job', 'time')

    def __str__(self):
        return f'Visit({self.place.lon} {self.place.lat}, {self.time / 3600:.2f}ч)'

    place: Place
    time: int

    @property
    def delay(self):
        return self.place.delay
