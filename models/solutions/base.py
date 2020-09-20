import numpy as np

from models.problems.base import BaseRoutingProblem


class VRPSolution:
    def __init__(self, problem: BaseRoutingProblem):
        self.problem = problem


# class CVRPTWSolution:
#     def __init__(self, problems):
