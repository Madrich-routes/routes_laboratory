from functools import reduce
from typing import List, Set


def sets_intersection(skill_sets: List[Set[int]]):
    """Пересечение всех множеств."""
    return reduce(lambda x, y: x & y, skill_sets, set())


def sets_union(skill_sets: List[Set[int]]):
    """Объединение всех множеств."""
    return reduce(lambda x, y: x | y, skill_sets, set())
