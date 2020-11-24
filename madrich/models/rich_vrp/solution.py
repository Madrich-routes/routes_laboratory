from dataclasses import dataclass, field
from typing import Optional, List, Dict

from madrich.models.rich_vrp.plan import Plan
from madrich.models.rich_vrp.problem import RichVRPProblem, RichMDVRPProblem


@dataclass
class VRPSolution:
    problem: RichVRPProblem
    routes: List[Plan]  # маршруты для каждого из курьеров
    info: Optional[dict]


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
                # ищем маршрут, который был точно после маршрута, который мы хотим вставить
                if insertable.waypoints[0].arrival > route.waypoints[-1].departure:  # значит мы проскочили по времени
                    self.routes[insertable.agent.id].insert(i - 1, insertable)  # значит на индекс раньше
                    break
            else:
                self.routes[insertable.agent.id].append(insertable)  # мы не нашли такого, вставляем в конец
