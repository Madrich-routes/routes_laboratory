from __future__ import annotations

from typing import List, Optional, Set
from uuid import uuid4

from models.rich_vrp.agent import Agent
from models.rich_vrp.depot import Depot
from models.rich_vrp.job import Job
from models.rich_vrp.place_mapping import PlaceMapping


class RichVRPProblem:
    """Это класс RichVRP задачи — максимально общей постановки транспортной задачи.

    Его функция — описать все, что может встретиться в задаче в однозначной стандартной форме для
    использования во всем остальном коде и обеспечить легкий доступ к параметрам задачи.

    Parameters
    ----------
    place_mapping : Объект, который умеет считать расстояние между точками
    agents : Список агентов, которые могут решать джобы в нашей задаче
    jobs : Список джоб, которые нужно выполнить в этой задаче
    depot : депо в этой задаче
    name : Название этой проблемы
    """

    def __init__(
        self,
        place_mapping: PlaceMapping,
        agents: List[Agent],
        jobs: List[Job],
        depot: Optional[Depot],
        name: Optional[str] = None
    ):
        self.name = name or uuid4()  # уникальный id этой конкретной проблемы
        self.matrix = place_mapping
        self.agents = agents
        self.jobs = jobs
        self.depot = depot

    def info(self) -> str:
        """Базовая статистика проблемы.

        Returns
        -------
        Тескстовое представление статистики
        """
        return (
            f'problem_name: {self.name}, '
            f'agents: {len(self.agents)}, '
            f'jobs: {len(self.jobs)}'
        )

    def profiles(self) -> Set[str]:
        """Получить список всех профайлов в проблеме.

        Returns
        -------
        Set всех профайлов
        """
        return {a.profile for a in self.agents}
