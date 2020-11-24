"""Методы из работы Pisinger, Ropke.

A general heuristic for vehicle routing problems.
"""

from dataclasses import dataclass
from typing import List

from madrich.utils.types import Array


@dataclass
class Request:
    src: int
    dst: int
    amount: int
    tw_start: int
    tw_end: int


@dataclass
class RPDPTW:
    requests = List[Request]


def ovrp_to_cvrp(
    matrix: Array,
    depots: Array
):
    """Откуда угодно до депо бесплатно."""
    matrix[:, depots] = 0


def cvrp_to_vrptw(
    time_matrix: Array,
    service_times: Array,
    max_capacity: int,
):
    """Cheapest."""
