"""Алгоритм бета-остова.

Очень медленный, но прикольный.
"""
import math
from functools import lru_cache
from itertools import combinations

from utils.types import Array

beta = 1.1
max_theta = math.asin(1 / beta)


@lru_cache
def dot(p, q, r):
    return sum((p[i] - r[i]) * (q[i] - r[i]) for i in [0, 1])


def sharp(points, p: int, q: int):
    theta = float('-inf')
    for r in points:
        if r not in [p, q]:
            prq = math.acos(dot(p, q, r) / (dot(p, p, r) * dot(q, q, r)) ** 0.5)
            theta = max(theta, prq)
    return theta


def beta_skeleton(points: Array, return_theta: bool = False):
    """Основной цикл.

    TODO: все это можно написать оптимальнее.
    """
    res = []

    for p, q in combinations(points):
        theta = sharp(points, p, q)

        if theta < max_theta:
            if return_theta:
                res += [(p, q, theta)]
            else:
                res += [(p, q)]

    return res
