from dataclasses import dataclass, field
from typing import Optional, List, Dict

from madrich.models.rich_vrp.plan import Plan
from madrich.models.rich_vrp.problem import RichVRPProblem, RichMDVRPProblem


@dataclass
class VRPSolution:
    problem: RichVRPProblem
    routes: List[Plan] = field(default_factory=list)  # маршруты для каждого из курьеров
    info: Optional[dict] = field(default_factory=dict)


@dataclass
class MDVRPSolution:
    problem: RichMDVRPProblem
    routes: Dict[int, List[Plan]] = field(default_factory=dict)  # agent_id: список маршрутов в временном порядке

    def merge(self, solution: VRPSolution):
        for route in solution.routes:
            self.insert_plan(route)

    def insert_plan(self, insertable: Plan):
        if insertable.agent.id not in self.routes:  # значит этот курьер еще ничего не отвез
            self.routes[insertable.agent.id] = [insertable]
        else:
            for i, route in enumerate(self.routes[insertable.agent.id]):
                # ищем маршрут, который был точно перед маршрутом, который мы хотим вставить
                if route.waypoints[-1].departure < insertable.waypoints[0].arrival:  # значит мы проскочили по времени
                    self.routes[insertable.agent.id].insert(i + 1, insertable)  # значит после него
                    break
            else:
                self.routes[insertable.agent.id].insert(0, insertable)  # мы не нашли такого, вставляем в конец
