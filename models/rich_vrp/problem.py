from typing import List, Set, Optional
from uuid import uuid4

from models.rich_vrp import Depot
from models.rich_vrp.agent import Agent
from models.rich_vrp.job import Job
from models.rich_vrp.place_mapping import PlaceMapping


class RichVRPProblem:
    """
    Это класс RichVRP задачи — максимально общей постановки транспортной задачи.
    Его функция — описать все, что может встретиться в задаче в однозначной стандартной форме
    для использования во всем остальном коде и обеспечить легкий доступ к параметрам задачи.
    """

    def __init__(
        self,
        place_mapping: PlaceMapping,
        agents: List[Agent],
        jobs: List[Job],
        depots: List[Depot],
        objectives: List[str],
        name: Optional[str] = None
    ):
        self.name = name or uuid4()  # уникальный id этой конкретной проблемы
        self.matrix = place_mapping  # TODO: rename
        self.agents = agents
        self.jobs = jobs
        self.depots = depots
        self.objectives = objectives

    def info(self) -> str:
        """
        Базовая статистика проблемы

        Returns
        -------
        Тескстовое представление статистики
        """
        return (
            f'problem_name: {self.name}, '
            f'agents: {len(self.agents)}, '
            f'jobs: {len(self.jobs)}, '
            f'depot: {len(self.depots)}, '
            f'objectives: {self.objectives}'
        )

    def profiles(self) -> Set[str]:
        """
        Получить список всех профайлов в проблеме

        Returns
        -------
        Set всех профайлов
        """
        return {a.type.profile for a in self.agents}
