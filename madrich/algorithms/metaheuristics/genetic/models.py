from madrich.temp.tsp import List


class BaseIndividual:
    """Класс для примера.

    Что-то, у чего есть fitness
    """

    def __init__(
        self,
        fitness: float
    ):
        self.fitness = fitness  # type: float
        self.metrics: List[float] = []
        self.crowding_dist: float = 0
