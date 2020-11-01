from typing import Tuple

from models.rich_vrp.job import Place
from temp.tsp import List


class Depot(Place):
    def __init__(
            self,
            id: int,
            time_windows: List[Tuple[int, int]],
            lat: float,
            lon: float,
            delay: int,
            name: str = '',
    ):
        super().__init__(id=id, name=name, lat=lat, lon=lon)
        self.time_windows = time_windows
        self.delay = delay

    def __hash__(self):
        return hash(self.id)
