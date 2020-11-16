from typing import List, Optional

from models.rich_vrp.plan import Plan
from models.rich_vrp.problem import RichVRPProblem


class VRPSolution:
    def __init__(
        self,
        problem: RichVRPProblem,
        routes: List[Plan],
        info: Optional[dict] = None
    ):
        # TODO: адекватно оформить решение
        self.problem = problem
        self.routes = routes
        self.geojson: Optional[str] = None
        self.info: Optional[dict] = info

    # def statistics(self):
    #     for a, r in self.routes.items():
