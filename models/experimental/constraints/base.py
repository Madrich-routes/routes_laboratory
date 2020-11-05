from functools import wraps
from typing import Callable, TypeVar


class BaseConstraint:
    pass


class BaseSoftConstraint:
    pass


class BaseHardConstraint:
    pass


IndType = TypeVar('IndType')


class Penalty:
    def __init__(
        self,
        feasible_dist: Callable[[IndType], float],
        fixed_cost: float = 0,
        distance_cost: Callable[[float], float] = lambda x: x,
    ):
        self.feasible_dist = feasible_dist
        self.distance_cost = distance_cost
        self.fixed_cost = fixed_cost

    def __call__(
        self,
        fitness_func: Callable[[IndType], float],
    ) -> Callable[[IndType], float]:
        @wraps(fitness_func)
        def wrapper(individual: IndType) -> float:
            dist = self.feasible_dist(individual)
            fitness = fitness_func(individual)

            if dist == 0:
                return fitness
            else:
                return self.fixed_cost + self.distance_cost(dist) + fitness

        return wrapper
