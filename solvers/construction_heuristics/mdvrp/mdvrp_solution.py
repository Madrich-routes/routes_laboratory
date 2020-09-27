from collections import defaultdict

from utils.types import Array


def determine_borderline(
        matrix: Array,
        depots: int,
        jobs: int,
        epsilon: int = 0.7,  # насколько более далекое депо мы рассматриваем
):
    """
    Определяем депо, которые мы вообще рассматриваем.
    """
    possible_depots = defaultdict(list)


