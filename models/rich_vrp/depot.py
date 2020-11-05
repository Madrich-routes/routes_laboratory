from typing import Tuple, List

from models.rich_vrp.job import Place


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
        super().__init__(id=id, name=name, lat=lat, lon=lon, delay=delay, time_windows=time_windows)

    def __hash__(self):
        return hash(self.id)
