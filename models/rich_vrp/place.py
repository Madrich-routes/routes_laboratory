from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional, Tuple, Sequence
# from utils.types import Array
import utils

@dataclass
class Place:
    """
    Общий базовый класс для всего, что является местом
    """
    id: int  # Просто какой-то уникальный id. Индекс в матрице хранят другие классы.
    name: Optional[str] = None  # читаемый идентификатор. Например, адрес.

    # позиция на карте
    lat: Optional[float] = None
    lon: Optional[float] = None

    # иногда может понадобиться указать декартовы координаты
    x: Optional[int] = None
    y: Optional[int] = None

    delay: int = 0  # сколько времени нужно пробыть в этом месте
    time_windows: Sequence[Tuple[int, int]] = field(default_factory=list)  # когда там можно находиться

    def __post_init__(self):
        self.time_windows = tuple(self.time_windows)

    def __hash__(self):
        return hash(self.descriptor)

    def __eq__(self, other: 'Place'):
        return self.descriptor == other.descriptor

    def __le__(self, other: 'Place'):
        return self.descriptor < other.descriptor

    @property
    def descriptor(self) -> Tuple[type, int]:
        """Вернуть уникальный индектификатор

        Returns
        -------
        Уникальный хендл для модели
        """
        return type(self), self.id
