from typing import List
from uuid import uuid4

from models.rich_vrp import Depot
from models.rich_vrp.agent import Agent
from models.rich_vrp.geometries.base import BaseGeometry
from models.rich_vrp.job import Job


class RichVRPProblem:
    """
    Это класс RichVRP задачи — максимально общей постановки транспортной задачи.
    Его функция — описать все, что может встретиться в задаче в однозначной стандартной форме
    для использования во всем остальном коде и обеспечить легкий доступ к параметрам задачи.
    """

    def __init__(
            self,
            matrix: BaseGeometry,
            agents: List[Agent],
            jobs: List[Job],
            depots: List[Depot],
            objectives: List[str],
    ):
        self.uuid = uuid4()  # уникальный id этой конкретной проблемы
        self.matrix = matrix
        self.agents = agents
        self.jobs = jobs
        self.depots = depots
        self.objectives = objectives

    def info(self) -> str:
        return (
            f'id={self.uuid}, '
            f'agents: {len(self.agents)}, '
            f'jobs: {len(self.jobs)}, '
            f'depot: {len(self.depots)}, '
            f'objectives: {self.objectives}'
        )
