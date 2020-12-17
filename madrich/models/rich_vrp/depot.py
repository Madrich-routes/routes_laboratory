"""Класс депо."""
from typing import Tuple

from madrich.models.rich_vrp.place import Place


class Depot(Place):
    """Депо — объект из которого машины забирают грузы. Или куда они их привозят.

    Parameters
    ----------
    id : Любой уникальный id
    time_window : Временные окна, в которые этот объект можно посетить
    lat : Широта
    lon : Долгота
    delay : Время посещения
    name : Читаемое имя (адрес или название)
    """

    def __init__(
        self,
        id: int,  # noqa
        time_window: Tuple[int, int],  # оно всегда одно и только одно
        lat: float,
        lon: float,
        delay: int,
        name: str = '',
    ):
        super().__init__(
            id=id, name=name, lat=lat, lon=lon, delay=delay, time_windows=[time_window]
        )

    def __hash__(self):
        return hash(self.id)
