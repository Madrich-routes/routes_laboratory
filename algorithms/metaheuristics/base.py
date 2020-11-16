from __future__ import annotations

class BaseSolution:
    @property
    def fitness(self):
        raise NotImplementedError

    @property
    def metrics(self):
        raise NotImplementedError

    @property
    def neighbours(self):
        raise NotImplementedError

    @property
    def improve(self):
        raise NotImplementedError

    @property
    def mutate(self):
        raise NotImplementedError

    def crossover(self, other: BaseSolution):
        raise NotImplementedError

    @property
    def crowding_dist(self):
        raise NotImplementedError

    def dist(self, other: BaseSolution):
        raise NotImplementedError
