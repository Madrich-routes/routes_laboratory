from datetime import datetime
from typing import Dict, List

import pandas as pd

from models.problems.base import BaseRoutingProblem
from models.rich_vrp import Agent
from models.rich_vrp.plan import Plan
from models.rich_vrp.visit import Visit


class VRPSolution:
    def __init__(
            self,
            problem: BaseRoutingProblem,
            routes: List[Plan],
    ):
        # TODO: адекватно оформить решение
        self.problem = problem
        self.routes = routes

    # def statistics(self):
    #     for a, r in self.routes.items():
