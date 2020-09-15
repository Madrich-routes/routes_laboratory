from dataclasses import dataclass
from itertools import combinations

from models.cvrptw import CVRPTWProblem


@dataclass
class ClarkeWright:
    """
    Предполагаем, что проблема симметричная
    """
    problem: CVRPTWProblem

    def sorted_pairs(self):
        """
        Пары точек отсортированные по возрастанию расстояния
        """
        m, ml = self.problem.matrix, len(self.problem.matrix)
        return sorted(combinations(range(ml), r=2), key=lambda x: m[x])

    def solve(self):
        ...
        # self.matrix
