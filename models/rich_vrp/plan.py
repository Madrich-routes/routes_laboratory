"""Описание класса Plan — план посещений одного агента на день."""
from typing import List
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from models.rich_vrp.problem import RichVRPProblem
    from models.rich_vrp import Agent, Depot, Job, Visit


class Plan:
    """Полный маршрут одной конкретной машины.

    Содержит в себе
    1. agent — объект агента, который выполняет задания
    2. waypoints — набор объектов типа Visit (точка и время прибытия)
    """

    def __init__(
        self,
        agent: Agent,
        waypoints: List[Visit]
    ):
        self.agent = agent
        self.waypoints = waypoints


class PlanReport:
    def __init__(
        self,
        plan: Plan,
        problem: 'RichVRPProblem',
    ):
        self.plan = plan
        self.problem = problem

    def duration(self) -> int:
        """Считаем общую длительность плана агента.

        Returns
        -------
        Длительность плана в секундах
        """
        if len(self.plan.waypoints) < 2:
            return 0

        first_point = self.plan.waypoints[0]
        last_point = self.plan.waypoints[-1]
        last_duration = last_point.delay if hasattr(last_point, 'delay') else 0

        return last_point.time - first_point.time + last_duration

    def total_stops(self) -> int:
        """Общее количество остановок."""
        return len(self.plan.waypoints)

    def depot_stops(self) -> int:
        """Общее количество заездов в депо."""
        return len(
            v for v in self.plan.waypoints
            if isinstance(v.place, Depot)
        )

    def job_stops(self):
        """Общее количество обработаных джоб."""
        return len(
            v for v in self.plan.waypoints
            if isinstance(v.place, Job)
        )

    def delay_time(self) -> int:
        """Суммарная задержка."""
        return sum(w.delay for w in self.plan.waypoints)

    def distance(self):
        """

        Returns
        -------

        """