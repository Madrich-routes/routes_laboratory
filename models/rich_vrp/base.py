import abc
from dataclasses import dataclass
from typing import Tuple


@dataclass
class GeoPoint(abc.ABC):
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
        return isinstance(other, GeoPoint) and self.id_ == other.id_

    def __hash__(self):
        return self.id_

    def __lt__(self, other):
        return self.id_ < other.id_

    def coords(self) -> Tuple[float, float]:
        return self.lon, self.lat
