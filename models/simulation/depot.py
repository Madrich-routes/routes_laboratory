import abc
from dataclasses import dataclass
from typing import Dict, Tuple


@dataclass
class Point(abc.ABC):
    __slots__ = ("id_", "lat", "lon", "address")

    id_: int
    lat: float
    lon: float
    address: str

    def __str__(self) -> str:
        return f'(id={self.id_})'

    def __repr__(self) -> str:
        return str(self)

    def __eq__(self, other) -> bool:
        return isinstance(other, Point) and self.id_ == other.id_

    def __hash__(self):
        return self.id_

    def __lt__(self, other):
        return self.id_ < other.id_

    def coords(self) -> Tuple[float, float]:
        return self.lon, self.lat


class Depot(Point):
    def __init__(
            self,
            lat: float,
            lon: float,
            id_: int,
            address: str = ''
    ):
        super().__init__(id_=id_, lat=lat, lon=lon, address=address)

    def __hash__(self):
        return hash(self.id_)


@dataclass
class Visit:
    __slots__ = ('point', 'time')

    def __str__(self):
        return f'Visit({self.point}, {self.time / 3600:.2f}ч)'

    point: Point
    time: int

    def export(self) -> Dict:
        return {**self.point.export(), **dict(time_visit=self.time)}
