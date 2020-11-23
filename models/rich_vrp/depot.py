""" Класс депо """
from typing import Tuple, List

from models.rich_vrp.place import Place


class Depot(Place):
    """Депо — объект из которого машины забирают грузы. Или куда они их привозят.

    Parameters
    ----------
    id : Любой уникальный id
    time_windows : Временные окна, в которые этот объект можно посетить
    lat : Широта
    lon : Долгота
    delay : Время посещения
    name : Читаемое имя (адрес или название)
    """

    def __init__(
        self,
        id: int,
        time_windows: List[Tuple[int, int]],
        lat: float,
        lon: float,
        delay: int,
        name: str = '',
    ):
        super().__init__(
            id=id, name=name, lat=lat, lon=lon, delay=delay, time_windows=time_windows
        )

    def __hash__(self):
        return hash(self.id)
