from models.problems.base import BaseRoutingProblem
from models.rich_vrp.solution import VRPSolution
from solvers.base import BaseSolver


class RustSolver(BaseSolver):
    def __init__(self):
        self.problem_file = './tmp/problem.pragmatic'
        self.solution_file = './tmp/solution.pragmatic'

    def solve(self, problem: BaseRoutingProblem) -> VRPSolution:
        ...
