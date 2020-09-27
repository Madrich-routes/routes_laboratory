from collections import defaultdict
from typing import List

from utils.types import Array


def determine_borderline(
        matrix: Array,
        depots: int,
        jobs: int,
        candidates: List[List[int]],  # множество ребер-кандидатов
        epsilon: int = 0.7,  # насколько более далекое депо мы рассматриваем
):
    """
    Определяем депо, которые мы вообще рассматриваем для каждого заказчика
    """
    possible_depots = defaultdict(list)


