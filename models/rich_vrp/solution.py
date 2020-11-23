from dataclasses import dataclass
from typing import List, Optional

from models.rich_vrp.plan import Plan
from models.rich_vrp.problem import RichVRPProblem


@dataclass
class VRPSolution:
    problem: RichVRPProblem
    routes: List[Plan]  # маршруты для каждого из курьеров
    info: Optional[dict]
