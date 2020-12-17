from typing import List

from madrich.models.rich_vrp import RichVRPProblem


class Benchmark:
    def __init__(self, problem: RichVRPProblem, length: float, solution: List[int]):
        self.problem = problem
        self.length = length
        self.solution = solution
