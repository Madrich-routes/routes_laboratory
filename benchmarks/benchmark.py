from typing import List

from models.rich_vrp.problem import RichVRPProblem


class Benchmark:
    def __init__(
        self,
        problem: RichVRPProblem,
        length: float,
        solution: List[int]
    ):
        self.problem = problem
        self.length = length
        self.solution = solution
