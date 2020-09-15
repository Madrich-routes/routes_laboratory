from dataclasses import dataclass
from typing import Tuple


@dataclass
class Point:
    lat: float
    lon: float

    def coords(self) -> Tuple[float, float]:
        return self.lon, self.lat
