"""В этом модуле описываются промежуточные классы и структуры, используемые во время работы с ребрами-
кандидатами."""
from dataclasses import dataclass
from typing import Set


@dataclass
class CandidateEdge:
    src: int  # откуда
    dst: int  # куда
    time: int  # сколько времени занимает проезд

    alpha_measure: float = None  # альфа-мера качества ребра
    length: int = None  # какая длина
    tw: int = None  # насколько узкое у ребра максимальное временное окно
    agents: Set[int] = None  # какие агенты могут по ребру проезжать
