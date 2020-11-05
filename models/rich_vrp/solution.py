from typing import List, Optional

from models.problems.base import BaseRoutingProblem
from models.rich_vrp.plan import Plan


class VRPSolution:
    def __init__(
            self,
            problem: BaseRoutingProblem,
            routes: List[Plan],
    ):
        # TODO: адекватно оформить решение
        self.problem = problem
        self.routes = routes
        self.geojson: Optional[str] = None

    # def statistics(self):
    #     for a, r in self.routes.items():
