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
            plans = self.routes[insertable.agent.id]

            # если он до первого
            if insertable.waypoints[-1].departure < plans[0].waypoints[0].arrival:
                plans.insert(0, insertable)
                return

            for i in range(len(plans)):
                # нам нужно куда-то вставить маршрут
                # не куда-то, а по порядочку обязательно
                if i == (len(plans) - 1):  # значит мы дошли до конца
                    plans.append(insertable)

                # сравниваю текущий и следующий
                point = insertable.waypoints[0]
                if plans[i].waypoints[-1].departure < point.arrival < plans[i + 1].waypoints[0].arrival:
                    assert plans[i].waypoints[-1].departure < point.arrival, 'shit'
                    assert point.departure < plans[i + 1].waypoints[0].arrival, 'big shit'
                    plans.insert(i + 1, insertable)

    def print(self):
        for agent_id, route in self.routes.items():
            print(f'agent: {agent_id}\n {route}')
