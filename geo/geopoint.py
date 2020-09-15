import math
from dataclasses import dataclass
from typing import Dict, Tuple

from auromat.coordinates.transform import spherical_to_cartesian

from geo.transforms import EARTH_R


@dataclass
class GeoPoint:
    """
    Точка с географическими координатами.
    """
    __slots__ = ("id_", "lat", "lon", "address")

    id_: int
    lat: float
    lon: float
    address: str

    def __str__(self) -> str:
        return f'(id={self.id_}, c={self.coords()})'

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

    def to_cartesian(self):
        """
        Получаем 3D координаты точки
        :return:
        """
        return spherical_to_cartesian(EARTH_R, self.lat, self.lon)


@dataclass
class Point3D:
    __slots__ = ("id_", "x", "y", "z")

    id_: int
    x: float
    y: float
    z: float
